"""
Señales de Django para automatizar el cálculo de puntos MVP cuando termina una jornada.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db import models
from django.core.cache import cache
import logging

from partidos.models import Partido
from fantasy.models import (
    PuntosMVPJornada, PuntosMVPTotalJugador,
    PuntosEquipoJornada, PuntosEquipoTotal
)
from nucleo.models import Grupo, Temporada
from jugadores.models import Jugador
from clubes.models import Club
from valoraciones.views import _coef_division_lookup, _coef_club_lookup
from django.db.models import Sum, Max

logger = logging.getLogger(__name__)

# Importar y crear instancia del comando para reutilizar métodos
_command_instance = None
_command_instance_equipo = None

def _actualizar_sumatorio_total(jugador_id: int, temporada_id: int):
    """
    Actualiza el sumatorio total de puntos de un jugador en una temporada.
    Suma todos los puntos de todas las jornadas.
    """
    try:
        # Calcular sumatorio desde PuntosMVPJornada
        totales = (
            PuntosMVPJornada.objects
            .filter(
                jugador_id=jugador_id,
                temporada_id=temporada_id,
            )
            .aggregate(
                puntos_base_total=Sum("puntos_base"),
                puntos_con_coef_total=Sum("puntos_con_coef"),
                goles_total=Sum("goles"),
                partidos_total=Sum("partidos_jugados"),
                max_jornada=Max("jornada"),
            )
        )
        
        # Actualizar o crear registro en PuntosMVPTotalJugador
        PuntosMVPTotalJugador.objects.update_or_create(
            jugador_id=jugador_id,
            temporada_id=temporada_id,
            defaults={
                "puntos_base_total": float(totales["puntos_base_total"] or 0),
                "puntos_con_coef_total": float(totales["puntos_con_coef_total"] or 0),
                "goles_total": int(totales["goles_total"] or 0),
                "partidos_total": int(totales["partidos_total"] or 0),
                "ultima_jornada_procesada": int(totales["max_jornada"] or 0),
            },
        )
    except Exception as e:
        logger.error(
            f"Error al actualizar sumatorio total para jugador={jugador_id}, "
            f"temporada={temporada_id}: {e}",
            exc_info=True,
        )


def _get_command_instance():
    """Obtiene la instancia del comando de cálculo de puntos MVP."""
    global _command_instance
    if _command_instance is None:
        try:
            from fantasy.management.commands.calcular_puntos_mvp_jornada import (
                Command as CalcularPuntosCommand,
            )
            _command_instance = CalcularPuntosCommand()
        except ImportError:
            logger.warning("No se pudo importar el comando de cálculo de puntos MVP")
    return _command_instance


def jornada_completa(grupo_id: int, temporada_id: int, jornada_numero: int) -> bool:
    """
    Verifica si todos los partidos de una jornada específica están jugados.
    
    Args:
        grupo_id: ID del grupo
        temporada_id: ID de la temporada
        jornada_numero: Número de jornada
        
    Returns:
        True si todos los partidos están jugados, False en caso contrario
    """
    partidos_jornada = Partido.objects.filter(
        grupo_id=grupo_id,
        grupo__temporada_id=temporada_id,
        jornada_numero=jornada_numero,
    )
    
    total_partidos = partidos_jornada.count()
    partidos_jugados = partidos_jornada.filter(jugado=True).count()
    
    # Consideramos completa si hay partidos y todos están jugados
    return total_partidos > 0 and total_partidos == partidos_jugados


@receiver(post_save, sender=Partido)
def calcular_puntos_mvp_si_jornada_completa(sender, instance, created, **kwargs):
    """
    Señal que se dispara cuando se guarda un partido.
    Si el partido está marcado como jugado y la jornada está completa,
    calcula automáticamente los puntos MVP para esa jornada.
    """
    # Solo procesar si el partido está jugado
    if not instance.jugado or not instance.grupo:
        return
    
    grupo = instance.grupo
    temporada_id = grupo.temporada_id
    jornada_numero = instance.jornada_numero
    
    # Usar cache para evitar calcular múltiples veces en la misma jornada
    cache_key = f"mvp_jornada_calculando_{grupo.id}_{temporada_id}_{jornada_numero}"
    if cache.get(cache_key):
        logger.debug(
            f"Ya se está calculando MVP para jornada {jornada_numero} del grupo {grupo.id}"
        )
        return
    
    # Verificar si la jornada está completa
    if not jornada_completa(grupo.id, temporada_id, jornada_numero):
        return
    
    # Verificar si ya existen puntos calculados para esta jornada
    if PuntosMVPJornada.objects.filter(
        temporada_id=temporada_id,
        grupo=grupo,
        jornada=jornada_numero,
    ).exists():
        logger.debug(
            f"Ya existen puntos MVP calculados para jornada {jornada_numero} del grupo {grupo.id}"
        )
        return
    
    # Marcar que estamos calculando (evitar procesamiento duplicado)
    cache.set(cache_key, True, timeout=300)  # 5 minutos
    
    try:
        # Calcular puntos MVP para esta jornada en background (usar transaction.on_commit)
        transaction.on_commit(
            lambda: _calcular_puntos_mvp_async(
                temporada_id, grupo.id, jornada_numero
            )
        )
    except Exception as e:
        logger.error(
            f"Error al programar cálculo de puntos MVP para jornada {jornada_numero} "
            f"del grupo {grupo.id}: {e}",
            exc_info=True,
        )
        cache.delete(cache_key)


def _calcular_puntos_mvp_async(temporada_id: int, grupo_id: int, jornada_numero: int):
    """
    Función que se ejecuta después de commit para calcular puntos MVP.
    Esto evita bloquear la transacción principal.
    """
    command_instance = _get_command_instance()
    if not command_instance:
        logger.error("No se puede calcular puntos MVP: comando no disponible")
        return
    
    try:
        logger.info(
            f"Iniciando cálculo automático de puntos MVP para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}"
        )
        
        try:
            temporada = Temporada.objects.get(id=temporada_id)
            grupo = Grupo.objects.get(id=grupo_id)
        except (Temporada.DoesNotExist, Grupo.DoesNotExist) as e:
            logger.error(f"No se encontró temporada o grupo: {e}")
            return
        
        # Obtener coeficientes
        coef_division = _coef_division_lookup(temporada_id, 1)  # Jornada de referencia
        coef_club = _coef_club_lookup(temporada_id, 1)
        
        # Calcular puntos usando el método del comando
        puntos_jugadores = command_instance._calcular_puntos_jugador_jornada(
            grupo, temporada, jornada_numero, coef_division, coef_club
        )
        
        if not puntos_jugadores:
            logger.warning(
                f"No hay puntos para calcular en temporada={temporada_id}, "
                f"grupo={grupo_id}, jornada={jornada_numero}"
            )
            return
        
        # Verificar si ya existen (no forzar)
        if PuntosMVPJornada.objects.filter(
            temporada=temporada,
            grupo=grupo,
            jornada=jornada_numero,
        ).exists():
            logger.debug(
                f"Ya existen puntos para temporada={temporada_id}, "
                f"grupo={grupo_id}, jornada={jornada_numero}"
            )
            return
        
        # Guardar puntos
        coef_div = float(coef_division.get(grupo.competicion_id, 1.0))
        guardados = 0
        
        for jid, datos in puntos_jugadores.items():
            try:
                jugador = Jugador.objects.get(id=jid)
            except Jugador.DoesNotExist:
                continue
            
            puntos_base = float(datos["puntos"])
            puntos_con_coef = puntos_base * coef_div
            
            # Guardar puntos de la jornada
            puntos_jornada_obj, created = PuntosMVPJornada.objects.update_or_create(
                jugador=jugador,
                temporada=temporada,
                grupo=grupo,
                jornada=jornada_numero,
                defaults={
                    "puntos_base": puntos_base,
                    "puntos_con_coef": puntos_con_coef,
                    "coef_division": coef_div,
                    "partidos_jugados": datos["partidos_jugados"],
                    "goles": datos["goles"],
                },
            )
            
            # Actualizar sumatorio total del jugador
            _actualizar_sumatorio_total(jugador.id, temporada.id)
            
            guardados += 1
        
        logger.info(
            f"Cálculo automático completado para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}: {guardados} jugadores guardados"
        )
        
    except Exception as e:
        logger.error(
            f"Error al calcular puntos MVP automáticamente para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}: {e}",
            exc_info=True,
        )
    finally:
        # Limpiar cache
        cache_key = f"mvp_jornada_calculando_{grupo_id}_{temporada_id}_{jornada_numero}"
        cache.delete(cache_key)


# =============================================================================
# SEÑALES PARA PUNTOS DE EQUIPOS
# =============================================================================

def _actualizar_sumatorio_total_equipo(club_id: int, temporada_id: int):
    """
    Actualiza el sumatorio total de puntos fantasy de un equipo en una temporada.
    """
    try:
        club = Club.objects.get(id=club_id)
        temporada = Temporada.objects.get(id=temporada_id)
    except (Club.DoesNotExist, Temporada.DoesNotExist):
        logger.warning(
            f"No se encontró club={club_id} o temporada={temporada_id} para actualizar sumatorio equipo."
        )
        return

    # Sumar todos los puntos de jornada para este equipo en esta temporada
    sum_data = (
        PuntosEquipoJornada.objects.filter(
            club=club, temporada=temporada
        )
        .aggregate(
            total_puntos=Sum("puntos"),
            total_partidos=Sum("partidos_jugados"),
            total_victorias=Sum("victorias"),
            total_empates=Sum("empates"),
            total_derrotas=Sum("derrotas"),
            total_goles_favor=Sum("goles_favor"),
            total_goles_contra=Sum("goles_contra"),
            max_jornada=Max("jornada"),
        )
    )

    PuntosEquipoTotal.objects.update_or_create(
        club=club,
        temporada=temporada,
        defaults={
            "puntos_total": float(sum_data["total_puntos"] or 0),
            "partidos_total": int(sum_data["total_partidos"] or 0),
            "victorias_total": int(sum_data["total_victorias"] or 0),
            "empates_total": int(sum_data["total_empates"] or 0),
            "derrotas_total": int(sum_data["total_derrotas"] or 0),
            "goles_favor_total": int(sum_data["total_goles_favor"] or 0),
            "goles_contra_total": int(sum_data["total_goles_contra"] or 0),
            "ultima_jornada_procesada": int(sum_data["max_jornada"] or 0),
        },
    )
    logger.debug(
        f"Sumatorio total actualizado para equipo {club} en {temporada}: "
        f"{sum_data['total_puntos'] or 0:.2f} pts"
    )


def _get_command_instance_equipo():
    """Obtiene la instancia del comando de cálculo de puntos de equipos."""
    global _command_instance_equipo
    if '_command_instance_equipo' not in globals():
        _command_instance_equipo = None
    if _command_instance_equipo is None:
        try:
            from fantasy.management.commands.calcular_puntos_equipo_jornada import (
                Command as CalcularPuntosEquipoCommand,
            )
            _command_instance_equipo = CalcularPuntosEquipoCommand()
        except ImportError:
            logger.warning("No se pudo importar el comando de cálculo de puntos de equipos")
    return _command_instance_equipo


@receiver(post_save, sender=Partido)
def calcular_puntos_equipo_si_jornada_completa(sender, instance, created, **kwargs):
    """
    Señal que se dispara cuando se guarda un partido.
    Si el partido está marcado como jugado y la jornada está completa,
    calcula automáticamente los puntos fantasy de equipos para esa jornada.
    """
    # Solo procesar si el partido está jugado
    if not instance.jugado or not instance.grupo:
        return
    
    grupo = instance.grupo
    temporada_id = grupo.temporada_id
    jornada_numero = instance.jornada_numero
    
    # Usar cache para evitar calcular múltiples veces en la misma jornada
    cache_key = f"equipo_jornada_calculando_{grupo.id}_{temporada_id}_{jornada_numero}"
    if cache.get(cache_key):
        logger.debug(
            f"Ya se está calculando puntos de equipos para jornada {jornada_numero} del grupo {grupo.id}"
        )
        return
    
    # Verificar si la jornada está completa
    if not jornada_completa(grupo.id, temporada_id, jornada_numero):
        return
    
    # Verificar si ya existen puntos calculados para esta jornada
    if PuntosEquipoJornada.objects.filter(
        temporada_id=temporada_id,
        grupo=grupo,
        jornada=jornada_numero,
    ).exists():
        logger.debug(
            f"Ya existen puntos de equipos calculados para jornada {jornada_numero} del grupo {grupo.id}"
        )
        return
    
    # Marcar que estamos calculando (evitar procesamiento duplicado)
    cache.set(cache_key, True, timeout=300)  # 5 minutos
    
    try:
        # Calcular puntos de equipos para esta jornada en background
        transaction.on_commit(
            lambda: _calcular_puntos_equipo_async(
                temporada_id, grupo.id, jornada_numero
            )
        )
    except Exception as e:
        logger.error(
            f"Error al programar cálculo de puntos de equipos para jornada {jornada_numero} "
            f"del grupo {grupo.id}: {e}",
            exc_info=True,
        )
        cache.delete(cache_key)


def _calcular_puntos_equipo_async(temporada_id: int, grupo_id: int, jornada_numero: int):
    """
    Función que se ejecuta después de commit para calcular puntos de equipos.
    Esto evita bloquear la transacción principal.
    """
    command_instance = _get_command_instance_equipo()
    if not command_instance:
        logger.error("No se puede calcular puntos de equipos: comando no disponible")
        return
    
    try:
        logger.info(
            f"Iniciando cálculo automático de puntos de equipos para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}"
        )
        
        try:
            temporada = Temporada.objects.get(id=temporada_id)
            grupo = Grupo.objects.get(id=grupo_id)
        except (Temporada.DoesNotExist, Grupo.DoesNotExist) as e:
            logger.error(f"No se encontró temporada o grupo: {e}")
            return
        
        # Calcular puntos usando el método del comando
        puntos_equipos = command_instance._calcular_puntos_equipo_jornada(
            grupo, temporada, jornada_numero
        )
        
        if not puntos_equipos:
            logger.warning(
                f"No hay puntos de equipos para calcular en temporada={temporada_id}, "
                f"grupo={grupo_id}, jornada={jornada_numero}"
            )
            return
        
        # Verificar si ya existen (no forzar)
        if PuntosEquipoJornada.objects.filter(
            temporada=temporada,
            grupo=grupo,
            jornada=jornada_numero,
        ).exists():
            logger.debug(
                f"Ya existen puntos de equipos para temporada={temporada_id}, "
                f"grupo={grupo_id}, jornada={jornada_numero}"
            )
            return
        
        # Guardar puntos
        guardados = 0
        
        for club_id, datos in puntos_equipos.items():
            try:
                club = Club.objects.get(id=club_id)
            except Club.DoesNotExist:
                continue
            
            # Guardar puntos de la jornada
            puntos_jornada_obj, created = PuntosEquipoJornada.objects.update_or_create(
                club=club,
                temporada=temporada,
                grupo=grupo,
                jornada=jornada_numero,
                defaults={
                    "puntos": datos["puntos"],
                    "partidos_jugados": datos["partidos_jugados"],
                    "victorias": datos["victorias"],
                    "empates": datos["empates"],
                    "derrotas": datos["derrotas"],
                    "goles_favor": datos["goles_favor"],
                    "goles_contra": datos["goles_contra"],
                },
            )
            
            # Actualizar sumatorio total del equipo
            _actualizar_sumatorio_total_equipo(club.id, temporada.id)
            
            guardados += 1
        
        logger.info(
            f"Cálculo automático de equipos completado para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}: {guardados} equipos guardados"
        )
        
    except Exception as e:
        logger.error(
            f"Error al calcular puntos de equipos automáticamente para temporada={temporada_id}, "
            f"grupo={grupo_id}, jornada={jornada_numero}: {e}",
            exc_info=True,
        )
    finally:
        # Limpiar cache
        cache_key = f"equipo_jornada_calculando_{grupo_id}_{temporada_id}_{jornada_numero}"
        cache.delete(cache_key)

