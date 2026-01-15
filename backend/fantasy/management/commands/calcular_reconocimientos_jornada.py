# fantasy/management/commands/calcular_reconocimientos_jornada.py
"""
Comando para calcular y almacenar reconocimientos de jornada/semana:
- MVP del partido
- MVP de jornada por división
- MVP global de la semana
- Goleador de jornada por división
- Mejor equipo de jornada por división
- Mejor equipo global de la semana

Uso:
    # Calcular reconocimientos de una jornada específica
    python manage.py calcular_reconocimientos_jornada --temporada_id 4 --grupo_id 1 --jornada 5
    
    # Calcular reconocimientos de la última jornada jugada
    python manage.py calcular_reconocimientos_jornada --temporada_id 4
    
    # Modo retrospectivo (desde jornada 1 y semana 1)
    python manage.py calcular_reconocimientos_jornada --temporada_id 4 --retrospectivo
    
    # Forzar recálculo aunque ya existan
    python manage.py calcular_reconocimientos_jornada --temporada_id 4 --jornada 5 --force
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max, Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from nucleo.models import Temporada, Grupo
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador
from clubes.models import ClubEnGrupo
from jugadores.models import Jugador
from valoraciones.views import (
    JugadoresJornadaView, JugadoresJornadaGlobalView,
    EquipoJornadaView, EquipoJornadaGlobalView,
    MVPGlobalView,
    _coef_division_lookup, _coef_club_lookup
)
from estadisticas.views import GoleadoresJornadaView
from fantasy.models import (
    MVPPartido, MVPJornadaDivision, MVPJornadaGlobal,
    GoleadorJornadaDivision, MejorEquipoJornadaDivision, MejorEquipoJornadaGlobal,
    PuntosMVPTotalJugador
)
from math import ceil
from clubes.models import Club


class MockRequest:
    """Request mock para llamar a los endpoints."""
    def __init__(self, params: Dict[str, Any]):
        self.GET = params
        self.META = {}
        self.scheme = "https"
        self.get_host = lambda: "pcfutsal.es"
    
    def build_absolute_uri(self, path: str = ""):
        """Construye una URI absoluta (mock)."""
        if path.startswith("http"):
            return path
        if path.startswith("/"):
            return f"https://pcfutsal.es{path}"
        return f"https://pcfutsal.es/{path}"


def obtener_fecha_martes_semana(fecha: datetime) -> datetime:
    """
    Obtiene la fecha del martes de la semana para una fecha dada.
    Semana: Miércoles 19:00 - Domingo 21:00
    El martes corresponde a la semana siguiente.
    """
    # Si es domingo o lunes, el martes es de esta semana
    # Si es martes a sábado, el martes es de la semana siguiente
    dias_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
    
    if dias_semana == 0:  # Lunes
        return fecha + timedelta(days=1)  # Martes siguiente
    elif dias_semana == 1:  # Martes
        return fecha
    elif dias_semana >= 2:  # Miércoles a Domingo
        # Calcular días hasta el martes siguiente
        dias_hasta_martes = (7 - dias_semana + 1) % 7
        if dias_hasta_martes == 0:
            dias_hasta_martes = 7
        return fecha + timedelta(days=dias_hasta_martes)
    
    return fecha


class Command(BaseCommand):
    help = (
        "Calcula y almacena todos los reconocimientos de jornada/semana:\n"
        "- MVP del partido (con criterios de desempate)\n"
        "- MVP de jornada por división\n"
        "- MVP global de la semana\n"
        "- Goleador de jornada por división\n"
        "- Mejor equipo de jornada por división\n"
        "- Mejor equipo global de la semana"
    )

    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    def add_arguments(self, parser):
        parser.add_argument(
            "--temporada_id",
            type=int,
            default=self.TEMPORADA_ID_BASE,
            help=f"ID de la temporada (por defecto {self.TEMPORADA_ID_BASE}).",
        )
        parser.add_argument(
            "--grupo_id",
            type=int,
            help="ID del grupo específico (opcional). Si no se especifica, procesa todos.",
        )
        parser.add_argument(
            "--jornada",
            type=int,
            help="Número de jornada (opcional). Si no se especifica, usa la última jornada jugada.",
        )
        parser.add_argument(
            "--semana",
            type=str,
            help="Fecha del martes de la semana para cálculos globales (formato YYYY-MM-DD).",
        )
        parser.add_argument(
            "--retrospectivo",
            action="store_true",
            help="Calcular todas las jornadas/semanas desde la jornada 1 y semana 1 de la temporada actual.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forzar recálculo aunque ya existan reconocimientos.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No guarda en BD; solo muestra qué haría.",
        )

    def handle(self, *args, **options):
        temporada_id = options["temporada_id"]
        grupo_id = options.get("grupo_id")
        jornada = options.get("jornada")
        semana = options.get("semana")
        retrospectivo = options.get("retrospectivo", False)
        force = options.get("force", False)
        dry_run = options.get("dry_run", False)

        try:
            temporada = Temporada.objects.get(id=temporada_id)
        except Temporada.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Temporada con ID {temporada_id} no encontrada."))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("=== MODO DRY-RUN: No se guardará nada en BD ==="))

        if retrospectivo:
            self.stdout.write(self.style.SUCCESS("=== MODO RETROSPECTIVO ==="))
            self._calcular_retrospectivo(temporada, force, dry_run)
        else:
            if grupo_id:
                try:
                    grupo = Grupo.objects.get(id=grupo_id, temporada=temporada)
                    self._procesar_grupo_jornada(temporada, grupo, jornada, force, dry_run)
                except Grupo.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Grupo con ID {grupo_id} no encontrado."))
            else:
                # Procesar todos los grupos
                grupos = Grupo.objects.filter(temporada=temporada)
                for grupo in grupos:
                    self._procesar_grupo_jornada(temporada, grupo, jornada, force, dry_run)
                
                # Calcular reconocimientos globales si se especificó semana
                if semana:
                    self._calcular_reconocimientos_globales_semana(temporada, semana, force, dry_run)
                else:
                    # Calcular última semana
                    self._calcular_reconocimientos_globales_ultima_semana(temporada, force, dry_run)

        self.stdout.write(self.style.SUCCESS("✓ Proceso completado."))

    def _calcular_retrospectivo(self, temporada: Temporada, force: bool, dry_run: bool):
        """Calcula todos los reconocimientos desde la jornada 1 y semana 1."""
        self.stdout.write(f"Calculando reconocimientos retrospectivos para temporada {temporada.nombre}...")
        
        # Obtener todos los grupos
        grupos = Grupo.objects.filter(temporada=temporada)
        
        # Identificar todas las jornadas jugadas desde la jornada 1
        jornadas_por_grupo = {}
        for grupo in grupos:
            jornadas = (
                Partido.objects
                .filter(grupo=grupo, jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
                .order_by("jornada_numero")
            )
            jornadas_por_grupo[grupo.id] = sorted(set(jornadas))
        
        # Procesar cada jornada de cada grupo
        for grupo in grupos:
            jornadas = jornadas_por_grupo.get(grupo.id, [])
            for jornada_num in jornadas:
                self.stdout.write(f"  Procesando {grupo.nombre} - Jornada {jornada_num}...")
                self._procesar_grupo_jornada(temporada, grupo, jornada_num, force, dry_run)
        
        # Identificar todas las semanas con partidos desde la semana 1
        self.stdout.write("  Calculando reconocimientos globales por semana...")
        
        # Obtener todas las fechas de martes de semanas con partidos
        partidos = (
            Partido.objects
            .filter(grupo__temporada=temporada, jugado=True)
            .order_by("fecha_hora")
            .values_list("fecha_hora", flat=True)
        )
        
        semanas_martes = set()
        for fecha_partido in partidos:
            fecha = fecha_partido.astimezone(timezone.get_current_timezone()).date()
            # Encontrar el martes de esa semana
            dias_desde_lunes = fecha.weekday()
            lunes = fecha - timedelta(days=dias_desde_lunes)
            martes = lunes + timedelta(days=1)
            semanas_martes.add(martes.strftime("%Y-%m-%d"))
        
        # Ordenar semanas cronológicamente
        semanas_ordenadas = sorted(semanas_martes)
        
        # Calcular reconocimientos globales para cada semana
        for semana_martes in semanas_ordenadas:
            self.stdout.write(f"  Procesando semana {semana_martes}...")
            self._calcular_reconocimientos_globales_semana(temporada, semana_martes, force, dry_run)

    def _procesar_grupo_jornada(
        self,
        temporada: Temporada,
        grupo: Grupo,
        jornada: Optional[int],
        force: bool,
        dry_run: bool
    ):
        """Procesa reconocimientos de una jornada específica de un grupo."""
        # Determinar jornada a procesar
        if jornada is None:
            # Usar última jornada jugada
            ultima_jornada = (
                Partido.objects
                .filter(grupo=grupo, jugado=True)
                .aggregate(max_jornada=Max("jornada_numero"))
            )
            jornada = ultima_jornada.get("max_jornada")
            if jornada is None:
                self.stdout.write(self.style.WARNING(f"  No hay jornadas jugadas en {grupo.nombre}."))
                return
        
        self.stdout.write(f"  Procesando {grupo.nombre} - Jornada {jornada}...")
        
        # 1. Calcular MVP del partido para cada partido de la jornada
        self._calcular_mvp_partidos(temporada, grupo, jornada, force, dry_run)
        
        # 2. Calcular MVP de jornada por división
        self._calcular_mvp_jornada_division(temporada, grupo, jornada, force, dry_run)
        
        # 3. Calcular goleador de jornada por división
        self._calcular_goleador_jornada_division(temporada, grupo, jornada, force, dry_run)
        
        # 4. Calcular mejor equipo de jornada por división
        self._calcular_mejor_equipo_jornada_division(temporada, grupo, jornada, force, dry_run)

    def _calcular_mvp_partidos(
        self,
        temporada: Temporada,
        grupo: Grupo,
        jornada: int,
        force: bool,
        dry_run: bool
    ):
        """Calcula el MVP de cada partido de la jornada."""
        partidos = (
            Partido.objects
            .filter(grupo=grupo, jornada_numero=jornada, jugado=True)
            .select_related("local", "visitante")
            .prefetch_related("eventos", "alineaciones_jugadores")
        )
        
        for partido in partidos:
            # Verificar si ya existe MVP del partido
            if not force and MVPPartido.objects.filter(partido=partido).exists():
                continue
            
            # Calcular MVP del partido con criterios de desempate
            mvp_data = self._calcular_mvp_partido(partido, temporada)
            
            if mvp_data:
                if not dry_run:
                    MVPPartido.objects.update_or_create(
                        partido=partido,
                        defaults=mvp_data
                    )
                self.stdout.write(f"    ✓ MVP Partido {partido}: {mvp_data['jugador']} ({mvp_data['puntos']} pts)")

    def _calcular_puntos_jugador_partido(
        self,
        partido: Partido,
        jugador_id: int,
        coef_club: dict
    ) -> Dict[str, Any]:
        """
        Calcula los puntos de un jugador específico en un partido.
        Retorna un dict con puntos, goles, tarjetas, etc.
        """
        mvp_view = MVPGlobalView()
        
        alineaciones = list(partido.alineaciones_jugadores.all())
        eventos = list(partido.eventos.all())
        al_por_j = {al.jugador_id: al for al in alineaciones if al.jugador_id}
        
        al_jugador = al_por_j.get(jugador_id)
        if not al_jugador or not al_jugador.jugador:
            return {
                "puntos": 0.0,
                "goles": 0,
                "tarjetas_amarillas": 0,
                "tarjetas_rojas": 0,
                "mvp_evento": False,
                "equipo_ganador": False,
                "club_id": None,
            }
        
        jugador = al_jugador.jugador
        club_id_jugador = al_jugador.club_id
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        
        puntos = 0.0
        goles = 0
        tarjetas_amarillas = 0
        tarjetas_rojas = 0
        mvp_evento = False
        
        # 1. Presencia
        puntos += mvp_view._puntos_presencia(al_jugador.titular)
        
        # 2. Bonus resultado
        puntos += mvp_view._bonus_resultado(partido, club_id_jugador, gl, gv)
        
        # 3. Bonus rival fuerte
        puntos += mvp_view._bonus_rival_fuerte(partido, club_id_jugador, coef_club)
        
        # 4. Bonus duelo fuertes
        puntos += mvp_view._bonus_duelo_fuertes(partido, coef_club)
        
        # 5. Bonus intensidad
        puntos += mvp_view._bonus_intensidad(partido)
        
        # 6. Eventos
        eventos_jugador = [e for e in eventos if e.jugador_id == jugador_id]
        for ev in eventos_jugador:
            if ev.tipo_evento == "gol":
                puntos += 3.0
                goles += 1
            elif ev.tipo_evento == "gol_pp":
                puntos -= 2.0
            elif ev.tipo_evento == "amarilla":
                puntos -= 1.0
                tarjetas_amarillas += 1
            elif ev.tipo_evento == "doble_amarilla":
                puntos -= 3.0
                tarjetas_amarillas += 2
            elif ev.tipo_evento == "roja":
                puntos -= 5.0
                tarjetas_rojas += 1
            elif ev.tipo_evento == "mvp":
                puntos += 3.0
                mvp_evento = True
        
        # 7. Porteros: goles encajados
        es_portero = mvp_view._es_portero(jugador, al_jugador)
        if es_portero:
            goles_recibidos = gv if partido.local_id == club_id_jugador else gl
            puntos += mvp_view._penal_goles_encajados(goles_recibidos)
            
            # Portería seria
            if partido.local_id == club_id_jugador:
                if gl > gv and gv <= 1:
                    puntos += 1.0
            else:
                if gv > gl and gl <= 1:
                    puntos += 1.0
            
            # Extra portero goleador
            if goles > 0:
                puntos += mvp_view._extra_portero_gol(goles)
        
        # Determinar si su equipo ganó
        equipo_ganador = False
        if partido.jugado:
            if partido.local_id == club_id_jugador:
                equipo_ganador = gl > gv
            else:
                equipo_ganador = gv > gl
        
        return {
            "puntos": ceil(puntos),
            "goles": goles,
            "tarjetas_amarillas": tarjetas_amarillas,
            "tarjetas_rojas": tarjetas_rojas,
            "mvp_evento": mvp_evento,
            "equipo_ganador": equipo_ganador,
            "club_id": club_id_jugador,
        }

    def _calcular_mvp_partido(self, partido: Partido, temporada: Temporada) -> Optional[Dict[str, Any]]:
        """
        Calcula el MVP de un partido con criterios de desempate.
        
        Criterios de desempate (en caso de empate a puntos):
        1. Jugador del equipo que ganó el partido
        2. Jugador que marcó más goles
        3. Jugador que recibió menos tarjetas
        4. Jugador con más puntos MVP acumulados en la temporada
        """
        if not partido.jugado:
            return None
        
        # Obtener coeficientes
        coef_club = _coef_club_lookup(temporada.id, self.JORNADA_REF_COEF)
        
        # Obtener todos los jugadores que participaron en el partido
        alineaciones = list(partido.alineaciones_jugadores.all())
        jugadores_participantes = [al.jugador_id for al in alineaciones if al.jugador_id]
        
        if not jugadores_participantes:
            return None
        
        # Calcular puntos de cada jugador
        jugadores_puntos = []
        for jugador_id in jugadores_participantes:
            datos = self._calcular_puntos_jugador_partido(partido, jugador_id, coef_club)
            datos["jugador_id"] = jugador_id
            jugadores_puntos.append(datos)
        
        if not jugadores_puntos:
            return None
        
        # Ordenar por puntos (mayor a menor)
        jugadores_puntos.sort(key=lambda x: x["puntos"], reverse=True)
        
        # Buscar el máximo de puntos
        max_puntos = jugadores_puntos[0]["puntos"]
        
        # Filtrar jugadores con máximo de puntos (empate)
        candidatos = [j for j in jugadores_puntos if j["puntos"] == max_puntos]
        
        if len(candidatos) == 1:
            # No hay empate, este es el MVP
            mvp_data = candidatos[0]
        else:
            # Hay empate, aplicar criterios de desempate
            mvp_data = self._aplicar_criterios_desempate(candidatos, partido, temporada)
        
        if not mvp_data:
            return None
        
        # Obtener jugador
        try:
            jugador = Jugador.objects.get(id=mvp_data["jugador_id"])
        except Jugador.DoesNotExist:
            return None
        
        # Obtener puntos MVP acumulados en la temporada
        puntos_acumulados = 0.0
        try:
            total = PuntosMVPTotalJugador.objects.get(jugador=jugador, temporada=temporada)
            puntos_acumulados = total.puntos_con_coef_total or 0.0
        except PuntosMVPTotalJugador.DoesNotExist:
            pass
        
        return {
            "jugador": jugador,
            "puntos": float(mvp_data["puntos"]),
            "goles": mvp_data["goles"],
            "tarjetas_amarillas": mvp_data["tarjetas_amarillas"],
            "tarjetas_rojas": mvp_data["tarjetas_rojas"],
            "mvp_evento": mvp_data["mvp_evento"],
            "equipo_ganador": mvp_data["equipo_ganador"],
            "puntos_mvp_acumulados": puntos_acumulados,
        }

    def _aplicar_criterios_desempate(
        self,
        candidatos: List[Dict[str, Any]],
        partido: Partido,
        temporada: Temporada
    ) -> Optional[Dict[str, Any]]:
        """
        Aplica criterios de desempate en orden:
        1. Jugador del equipo que ganó el partido
        2. Jugador que marcó más goles
        3. Jugador que recibió menos tarjetas
        4. Jugador con más puntos MVP acumulados en la temporada
        """
        if not candidatos:
            return None
        
        if len(candidatos) == 1:
            return candidatos[0]
        
        # Criterio 1: Jugador del equipo que ganó el partido
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        equipo_ganador_id = None
        if gl > gv:
            equipo_ganador_id = partido.local_id
        elif gv > gl:
            equipo_ganador_id = partido.visitante_id
        
        if equipo_ganador_id:
            ganadores = [c for c in candidatos if c.get("club_id") == equipo_ganador_id]
            if ganadores:
                candidatos = ganadores
                if len(candidatos) == 1:
                    return candidatos[0]
        
        # Criterio 2: Jugador que marcó más goles
        max_goles = max(c["goles"] for c in candidatos)
        max_goleadores = [c for c in candidatos if c["goles"] == max_goles]
        if len(max_goleadores) < len(candidatos):
            candidatos = max_goleadores
            if len(candidatos) == 1:
                return candidatos[0]
        
        # Criterio 3: Jugador que recibió menos tarjetas (amarillas + rojas)
        total_tarjetas = [
            (c, c["tarjetas_amarillas"] + c["tarjetas_rojas"])
            for c in candidatos
        ]
        min_tarjetas = min(t for _, t in total_tarjetas)
        menos_tarjetas = [c for c, t in total_tarjetas if t == min_tarjetas]
        if len(menos_tarjetas) < len(candidatos):
            candidatos = menos_tarjetas
            if len(candidatos) == 1:
                return candidatos[0]
        
        # Criterio 4: Jugador con más puntos MVP acumulados en la temporada
        puntos_acumulados = []
        for candidato in candidatos:
            try:
                jugador = Jugador.objects.get(id=candidato["jugador_id"])
                total = PuntosMVPTotalJugador.objects.get(jugador=jugador, temporada=temporada)
                puntos_acumulados.append((candidato, total.puntos_con_coef_total or 0.0))
            except (Jugador.DoesNotExist, PuntosMVPTotalJugador.DoesNotExist):
                puntos_acumulados.append((candidato, 0.0))
        
        if puntos_acumulados:
            max_puntos_acum = max(p for _, p in puntos_acumulados)
            mejor_acum = [c for c, p in puntos_acumulados if p == max_puntos_acum]
            if len(mejor_acum) == 1:
                return mejor_acum[0]
        
        # Si aún hay empate después de todos los criterios, devolver el primero
        return candidatos[0]

    def _calcular_mvp_jornada_division(
        self,
        temporada: Temporada,
        grupo: Grupo,
        jornada: int,
        force: bool,
        dry_run: bool
    ):
        """Calcula el MVP de la jornada por división usando JugadoresJornadaView."""
        # Verificar si ya existe
        if not force and MVPJornadaDivision.objects.filter(
            temporada=temporada,
            grupo=grupo,
            jornada=jornada
        ).exists():
            return
        
        # Crear request mock
        request = MockRequest({"grupo_id": str(grupo.id), "jornada": str(jornada)})
        view = JugadoresJornadaView()
        response = view.get(request)
        
        if response.status_code != 200:
            self.stdout.write(self.style.WARNING(
                f"  Error al calcular MVP jornada división: {response.data}"
            ))
            return
        
        data = response.data
        jugador_mvp_data = data.get("jugador_de_la_jornada")
        
        if not jugador_mvp_data:
            return
        
        jugador_id = jugador_mvp_data.get("jugador_id")
        if not jugador_id:
            return
        
        try:
            jugador = Jugador.objects.get(id=jugador_id)
        except Jugador.DoesNotExist:
            return
        
        # Obtener coeficiente de división
        coef_division = _coef_division_lookup(temporada.id, self.JORNADA_REF_COEF)
        coef_div = float(coef_division.get(grupo.competicion_id, 1.0))
        
        puntos_base = float(jugador_mvp_data.get("puntos", 0))
        puntos_con_coef = puntos_base * coef_div
        
        # Obtener partidos jugados y goles
        partidos_jornada = Partido.objects.filter(
            grupo=grupo,
            jornada_numero=jornada,
            jugado=True
        )
        
        partidos_jugados = 0
        goles = 0
        
        for partido in partidos_jornada:
            # Verificar si el jugador participó en este partido
            alineaciones = partido.alineaciones_jugadores.filter(jugador_id=jugador_id)
            if alineaciones.exists():
                partidos_jugados += 1
                
                # Contar goles en este partido
                eventos_gol = partido.eventos.filter(
                    jugador_id=jugador_id,
                    tipo_evento="gol"
                )
                goles += eventos_gol.count()
        
        if not dry_run:
            MVPJornadaDivision.objects.update_or_create(
                temporada=temporada,
                grupo=grupo,
                jornada=jornada,
                defaults={
                    "jugador": jugador,
                    "puntos": puntos_base,
                    "puntos_con_coef": puntos_con_coef,
                    "coef_division": coef_div,
                    "partidos_jugados": partidos_jugados,
                    "goles": goles,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"    ✓ MVP Jornada {grupo.nombre} J{jornada}: {jugador} ({puntos_con_coef:.2f} pts)"
        ))

    def _calcular_goleador_jornada_division(
        self,
        temporada: Temporada,
        grupo: Grupo,
        jornada: int,
        force: bool,
        dry_run: bool
    ):
        """Calcula el goleador de la jornada por división usando GoleadoresJornadaView."""
        # Verificar si ya existe
        if not force and GoleadorJornadaDivision.objects.filter(
            temporada=temporada,
            grupo=grupo,
            jornada=jornada
        ).exists():
            return
        
        # Crear request mock
        request = MockRequest({"grupo_id": str(grupo.id), "jornada": str(jornada)})
        view = GoleadoresJornadaView()
        response = view.get(request)
        
        if response.status_code != 200:
            self.stdout.write(self.style.WARNING(
                f"  Error al calcular goleador jornada división: {response.data}"
            ))
            return
        
        data = response.data
        goleadores = data.get("goleadores", [])
        
        if not goleadores:
            return
        
        # El primer goleador es el que más goles marcó
        goleador_mvp = goleadores[0]
        jugador_id = goleador_mvp.get("jugador_id")
        
        if not jugador_id:
            return
        
        try:
            jugador = Jugador.objects.get(id=jugador_id)
        except Jugador.DoesNotExist:
            return
        
        goles = goleador_mvp.get("goles_jornada", 0)
        
        # Contar partidos jugados en la jornada
        partidos_jornada = Partido.objects.filter(
            grupo=grupo,
            jornada_numero=jornada,
            jugado=True
        )
        partidos_jugados = 0
        for partido in partidos_jornada:
            alineaciones = partido.alineaciones_jugadores.filter(jugador_id=jugador_id)
            if alineaciones.exists():
                partidos_jugados += 1
        
        if not dry_run:
            GoleadorJornadaDivision.objects.update_or_create(
                temporada=temporada,
                grupo=grupo,
                jornada=jornada,
                defaults={
                    "jugador": jugador,
                    "goles": goles,
                    "partidos_jugados": partidos_jugados,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"    ✓ Goleador {grupo.nombre} J{jornada}: {jugador} ({goles} goles)"
        ))

    def _calcular_mejor_equipo_jornada_division(
        self,
        temporada: Temporada,
        grupo: Grupo,
        jornada: int,
        force: bool,
        dry_run: bool
    ):
        """Calcula el mejor equipo de la jornada por división usando EquipoJornadaView."""
        # Verificar si ya existe
        if not force and MejorEquipoJornadaDivision.objects.filter(
            temporada=temporada,
            grupo=grupo,
            jornada=jornada
        ).exists():
            return
        
        # Crear request mock
        request = MockRequest({"grupo_id": str(grupo.id), "jornada": str(jornada)})
        view = EquipoJornadaView()
        response = view.get(request)
        
        if response.status_code != 200:
            self.stdout.write(self.style.WARNING(
                f"  Error al calcular mejor equipo jornada división: {response.data}"
            ))
            return
        
        data = response.data
        equipo_mvp_data = data.get("equipo_de_la_jornada")
        
        if not equipo_mvp_data:
            return
        
        club_id = equipo_mvp_data.get("club_id")
        if not club_id:
            return
        
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return
        
        puntos = float(equipo_mvp_data.get("puntos", 0))
        
        # Obtener estadísticas del equipo
        partidos_jornada = Partido.objects.filter(
            grupo=grupo,
            jornada_numero=jornada,
            jugado=True
        ).filter(
            Q(local_id=club_id) | Q(visitante_id=club_id)
        )
        
        partidos_jugados = partidos_jornada.count()
        victorias = 0
        empates = 0
        derrotas = 0
        goles_favor = 0
        goles_contra = 0
        
        for partido in partidos_jornada:
            gl = partido.goles_local or 0
            gv = partido.goles_visitante or 0
            
            if partido.local_id == club_id:
                goles_favor += gl
                goles_contra += gv
                if gl > gv:
                    victorias += 1
                elif gl == gv:
                    empates += 1
                else:
                    derrotas += 1
            else:
                goles_favor += gv
                goles_contra += gl
                if gv > gl:
                    victorias += 1
                elif gv == gl:
                    empates += 1
                else:
                    derrotas += 1
        
        if not dry_run:
            MejorEquipoJornadaDivision.objects.update_or_create(
                temporada=temporada,
                grupo=grupo,
                jornada=jornada,
                defaults={
                    "club": club,
                    "puntos": puntos,
                    "partidos_jugados": partidos_jugados,
                    "victorias": victorias,
                    "empates": empates,
                    "derrotas": derrotas,
                    "goles_favor": goles_favor,
                    "goles_contra": goles_contra,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"    ✓ Mejor Equipo {grupo.nombre} J{jornada}: {club} ({puntos:.2f} pts)"
        ))

    def _fecha_martes_semana_a_ventana(self, fecha_martes_str: str):
        """
        Convierte una fecha de martes (YYYY-MM-DD) a la ventana de semana (Mi 19:00 - Do 21:00).
        Retorna (start_datetime, end_datetime) en timezone aware.
        """
        from datetime import datetime, time
        fecha_martes = datetime.strptime(fecha_martes_str, "%Y-%m-%d").date()
        # El martes es day 1 (0=Lunes, 1=Martes...)
        dias_hasta_miercoles = 1  # Martes -> Miércoles
        dias_hasta_domingo = 5     # Martes -> Domingo
        
        miercoles = fecha_martes + timedelta(days=dias_hasta_miercoles)
        domingo = fecha_martes + timedelta(days=dias_hasta_domingo)
        
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(miercoles, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(domingo, time(21, 0, 0)), tz)
        return start, end

    def _detectar_ultima_semana_con_partidos(self, temporada: Temporada):
        """Detecta la última semana con partidos jugados y retorna la fecha del martes."""
        ultimo_partido = (
            Partido.objects
            .filter(grupo__temporada=temporada, jugado=True)
            .order_by("-fecha_hora")
            .first()
        )
        if not ultimo_partido:
            return None
        
        fecha_partido = ultimo_partido.fecha_hora.astimezone(timezone.get_current_timezone()).date()
        # Encontrar el martes de esa semana
        # weekday(): 0=Lunes, 1=Martes, ..., 6=Domingo
        dias_desde_lunes = fecha_partido.weekday()
        lunes = fecha_partido - timedelta(days=dias_desde_lunes)
        martes = lunes + timedelta(days=1)
        return martes.strftime("%Y-%m-%d")

    def _calcular_reconocimientos_globales_semana(
        self,
        temporada: Temporada,
        semana: str,
        force: bool,
        dry_run: bool
    ):
        """
        Calcula reconocimientos globales para una semana específica.
        semana: fecha del martes de la semana (formato YYYY-MM-DD)
        """
        try:
            fecha_martes = datetime.strptime(semana, "%Y-%m-%d").date()
        except ValueError:
            self.stdout.write(self.style.ERROR(f"  Formato de fecha inválido: {semana}. Debe ser YYYY-MM-DD"))
            return
        
        # Verificar si ya existe MVP global
        if not force and MVPJornadaGlobal.objects.filter(
            temporada=temporada,
            semana=fecha_martes
        ).exists():
            return
        
        # Calcular ventana de semana
        start_dt, end_dt = self._fecha_martes_semana_a_ventana(semana)
        
        # Calcular MVP global usando JugadoresJornadaGlobalView
        request = MockRequest({
            "temporada_id": str(temporada.id),
            "weekend": semana,
            "strict": "1"
        })
        view = JugadoresJornadaGlobalView()
        response = view.get(request)
        
        if response.status_code != 200:
            self.stdout.write(self.style.WARNING(
                f"  Error al calcular MVP global semana {semana}: {response.data}"
            ))
            return
        
        data = response.data
        jugador_mvp_data = data.get("jugador_de_la_jornada_global")
        
        if not jugador_mvp_data:
            return
        
        jugador_id = jugador_mvp_data.get("jugador_id")
        if not jugador_id:
            return
        
        try:
            jugador = Jugador.objects.get(id=jugador_id)
            # Obtener grupo del jugador (asumimos que viene en los datos o lo obtenemos del primer partido)
            grupo_id = jugador_mvp_data.get("grupo_id")
            if not grupo_id:
                # Intentar obtenerlo de algún partido de la semana
                partidos_semana = Partido.objects.filter(
                    grupo__temporada=temporada,
                    jugado=True,
                    fecha_hora__gte=start_dt,
                    fecha_hora__lte=end_dt,
                    alineaciones_jugadores__jugador_id=jugador_id
                ).first()
                if partidos_semana:
                    grupo = partidos_semana.grupo
                else:
                    return
            else:
                grupo = Grupo.objects.get(id=grupo_id, temporada=temporada)
        except (Jugador.DoesNotExist, Grupo.DoesNotExist):
            return
        
        puntos = float(jugador_mvp_data.get("puntos_semana", 0))
        puntos_base = float(jugador_mvp_data.get("puntos", 0))
        
        # Obtener coeficiente de división
        coef_division = _coef_division_lookup(temporada.id, self.JORNADA_REF_COEF)
        coef_div = float(coef_division.get(grupo.competicion_id, 1.0))
        
        # Contar partidos jugados y goles en la semana
        partidos_semana = Partido.objects.filter(
            grupo__temporada=temporada,
            jugado=True,
            fecha_hora__gte=start_dt,
            fecha_hora__lte=end_dt,
            alineaciones_jugadores__jugador_id=jugador_id
        ).distinct()
        
        partidos_jugados = partidos_semana.count()
        eventos_gol = EventoPartido.objects.filter(
            partido__in=partidos_semana,
            jugador_id=jugador_id,
            tipo_evento="gol"
        )
        goles = eventos_gol.count()
        
        if not dry_run:
            MVPJornadaGlobal.objects.update_or_create(
                temporada=temporada,
                semana=fecha_martes,
                defaults={
                    "jugador": jugador,
                    "grupo": grupo,
                    "puntos": puntos,
                    "puntos_base": puntos_base,
                    "coef_division": coef_div,
                    "partidos_jugados": partidos_jugados,
                    "goles": goles,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"    ✓ MVP Global Semana {semana}: {jugador} ({puntos:.2f} pts)"
        ))
        
        # Calcular mejor equipo global
        request_equipo = MockRequest({
            "temporada_id": str(temporada.id),
            "weekend": semana,
            "strict": "1"
        })
        view_equipo = EquipoJornadaGlobalView()
        response_equipo = view_equipo.get(request_equipo)
        
        if response_equipo.status_code == 200:
            data_equipo = response_equipo.data
            equipo_mvp_data = data_equipo.get("equipo_de_la_jornada_global")
            
            if equipo_mvp_data:
                club_id = equipo_mvp_data.get("club_id")
                if club_id:
                    try:
                        club = Club.objects.get(id=club_id)
                        grupo_equipo_id = equipo_mvp_data.get("grupo_id")
                        if grupo_equipo_id:
                            grupo_equipo = Grupo.objects.get(id=grupo_equipo_id, temporada=temporada)
                        else:
                            grupo_equipo = grupo  # Usar el mismo grupo por defecto
                        
                        puntos_equipo = float(equipo_mvp_data.get("puntos_semana", 0))
                        puntos_base_equipo = float(equipo_mvp_data.get("puntos", 0))
                        coef_div_equipo = float(coef_division.get(grupo_equipo.competicion_id, 1.0))
                        
                        # Estadísticas del equipo en la semana
                        partidos_equipo = Partido.objects.filter(
                            grupo__temporada=temporada,
                            jugado=True,
                            fecha_hora__gte=start_dt,
                            fecha_hora__lte=end_dt
                        ).filter(
                            Q(local_id=club_id) | Q(visitante_id=club_id)
                        )
                        
                        partidos_jugados_equipo = partidos_equipo.count()
                        victorias = empates = derrotas = 0
                        goles_favor = goles_contra = 0
                        
                        for p in partidos_equipo:
                            gl = p.goles_local or 0
                            gv = p.goles_visitante or 0
                            if p.local_id == club_id:
                                goles_favor += gl
                                goles_contra += gv
                                if gl > gv: victorias += 1
                                elif gl == gv: empates += 1
                                else: derrotas += 1
                            else:
                                goles_favor += gv
                                goles_contra += gl
                                if gv > gl: victorias += 1
                                elif gv == gl: empates += 1
                                else: derrotas += 1
                        
                        if not dry_run:
                            MejorEquipoJornadaGlobal.objects.update_or_create(
                                temporada=temporada,
                                semana=fecha_martes,
                                defaults={
                                    "club": club,
                                    "grupo": grupo_equipo,
                                    "puntos": puntos_equipo,
                                    "puntos_base": puntos_base_equipo,
                                    "coef_division": coef_div_equipo,
                                    "partidos_jugados": partidos_jugados_equipo,
                                    "victorias": victorias,
                                    "empates": empates,
                                    "derrotas": derrotas,
                                    "goles_favor": goles_favor,
                                    "goles_contra": goles_contra,
                                }
                            )
                        
                        self.stdout.write(self.style.SUCCESS(
                            f"    ✓ Mejor Equipo Global Semana {semana}: {club} ({puntos_equipo:.2f} pts)"
                        ))
                    except (Club.DoesNotExist, Grupo.DoesNotExist):
                        pass

    def _calcular_reconocimientos_globales_ultima_semana(
        self,
        temporada: Temporada,
        force: bool,
        dry_run: bool
    ):
        """Calcula reconocimientos globales para la última semana con partidos."""
        semana_martes = self._detectar_ultima_semana_con_partidos(temporada)
        if not semana_martes:
            self.stdout.write(self.style.WARNING(
                f"  No se encontró ninguna semana con partidos jugados."
            ))
            return
        
        self.stdout.write(f"  Calculando reconocimientos globales para semana {semana_martes}...")
        self._calcular_reconocimientos_globales_semana(temporada, semana_martes, force, dry_run)

