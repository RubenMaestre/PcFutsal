# fantasy/management/commands/calcular_puntos_mvp_jornada.py
"""
Comando para calcular y almacenar puntos MVP por jornada.

Uso:
    python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --jornada 1
    python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --jornada 1 --grupo 5
    python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --todas-jornadas
    python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --jornada 1 --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from math import ceil

from nucleo.models import Temporada, Grupo
from partidos.models import Partido, AlineacionPartidoJugador
from clubes.models import ClubEnGrupo
from jugadores.models import Jugador
from valoraciones.views import MVPGlobalView, _coef_division_lookup, _coef_club_lookup
from fantasy.models import PuntosMVPJornada, PuntosMVPTotalJugador
from django.db.models import Sum, Max
from fantasy.signals import _actualizar_sumatorio_total


def _norm_media(url: str) -> str:
    """Normaliza URL de media."""
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return url


class Command(BaseCommand):
    help = (
        "Calcula y almacena puntos MVP por jornada para optimizar el ranking MVP global.\n"
        "Reutiliza la lógica de cálculo de MVPGlobalView pero almacena los resultados."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--temporada",
            type=str,
            required=True,
            help='Nombre de la temporada (ej. "2025/2026").',
        )
        parser.add_argument(
            "--jornada",
            type=int,
            help="Número de jornada a calcular. Si no se especifica, se calculan todas.",
        )
        parser.add_argument(
            "--grupo",
            type=int,
            help="ID del grupo específico (opcional). Si no se especifica, se procesan todos.",
        )
        parser.add_argument(
            "--todas-jornadas",
            action="store_true",
            help="Calcula todas las jornadas de la temporada.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No guarda en BD; solo muestra qué haría.",
        )
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Recalcula incluso si ya existen puntos para esa jornada.",
        )

    def _calcular_puntos_jugador_jornada(
        self,
        grupo: Grupo,
        temporada: Temporada,
        jornada: int,
        coef_division: dict,
        coef_club: dict,
    ) -> dict[int, dict]:
        """
        Calcula puntos MVP para todos los jugadores de un grupo en una jornada específica.
        
        Retorna: dict[jugador_id, {puntos, goles, partidos_jugados, ...}]
        """
        # Obtener todos los partidos de esa jornada en ese grupo
        partidos = (
            Partido.objects
            .filter(
                grupo=grupo,
                jornada_numero=jornada,
                jugado=True,
            )
            .select_related("local", "visitante")
            .prefetch_related("eventos", "alineaciones_jugadores")
            .order_by("fecha_hora", "id")
        )
        
        partidos_list = list(partidos)
        if not partidos_list:
            return {}
        
        # Info de clubes
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        club_info = {
            c.club_id: {
                "escudo": _norm_media(c.club.escudo_url or ""),
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }
            for c in clasif_rows
        }
        
        # Instancia de MVPGlobalView para usar sus métodos de cálculo
        mvp_view = MVPGlobalView()
        
        ranking_jornada: dict[int, dict] = {}
        
        for p in partidos_list:
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            bonus_df = mvp_view._bonus_duelo_fuertes(p, coef_club)
            bonus_int = mvp_view._bonus_intensidad(p)
            
            alineaciones = list(p.alineaciones_jugadores.all())
            al_por_j = {al.jugador_id: al for al in alineaciones if al.jugador_id}
            eventos = list(p.eventos.all())
            
            # 1) Presencia + contexto
            for al in alineaciones:
                jug = al.jugador
                if not jug:
                    continue
                jid = jug.id
                cid = al.club_id
                es_gk = mvp_view._es_portero(jug, al)
                
                if jid not in ranking_jornada:
                    info = club_info.get(cid or 0, {})
                    ranking_jornada[jid] = {
                        "jugador_id": jid,
                        "puntos": 0.0,
                        "es_portero": es_gk,
                        "goles": 0,
                        "partidos_jugados": 0,
                    }
                else:
                    if es_gk:
                        ranking_jornada[jid]["es_portero"] = True
                
                ranking_jornada[jid]["puntos"] += mvp_view._puntos_presencia(al.titular)
                ranking_jornada[jid]["partidos_jugados"] += 1
                
                pr = mvp_view._bonus_resultado(p, cid, gl, gv)
                if pr:
                    ranking_jornada[jid]["puntos"] += pr
                
                brf = mvp_view._bonus_rival_fuerte(p, cid, coef_club)
                if brf:
                    ranking_jornada[jid]["puntos"] += brf
                
                if bonus_df:
                    ranking_jornada[jid]["puntos"] += bonus_df
                if bonus_int:
                    ranking_jornada[jid]["puntos"] += bonus_int
            
            # 2) Eventos (incluye conteo de goles)
            for ev in eventos:
                if not ev.jugador_id:
                    continue
                jid = ev.jugador_id
                jug = ev.jugador
                al_ev = al_por_j.get(jid)
                es_gk = mvp_view._es_portero(jug, al_ev)
                
                if jid not in ranking_jornada:
                    cid = ev.club_id
                    info = club_info.get(cid or 0, {})
                    ranking_jornada[jid] = {
                        "jugador_id": jid,
                        "puntos": 0.0,
                        "es_portero": es_gk,
                        "goles": 0,
                        "partidos_jugados": 0,
                    }
                else:
                    if es_gk:
                        ranking_jornada[jid]["es_portero"] = True
                
                pts_ev = mvp_view._puntos_evento(ev.tipo_evento)
                if pts_ev:
                    ranking_jornada[jid]["puntos"] += pts_ev
                
                if ev.tipo_evento == "gol":
                    ranking_jornada[jid]["goles"] = (
                        ranking_jornada[jid].get("goles", 0) + 1
                    )
            
            # 3) Porteros: goles encajados + "portería seria"
            g_rec_local, g_rec_visit = gv, gl
            ports_local = [
                al for al in alineaciones
                if al.club_id == p.local_id and mvp_view._es_portero(al.jugador, al)
            ]
            ports_visit = [
                al for al in alineaciones
                if al.club_id == p.visitante_id and mvp_view._es_portero(al.jugador, al)
            ]
            
            if ports_local:
                pen = mvp_view._penal_goles_encajados(g_rec_local)
                for al in ports_local:
                    if al.jugador_id in ranking_jornada and pen:
                        ranking_jornada[al.jugador_id]["puntos"] += pen
                if gl > gv and gv <= 1:
                    for al in ports_local:
                        if al.jugador_id in ranking_jornada:
                            ranking_jornada[al.jugador_id]["puntos"] += 1.0
            
            if ports_visit:
                pen = mvp_view._penal_goles_encajados(g_rec_visit)
                for al in ports_visit:
                    if al.jugador_id in ranking_jornada and pen:
                        ranking_jornada[al.jugador_id]["puntos"] += pen
                if gv > gl and gl <= 1:
                    for al in ports_visit:
                        if al.jugador_id in ranking_jornada:
                            ranking_jornada[al.jugador_id]["puntos"] += 1.0
            
            # 4) Extra portero goleador
            for ev in eventos:
                if ev.tipo_evento != "gol" or not ev.jugador_id:
                    continue
                al_ev = al_por_j.get(ev.jugador_id)
                jug_ev = ev.jugador
                if not mvp_view._es_portero(jug_ev, al_ev):
                    continue
                goles_gk = len([
                    e for e in eventos
                    if e.jugador_id == ev.jugador_id and e.tipo_evento == "gol"
                ])
                ranking_jornada[ev.jugador_id]["puntos"] += mvp_view._extra_portero_gol(goles_gk)
        
        # Redondear puntos
        for d in ranking_jornada.values():
            d["puntos"] = ceil(d["puntos"])
        
        return ranking_jornada

    @transaction.atomic
    def handle(self, *args, **opts):
        temporada_nombre: str = opts["temporada"]
        jornada: int | None = opts.get("jornada")
        grupo_id: int | None = opts.get("grupo")
        todas_jornadas: bool = opts.get("todas_jornadas", False)
        dry_run: bool = opts.get("dry_run", False)
        forzar: bool = opts.get("forzar", False)
        
        # 1) Obtener temporada
        try:
            temporada = Temporada.objects.get(nombre=temporada_nombre)
        except Temporada.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"No existe Temporada nombre='{temporada_nombre}'")
            )
            return
        
        # 2) Obtener grupos
        grupos_qs = Grupo.objects.filter(temporada=temporada).select_related("competicion")
        if grupo_id:
            grupos_qs = grupos_qs.filter(id=grupo_id)
        
        grupos = list(grupos_qs)
        if not grupos:
            self.stderr.write(
                self.style.ERROR(f"No hay grupos para la temporada '{temporada_nombre}'")
            )
            return
        
        # 3) Obtener coeficientes
        JORNADA_REF_COEF = 6  # Mismo que MVPGlobalView
        coef_division = _coef_division_lookup(temporada.id, JORNADA_REF_COEF)
        coef_club = _coef_club_lookup(temporada.id, JORNADA_REF_COEF)
        
        # 4) Determinar jornadas a procesar
        if todas_jornadas:
            # Obtener todas las jornadas únicas de los partidos jugados
            jornadas = (
                Partido.objects
                .filter(grupo__temporada=temporada, jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
                .order_by("jornada_numero")
            )
            jornadas_list = list(jornadas)
        elif jornada is not None:
            jornadas_list = [jornada]
        else:
            self.stderr.write(
                self.style.ERROR(
                    "Debes especificar --jornada N o --todas-jornadas"
                )
            )
            return
        
        if not jornadas_list:
            self.stderr.write(
                self.style.WARNING("No hay jornadas con partidos jugados.")
            )
            return
        
        self.stdout.write(
            self.style.NOTICE(
                f"Temporada: {temporada} · Grupos: {len(grupos)} · "
                f"Jornadas: {jornadas_list} · {'DRY-RUN' if dry_run else 'GUARDANDO'}"
            )
        )
        
        total_creados = 0
        total_actualizados = 0
        total_omitidos = 0
        
        # 5) Procesar cada jornada
        for jornada_num in jornadas_list:
            self.stdout.write(
                self.style.NOTICE(f"\n--- Procesando Jornada {jornada_num} ---")
            )
            
            for grupo in grupos:
                # Verificar si ya existe (si no es forzar)
                if not forzar:
                    existe = PuntosMVPJornada.objects.filter(
                        temporada=temporada,
                        grupo=grupo,
                        jornada=jornada_num,
                    ).exists()
                    if existe:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  [Grupo {grupo.id}] J{jornada_num}: Ya existe. "
                                f"Usa --forzar para recalcular."
                            )
                        )
                        total_omitidos += 1
                        continue
                
                # Calcular puntos
                puntos_jugadores = self._calcular_puntos_jugador_jornada(
                    grupo, temporada, jornada_num, coef_division, coef_club
                )
                
                if not puntos_jugadores:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [Grupo {grupo.id}] J{jornada_num}: Sin partidos jugados."
                        )
                    )
                    continue
                
                coef_div = float(coef_division.get(grupo.competicion_id, 1.0))
                
                # Guardar puntos
                for jid, datos in puntos_jugadores.items():
                    try:
                        jugador = Jugador.objects.get(id=jid)
                    except Jugador.DoesNotExist:
                        continue
                    
                    puntos_base = float(datos["puntos"])
                    puntos_con_coef = puntos_base * coef_div
                    
                    if dry_run:
                        self.stdout.write(
                            f"  DRY: {jugador} (Grupo {grupo.id}) J{jornada_num}: "
                            f"{puntos_base:.1f} -> {puntos_con_coef:.1f} (coef={coef_div:.2f}) · "
                            f"{datos['goles']} goles · {datos['partidos_jugados']} partidos"
                        )
                        total_creados += 1
                    else:
                        obj, created = PuntosMVPJornada.objects.update_or_create(
                            jugador=jugador,
                            temporada=temporada,
                            grupo=grupo,
                            jornada=jornada_num,
                            defaults={
                                "puntos_base": puntos_base,
                                "puntos_con_coef": puntos_con_coef,
                                "coef_division": coef_div,
                                "partidos_jugados": datos["partidos_jugados"],
                                "goles": datos["goles"],
                            },
                        )
                        if created:
                            total_creados += 1
                        else:
                            total_actualizados += 1
                        
                        # Actualizar sumatorio total del jugador
                        _actualizar_sumatorio_total(jugador.id, temporada.id)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [Grupo {grupo.id}] J{jornada_num}: "
                        f"{len(puntos_jugadores)} jugadores procesados"
                    )
                )
        
        # 6) Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f"\n=== RESUMEN ==="
                f"\nCreados: {total_creados}"
                f"\nActualizados: {total_actualizados}"
                f"\nOmitidos: {total_omitidos}"
            )
        )

