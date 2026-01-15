# valoraciones/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Prefetch, Min, Max
from math import ceil
from collections import defaultdict
from nucleo.models import Grupo
from partidos.models import Partido, EventoPartido, AlineacionPartidoJugador
from jugadores.models import Jugador
from clubes.models import ClubEnGrupo
from .models import CoeficienteClub, CoeficienteDivision


class PartidoEstrellaView(APIView):
    """
    GET /api/valoraciones/partido-estrella/?grupo_id=1
    GET /api/valoraciones/partido-estrella/?grupo_id=1&jornada=7
    
    Devuelve el partido "más interesante" de la jornada según:
    - coeficiente base de cada club (guardado en CoeficienteClub)
    - cercanía en la clasificación
    - racha reciente
    - potencial goleador
    - penalización por partido muy desigual
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    # --- Helpers internos ---------------------------------------------
    def _bonus_racha(self, racha_texto: str) -> float:
        if not racha_texto:
            return 0.0
        racha_texto = racha_texto.strip().upper()[:5]
        total = 0.0
        for ch in racha_texto:
            if ch == "V":
                total += 0.05
            elif ch == "E":
                total += 0.02
            elif ch == "D":
                total -= 0.03
        return total

    def _bonus_goles(self, goles_local: int, goles_visit: int) -> float:
        goles_local = goles_local or 0
        goles_visit = goles_visit or 0
        bonus = 0.0
        if goles_local >= 35 and goles_visit >= 35:
            bonus += 0.12
        elif goles_local >= 25 and goles_visit >= 25:
            bonus += 0.08
        else:
            if goles_local >= 25 or goles_visit >= 25:
                bonus += 0.04
        return bonus

    def _penalizacion_desigual(self, pos_local, pos_visit) -> float:
        if not pos_local or not pos_visit:
            return 0.0
        diff = abs(pos_local - pos_visit)
        pen = 0.0
        if diff >= 10:
            pen -= 0.15
        elif diff >= 8:
            pen -= 0.10
        elif diff >= 6:
            pen -= 0.06
        top3 = pos_local <= 3 or pos_visit <= 3
        descenso = pos_local >= 15 or pos_visit >= 15
        if top3 and descenso:
            pen -= 0.05
        return pen

    # ------------------------------------------------------------------
    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Grupo
        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # 2. Partidos del grupo
        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        # Jornadas disponibles
        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "partido_estrella": None,
                "ranking_partidos": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 3. Determinar jornada a usar
        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
            if jornada_num not in jornadas_disponibles:
                jornada_num = jornadas_disponibles[-1]
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = jornadas_disponibles[-1]

        # 4. Partidos de esa jornada
        partidos_jornada = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
            .order_by("fecha_hora", "id")
        )

        if not partidos_jornada:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "partido_estrella": None,
                "ranking_partidos": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        # 5. Lookups de clasificación (para posiciones y rachas)
        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        clasif_lookup = {}
        for c in clasif_rows:
            clasif_lookup[c.club_id] = {
                "pos": c.posicion_actual,
                "racha": (c.racha or "").strip().upper(),
            }

        # 6. Lookups de coeficientes (club)
        coef_rows = (
            CoeficienteClub.objects
            .filter(
                temporada_id=self.TEMPORADA_ID_BASE,
                jornada_referencia=self.JORNADA_REF_COEF,
            )
            .select_related("club")
        )
        coef_lookup = {r.club_id: r.valor for r in coef_rows}

        # 7. Estadística de goles para "partidos alegres"
        partidos_jugados = (
            qs_partidos_grupo
            .filter(
                jugado=True,
                goles_local__isnull=False,
                goles_visitante__isnull=False,
            )
            .values("local_id", "visitante_id", "goles_local", "goles_visitante")
        )
        goles_por_club = {}
        for p in partidos_jugados:
            lid = p["local_id"]
            vid = p["visitante_id"]
            gl = p["goles_local"] or 0
            gv = p["goles_visitante"] or 0
            goles_por_club[lid] = goles_por_club.get(lid, 0) + gl
            goles_por_club[vid] = goles_por_club.get(vid, 0) + gv

        # 8. Calcular score por partido
        ranking = []
        for p in partidos_jornada:
            local_id = p.local_id
            visit_id = p.visitante_id
            coef_local = coef_lookup.get(local_id, 0.4)
            coef_visit = coef_lookup.get(visit_id, 0.4)
            base_score = coef_local + coef_visit  # 👈 sin coeficiente de división

            pos_local = clasif_lookup.get(local_id, {}).get("pos")
            pos_visit = clasif_lookup.get(visit_id, {}).get("pos")
            bonus_duelo = 0.0
            if pos_local and pos_visit:
                if {pos_local, pos_visit} == {1, 2}:
                    bonus_duelo += 0.25
                elif abs(pos_local - pos_visit) == 1 and max(pos_local, pos_visit) <= 4:
                    bonus_duelo += 0.15
                diff = abs(pos_local - pos_visit)
                if diff <= 2:
                    bonus_duelo += 0.08
                elif diff <= 4:
                    bonus_duelo += 0.04

            racha_local = clasif_lookup.get(local_id, {}).get("racha", "")
            racha_visit = clasif_lookup.get(visit_id, {}).get("racha", "")
            bonus_r = self._bonus_racha(racha_local) + self._bonus_racha(racha_visit)

            goles_local = goles_por_club.get(local_id, 0)
            goles_visit = goles_por_club.get(visit_id, 0)
            bonus_goles = self._bonus_goles(goles_local, goles_visit)

            penal = self._penalizacion_desigual(pos_local, pos_visit)

            score_final = base_score + bonus_duelo + bonus_r + bonus_goles + penal

            ranking.append({
                "partido_id": p.identificador_federacion or p.id,
                "jornada": p.jornada_numero,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "pabellon": p.pabellon or (p.local.pabellon if p.local else ""),
                "local": {
                    "id": p.local.id,
                    "nombre": p.local.nombre_corto or p.local.nombre_oficial,
                    "escudo": p.local.escudo_url or "",
                    "posicion": pos_local,
                    "coeficiente": float(coef_local),
                    "racha": racha_local,
                    "goles_temporada": goles_local,
                },
                "visitante": {
                    "id": p.visitante.id,
                    "nombre": p.visitante.nombre_corto or p.visitante.nombre_oficial,
                    "escudo": p.visitante.escudo_url or "",
                    "posicion": pos_visit,
                    "coeficiente": float(coef_visit),
                    "racha": racha_visit,
                    "goles_temporada": goles_visit,
                },
                "score": round(score_final, 3),
            })

        ranking.sort(key=lambda x: -x["score"])

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "partido_estrella": ranking[0] if ranking else None,
            "ranking_partidos": ranking,
        }
        return Response(payload, status=status.HTTP_200_OK)


class EquipoJornadaView(APIView):
    """
    GET /api/valoraciones/equipo-jornada/?grupo_id=1
    GET /api/valoraciones/equipo-jornada/?grupo_id=1&jornada=7
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    def _norm_media(self, path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/media/"):
            return path
        return "/media/" + path.lstrip("/")

    def _bonus_rival_fuerte(self, coef_rival: float) -> float:
        if coef_rival is None:
            return 0.0
        if coef_rival >= 0.8:
            return 0.35
        if coef_rival >= 0.6:
            return 0.20
        if coef_rival >= 0.4:
            return 0.10
        return 0.0

    def _bonus_diferencia(self, dif_goles: int) -> float:
        if dif_goles >= 3:
            return 0.35
        if dif_goles == 2:
            return 0.20
        if dif_goles == 1:
            return 0.10
        return 0.0

    def _penalizacion_rival_debil(self, pos_rival: int | None) -> float:
        if not pos_rival:
            return 0.0
        if pos_rival >= 14:
            return -0.15
        return 0.0

    def _bonus_rompe_racha(self, racha_rival: str | None) -> float:
        if not racha_rival:
            return 0.0
        r = racha_rival.strip().upper()
        streak_v = 0
        for ch in r:
            if ch == "V":
                streak_v += 1
            else:
                break
        if streak_v >= 3:
            return 0.15
        return 0.0

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
        )

        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "equipo_de_la_jornada": None,
                "ranking_clubes": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
            if jornada_num not in jornadas_disponibles:
                jornada_num = jornadas_disponibles[-1]
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = jornadas_disponibles[-1]

        partidos_jornada = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
            .order_by("fecha_hora", "id")
        )

        if not partidos_jornada:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "equipo_de_la_jornada": None,
                "ranking_clubes": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        clasif_rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        clasif_lookup = {}
        for c in clasif_rows:
            raw_escudo = getattr(c.club, "escudo_url", "") or ""
            clasif_lookup[c.club_id] = {
                "pos": c.posicion_actual,
                "racha": (c.racha or "").strip().upper(),
                "escudo": self._norm_media(raw_escudo),
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }

        coef_rows = (
            CoeficienteClub.objects
            .filter(
                temporada_id=self.TEMPORADA_ID_BASE,
                jornada_referencia=self.JORNADA_REF_COEF,
            )
            .select_related("club")
        )
        coef_lookup = {r.club_id: r.valor for r in coef_rows}

        ranking_clubes = {}
        for p in partidos_jornada:
            if not p.jugado:
                continue
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            local_id = p.local_id
            visit_id = p.visitante_id

            if gl > gv:
                base_local = 1.0
            elif gl == gv:
                base_local = 0.4
            else:
                base_local = 0.0

            coef_rival_local = coef_lookup.get(visit_id, 0.4)
            bonus_rival_local = self._bonus_rival_fuerte(coef_rival_local)
            dif_local = gl - gv
            bonus_dif_local = self._bonus_diferencia(dif_local)
            pos_rival_local = clasif_lookup.get(visit_id, {}).get("pos")
            pen_rival_local = self._penalizacion_rival_debil(pos_rival_local)
            racha_rival_local = clasif_lookup.get(visit_id, {}).get("racha")
            bonus_rompe_local = self._bonus_rompe_racha(racha_rival_local)
            coef_local = coef_lookup.get(local_id, 0.4)

            score_local = (
                base_local +
                bonus_rival_local +
                bonus_dif_local +
                bonus_rompe_local +
                pen_rival_local
            )
            score_local *= (0.9 + coef_local)

            if local_id not in ranking_clubes:
                raw_local_escudo = clasif_lookup.get(local_id, {}).get("escudo") or (p.local.escudo_url or "")
                ranking_clubes[local_id] = {
                    "club_id": local_id,
                    "nombre": clasif_lookup.get(local_id, {}).get("nombre", p.local.nombre_corto or p.local.nombre_oficial),
                    "escudo": self._norm_media(raw_local_escudo),
                    "score": 0.0,
                    "motivos": [],
                }

            motivo_local_parts = []
            if gl > gv:
                motivo_local_parts.append("Victoria")
            elif gl == gv:
                motivo_local_parts.append("Empate")
            else:
                motivo_local_parts.append("Derrota digna" if bonus_rival_local > 0 else "Derrota")
            if dif_local >= 3:
                motivo_local_parts.append("con goleada")
            elif dif_local == 2:
                motivo_local_parts.append("con buen margen")
            if pos_rival_local and pos_rival_local <= 6:
                motivo_local_parts.append("ante rival de la parte alta")
            if bonus_rompe_local > 0:
                motivo_local_parts.append("rompiendo racha rival")

            ranking_clubes[local_id]["score"] += round(score_local, 4)
            ranking_clubes[local_id]["motivos"].append(" ".join(motivo_local_parts))

            # ---- VISITANTE ----
            if gv > gl:
                base_visit = 1.0
            elif gv == gl:
                base_visit = 0.4
            else:
                base_visit = 0.0

            coef_rival_visit = coef_lookup.get(local_id, 0.4)
            bonus_rival_visit = self._bonus_rival_fuerte(coef_rival_visit)
            dif_visit = gv - gl
            bonus_dif_visit = self._bonus_diferencia(dif_visit)
            pos_rival_visit = clasif_lookup.get(local_id, {}).get("pos")
            pen_rival_visit = self._penalizacion_rival_debil(pos_rival_visit)
            racha_rival_visit = clasif_lookup.get(local_id, {}).get("racha")
            bonus_rompe_visit = self._bonus_rompe_racha(racha_rival_visit)
            coef_visit = coef_lookup.get(visit_id, 0.4)
            bonus_fuera = 0.0
            if gv > gl:
                bonus_fuera = 0.25

            score_visit = (
                base_visit +
                bonus_rival_visit +
                bonus_dif_visit +
                bonus_rompe_visit +
                pen_rival_visit +
                bonus_fuera
            )
            score_visit *= (0.9 + coef_visit)

            if visit_id not in ranking_clubes:
                raw_visit_escudo = clasif_lookup.get(visit_id, {}).get("escudo") or (p.visitante.escudo_url or "")
                ranking_clubes[visit_id] = {
                    "club_id": visit_id,
                    "nombre": clasif_lookup.get(visit_id, {}).get("nombre", p.visitante.nombre_corto or p.visitante.nombre_oficial),
                    "escudo": self._norm_media(raw_visit_escudo),
                    "score": 0.0,
                    "motivos": [],
                }

            motivo_visit_parts = []
            if gv > gl:
                motivo_visit_parts.append("Victoria a domicilio")
            elif gv == gl:
                motivo_visit_parts.append("Empate fuera")
            else:
                motivo_visit_parts.append("Derrota")
            if dif_visit >= 3:
                motivo_visit_parts.append("con goleada")
            elif dif_visit == 2:
                motivo_visit_parts.append("con buen margen")
            if pos_rival_visit and pos_rival_visit <= 6:
                motivo_visit_parts.append("ante rival de la parte alta")
            if bonus_rompe_visit > 0:
                motivo_visit_parts.append("rompiendo racha rival")

            ranking_clubes[visit_id]["score"] += round(score_visit, 4)
            ranking_clubes[visit_id]["motivos"].append(" ".join(motivo_visit_parts))

        ranking_lista = list(ranking_clubes.values())
        ranking_lista.sort(key=lambda x: x["score"], reverse=True)

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "equipo_de_la_jornada": ranking_lista[0] if ranking_lista else None,
            "ranking_clubes": ranking_lista,
        }
        return Response(payload, status=status.HTTP_200_OK)


class JugadoresJornadaView(APIView):
    """
    GET /api/valoraciones/jugadores-jornada/?grupo_id=1
    GET /api/valoraciones/jugadores-jornada/?grupo_id=1&jornada=7
    GET /api/valoraciones/jugadores-jornada/?grupo_id=1&only_porteros=1
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    def _norm_media(self, path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/media/"):
            return path
        return "/media/" + path.lstrip("/")

    def _abs_media(self, request, path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return request.build_absolute_uri(path)

    def _get_clasif_lookup(self, grupo):
        rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        out = {}
        for c in rows:
            out[c.club_id] = {
                "pos": c.posicion_actual,
                "racha": (c.racha or "").strip().upper(),
                "escudo": self._norm_media(c.club.escudo_url or ""),
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }
        return out

    def _get_coef_lookup(self):
        rows = (
            CoeficienteClub.objects
            .filter(
                temporada_id=self.TEMPORADA_ID_BASE,
                jornada_referencia=self.JORNADA_REF_COEF,
            )
            .select_related("club")
        )
        return {r.club_id: r.valor for r in rows}

    def _puntos_presencia(self, es_titular: bool) -> float:
        return 3.0 if es_titular else 1.0

    def _puntos_evento(self, ev: EventoPartido) -> float:
        t = ev.tipo_evento
        if t == "gol":
            return 3.0
        if t == "gol_pp":
            return -2.0
        if t == "amarilla":
            return -1.0
        if t == "doble_amarilla":
            return -3.0
        if t == "roja":
            return -5.0
        if t == "mvp":
            return 3.0
        return 0.0

    def _bonus_resultado(self, partido: Partido, club_id_jugador: int | None) -> float:
        if not partido.jugado or club_id_jugador is None:
            return 0.0
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        if partido.local_id == club_id_jugador:
            if gl > gv:
                return 2.0
            elif gl == gv:
                return 1.0
            else:
                return 0.0
        else:
            if gv > gl:
                return 2.0
            elif gv == gl:
                return 1.0
            else:
                return 0.0

    def _bonus_rival_fuerte(self, partido: Partido, club_id_jugador: int | None, coef_lookup: dict) -> float:
        if club_id_jugador is None:
            return 0.0
        rival_id = partido.visitante_id if partido.local_id == club_id_jugador else partido.local_id
        coef_rival = coef_lookup.get(rival_id, 0.4)
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        gano_empato = (gl >= gv) if partido.local_id == club_id_jugador else (gv >= gl)
        if not gano_empato:
            return 0.0
        if coef_rival >= 0.8:
            return 1.0
        if coef_rival >= 0.6:
            return 0.5
        return 0.0

    def _bonus_duelo_fuertes(self, partido: Partido, coef_lookup: dict) -> float:
        coef_local = coef_lookup.get(partido.local_id, 0.4)
        coef_visit = coef_lookup.get(partido.visitante_id, 0.4)
        if coef_local >= 0.8 and coef_visit >= 0.8:
            return 1.0
        if coef_local >= 0.6 and coef_visit >= 0.6:
            return 0.5
        return 0.0

    def _bonus_intensidad(self, partido: Partido) -> float:
        if partido.indice_intensidad is None:
            return 0.0
        if partido.indice_intensidad >= 90:
            return 1.0
        if partido.indice_intensidad >= 80:
            return 0.5
        return 0.0

    def _gol_decisivo(self, partido: Partido, jugador_id: int, club_id_jugador: int) -> float:
        if not partido.jugado:
            return 0.0
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        if abs(gl - gv) != 1:
            return 0.0
        eventos = list(partido.eventos.filter(tipo_evento__in=["gol"]).order_by("minuto", "id"))
        if not eventos:
            return 0.0
        ultimo = eventos[-1]
        if not ultimo.jugador_id:
            return 0.0
        gol_del_local = (partido.local_id == (ultimo.club_id or 0))
        ganador_es_local = gl > gv
        if ganador_es_local and not gol_del_local:
            return 0.0
        if (not ganador_es_local) and gol_del_local:
            return 0.0
        if ultimo.jugador_id == jugador_id:
            return 1.0
        return 0.0

    def _es_portero(self, jugador: Jugador | None, alineacion: AlineacionPartidoJugador | None) -> bool:
        if alineacion and alineacion.etiqueta and alineacion.etiqueta.lower().startswith("pt"):
            return True
        if jugador and (jugador.posicion_principal == "portero"):
            return True
        return False

    def _puntos_portero_goles_marcados(self, goles_marcados_portero: int) -> float:
        if goles_marcados_portero <= 0:
            return 0.0
        if goles_marcados_portero == 1:
            return 5.0
        if goles_marcados_portero == 2:
            return 12.0
        return 20.0

    def _puntos_portero_goles_encajados(self, goles_recibidos: int) -> float:
        if goles_recibidos <= 2:
            return 0.0
        return float(-(goles_recibidos - 2))

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")
        only_porteros = request.GET.get("only_porteros") in ["1", "true", "True"]

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs_partidos_grupo = (
            Partido.objects
            .filter(grupo=grupo)
            .select_related("local", "visitante")
            .prefetch_related("eventos", "alineaciones_jugadores")
        )

        jornadas_disponibles = sorted(set(
            qs_partidos_grupo.values_list("jornada_numero", flat=True).distinct()
        ))

        if not jornadas_disponibles:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": None,
                "jugador_de_la_jornada": None,
                "ranking_jugadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
            if jornada_num not in jornadas_disponibles:
                jornada_num = jornadas_disponibles[-1]
        else:
            jugadas = (
                qs_partidos_grupo
                .filter(jugado=True)
                .values_list("jornada_numero", flat=True)
                .distinct()
            )
            jugadas = sorted(set(jugadas))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = jornadas_disponibles[-1]

        partidos_jornada = list(
            qs_partidos_grupo
            .filter(jornada_numero=jornada_num)
            .order_by("fecha_hora", "id")
        )

        if not partidos_jornada:
            payload_vacio = {
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada": jornada_num,
                "jugador_de_la_jornada": None,
                "ranking_jugadores": [],
            }
            return Response(payload_vacio, status=status.HTTP_200_OK)

        clasif_lookup = self._get_clasif_lookup(grupo)
        coef_lookup = self._get_coef_lookup()

        ranking_jugadores: dict[int, dict] = {}

        for p in partidos_jornada:
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            bonus_duelo_fuertes = self._bonus_duelo_fuertes(p, coef_lookup)
            bonus_intensidad = self._bonus_intensidad(p)

            alineaciones = list(p.alineaciones_jugadores.all())
            alineacion_por_jugador = {al.jugador_id: al for al in alineaciones if al.jugador_id}
            eventos = list(p.eventos.all())

            # 1) PRESENCIA
            for al in alineaciones:
                jugador = al.jugador
                if not jugador:
                    continue
                jugador_id = jugador.id
                club_id_jugador = al.club_id
                es_portero_flag = self._es_portero(jugador, al)

                if jugador_id not in ranking_jugadores:
                    club_info = clasif_lookup.get(club_id_jugador or 0, {})
                    ranking_jugadores[jugador_id] = {
                        "jugador_id": jugador_id,
                        "nombre": jugador.apodo or jugador.nombre,
                        "foto": self._norm_media(jugador.foto_url or ""),
                        "club_id": club_id_jugador,
                        "club_nombre": club_info.get("nombre", ""),
                        "club_escudo": club_info.get("escudo", ""),
                        "puntos": 0.0,
                        "detalles": [],
                        "es_portero": es_portero_flag,
                    }
                else:
                    if es_portero_flag:
                        ranking_jugadores[jugador_id]["es_portero"] = True

                pts_pres = self._puntos_presencia(al.titular)
                ranking_jugadores[jugador_id]["puntos"] += pts_pres
                ranking_jugadores[jugador_id]["detalles"].append(f"presencia: +{pts_pres}")

                pts_res = self._bonus_resultado(p, club_id_jugador)
                if pts_res:
                    ranking_jugadores[jugador_id]["puntos"] += pts_res
                    ranking_jugadores[jugador_id]["detalles"].append(f"resultado: +{pts_res}")

                pts_rival = self._bonus_rival_fuerte(p, club_id_jugador, coef_lookup)
                if pts_rival:
                    ranking_jugadores[jugador_id]["puntos"] += pts_rival
                    ranking_jugadores[jugador_id]["detalles"].append(f"rival fuerte: +{pts_rival}")

                if bonus_duelo_fuertes:
                    ranking_jugadores[jugador_id]["puntos"] += bonus_duelo_fuertes
                    ranking_jugadores[jugador_id]["detalles"].append(f"duelo fuertes: +{bonus_duelo_fuertes}")

                if bonus_intensidad:
                    ranking_jugadores[jugador_id]["puntos"] += bonus_intensidad
                    ranking_jugadores[jugador_id]["detalles"].append(f"intensidad: +{bonus_intensidad}")

            # 2) EVENTOS
            for ev in eventos:
                if not ev.jugador_id:
                    continue
                jugador_id = ev.jugador_id
                jug = ev.jugador
                al_ev = alineacion_por_jugador.get(jugador_id)
                es_portero_ev = self._es_portero(jug, al_ev)

                if jugador_id not in ranking_jugadores:
                    club_id_evento = ev.club_id
                    club_info = clasif_lookup.get(club_id_evento or 0, {})
                    ranking_jugadores[jugador_id] = {
                        "jugador_id": jugador_id,
                        "nombre": jug.apodo or jug.nombre if jug else f"Jugador {jugador_id}",
                        "foto": self._norm_media(jug.foto_url) if jug else "",
                        "club_id": club_id_evento or None,
                        "club_nombre": club_info.get("nombre", ""),
                        "club_escudo": club_info.get("escudo", ""),
                        "puntos": 0.0,
                        "detalles": [],
                        "es_portero": es_portero_ev,
                    }
                else:
                    if es_portero_ev:
                        ranking_jugadores[jugador_id]["es_portero"] = True

                pts_ev = self._puntos_evento(ev)
                if pts_ev:
                    ranking_jugadores[jugador_id]["puntos"] += pts_ev
                    ranking_jugadores[jugador_id]["detalles"].append(
                        f"evento {ev.tipo_evento}: {pts_ev:+}"
                    )

            # 3) Bonus gol decisivo
            if abs(gl - gv) == 1:
                for jugador_id, data_jug in list(ranking_jugadores.items()):
                    if jugador_id not in alineacion_por_jugador:
                        continue
                    club_id_jugador = data_jug["club_id"]
                    bonus_dec = self._gol_decisivo(p, jugador_id, club_id_jugador)
                    if bonus_dec:
                        data_jug["puntos"] += bonus_dec
                        data_jug["detalles"].append(f"gol decisivo: +{bonus_dec}")

            # 4) Porteros: goles encajados
            goles_recibidos_local = gv
            goles_recibidos_visit = gl

            porteros_local = [
                al for al in alineaciones
                if al.club_id == p.local_id and self._es_portero(al.jugador, al)
            ]
            porteros_visit = [
                al for al in alineaciones
                if al.club_id == p.visitante_id and self._es_portero(al.jugador, al)
            ]

            if porteros_local:
                pen_local = self._puntos_portero_goles_encajados(goles_recibidos_local)
                for al in porteros_local:
                    if not al.jugador_id:
                        continue
                    if al.jugador_id in ranking_jugadores and pen_local:
                        ranking_jugadores[al.jugador_id]["puntos"] += pen_local
                        ranking_jugadores[al.jugador_id]["detalles"].append(f"goles encajados: {pen_local:+}")

                if p.jugado and (gl > gv) and (gv <= 1):
                    for al in porteros_local:
                        if not al.jugador_id:
                            continue
                        ranking_jugadores[al.jugador_id]["puntos"] += 1.0
                        ranking_jugadores[al.jugador_id]["detalles"].append("portería seria: +1")

            if porteros_visit:
                pen_visit = self._puntos_portero_goles_encajados(goles_recibidos_visit)
                for al in porteros_visit:
                    if not al.jugador_id:
                        continue
                    if al.jugador_id in ranking_jugadores and pen_visit:
                        ranking_jugadores[al.jugador_id]["puntos"] += pen_visit
                        ranking_jugadores[al.jugador_id]["detalles"].append(f"goles encajados: {pen_visit:+}")

                if p.jugado and (gv > gl) and (gl <= 1):
                    for al in porteros_visit:
                        if not al.jugador_id:
                            continue
                        ranking_jugadores[al.jugador_id]["puntos"] += 1.0
                        ranking_jugadores[al.jugador_id]["detalles"].append("portería seria: +1")

            # 5) Porteros: goles marcados
            for ev in eventos:
                if ev.tipo_evento != "gol" or not ev.jugador_id:
                    continue
                al_ev = alineacion_por_jugador.get(ev.jugador_id)
                jug_ev = ev.jugador
                if not self._es_portero(jug_ev, al_ev):
                    continue

                goles_portero = len([
                    e for e in eventos
                    if e.jugador_id == ev.jugador_id and e.tipo_evento == "gol"
                ])
                pts_port_gol = self._puntos_portero_goles_marcados(goles_portero)
                if pts_port_gol:
                    ranking_jugadores[ev.jugador_id]["puntos"] += pts_port_gol
                    ranking_jugadores[ev.jugador_id]["detalles"].append(f"gol(es) de portero: +{pts_port_gol}")

        ranking_lista = []
        for _, data in ranking_jugadores.items():
            puntos_final = ceil(data["puntos"])
            data["puntos"] = puntos_final
            ranking_lista.append(data)

        if only_porteros:
            ranking_lista = [r for r in ranking_lista if r.get("es_portero")]

        ranking_lista.sort(key=lambda x: x["puntos"], reverse=True)

        for row in ranking_lista:
            row["foto"] = self._abs_media(request, row.get("foto", ""))
            row["club_escudo"] = self._abs_media(request, row.get("club_escudo", ""))

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada": jornada_num,
            "jugador_de_la_jornada": ranking_lista[0] if ranking_lista else None,
            "ranking_jugadores": ranking_lista,
        }
        return Response(payload, status=status.HTTP_200_OK)


# ============================================
# FUNCIONES HELPER GLOBALES
# ============================================

def _coef_division_lookup(temporada_id: int, jornada_ref: int | None = None) -> dict[int, float]:
    """
    {competicion_id: coef} priorizando la jornada_ref si se pasa; si no, el último por competición.
    """
    qs = CoeficienteDivision.objects.filter(temporada_id=temporada_id)
    if jornada_ref is not None:
        # primero exactos de esa jornada
        exactos = list(qs.filter(jornada_referencia=jornada_ref))
        exact_ids = {r.competicion_id for r in exactos}
        # fallback: último por competición para los que falten
        ultimos = {}
        for r in qs.exclude(competicion_id__in=exact_ids).order_by("competicion_id", "-actualizado_en"):
            if r.competicion_id not in ultimos:
                ultimos[r.competicion_id] = r
        out = {r.competicion_id: float(r.valor) for r in exactos}
        out.update({cid: float(r.valor) for cid, r in ultimos.items()})
        return out
    # sin jornada -> último por competición
    ultimos = {}
    for r in qs.order_by("competicion_id", "-actualizado_en"):
        if r.competicion_id not in ultimos:
            ultimos[r.competicion_id] = r
    return {cid: float(r.valor) for cid, r in ultimos.items()}


def _coef_club_lookup(temporada_id: int, jornada_ref: int | None = None) -> dict[int, float]:
    """
    {club_id: coef} intentando clavar jornada_ref; si no hay para un club, usa su último en temporada.
    Si tampoco hay, usa 0.5 (misma filosofía que CoeficientesClubesView).
    """
    qs = CoeficienteClub.objects.filter(temporada_id=temporada_id)
    por_jornada = {}
    ultimo = {}
    for c in qs:
        if c.jornada_referencia == jornada_ref:
            por_jornada[c.club_id] = c.valor
        if c.club_id not in ultimo or c.actualizado_en > ultimo[c.club_id][1]:
            ultimo[c.club_id] = (c.valor, c.actualizado_en)
    out = {}
    for cid in set(list(por_jornada.keys()) + list(ultimo.keys())):
        if jornada_ref is not None and cid in por_jornada:
            out[cid] = float(por_jornada[cid])
        else:
            out[cid] = float(ultimo.get(cid, (0.5, None))[0])  # fallback 0.5
    return out


def _norm_media(path: str | None) -> str:
    if not path:
        return ""
    path = path.strip()
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if path.startswith("/media/"):
        return path
    return "/media/" + path.lstrip("/")


def _abs_media(request, path: str | None) -> str:
    if not path:
        return ""
    path = path.strip()
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return request.build_absolute_uri(path)


def _get_temporada_id(request, default_id: int) -> int:
    t = request.GET.get("temporada_id")
    if not t:
        return default_id
    try:
        return int(t)
    except ValueError:
        return default_id


def _get_jornada_opt(request) -> int | None:
    j = request.GET.get("jornada")
    if not j:
        return None
    try:
        return int(j)
    except ValueError:
        return None


def _get_bool(request, key: str, default: bool = False) -> bool:
    val = request.GET.get(key)
    if val is None:
        return default
    return str(val).lower() in ["1", "true", "t", "yes", "y", "on"]


def _get_int(request, key: str, default: int) -> int:
    try:
        return int(request.GET.get(key, default))
    except (TypeError, ValueError):
        return default
    

class MVPClasificacionView(APIView):
    """
    GET /api/valoraciones/mvp-clasificacion/?grupo_id=1
    GET /api/valoraciones/mvp-clasificacion/?grupo_id=1&jornada=7
    GET /api/valoraciones/mvp-clasificacion/?grupo_id=1&jornada=7&only_porteros=1
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6

    def _norm_media(self, path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if path.startswith("/media/"):
            return path
        return "/media/" + path.lstrip("/")

    def _abs_media(self, request, path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return request.build_absolute_uri(path)

    def _get_clasif_lookup(self, grupo):
        rows = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
        )
        out = {}
        for c in rows:
            out[c.club_id] = {
                "pos": c.posicion_actual,
                "racha": (c.racha or "").strip().upper(),
                "escudo": self._norm_media(c.club.escudo_url or ""),
                "nombre": c.club.nombre_corto or c.club.nombre_oficial,
            }
        return out

    def _get_coef_lookup(self):
        rows = (
            CoeficienteClub.objects
            .filter(
                temporada_id=self.TEMPORADA_ID_BASE,
                jornada_referencia=self.JORNADA_REF_COEF,
            )
            .select_related("club")
        )
        return {r.club_id: r.valor for r in rows}

    def _calcular_puntos_de_jornada(self, partido: Partido, clasif_lookup: dict, coef_lookup: dict) -> dict[int, dict]:
        ranking_jugadores: dict[int, dict] = {}
        gl = partido.goles_local or 0
        gv = partido.goles_visitante or 0
        coef_local = coef_lookup.get(partido.local_id, 0.4)
        coef_visit = coef_lookup.get(partido.visitante_id, 0.4)

        bonus_duelo_fuertes = 0.0
        if coef_local >= 0.8 and coef_visit >= 0.8:
            bonus_duelo_fuertes = 1.0
        elif coef_local >= 0.6 and coef_visit >= 0.6:
            bonus_duelo_fuertes = 0.5

        bonus_intensidad = 0.0
        if partido.indice_intensidad is not None:
            if partido.indice_intensidad >= 90:
                bonus_intensidad = 1.0
            elif partido.indice_intensidad >= 80:
                bonus_intensidad = 0.5

        alineaciones = list(partido.alineaciones_jugadores.all())
        alineacion_por_jugador = {al.jugador_id: al for al in alineaciones if al.jugador_id}
        eventos = list(partido.eventos.all())

        # 1) Presencia y contexto
        for al in alineaciones:
            jug = al.jugador
            if not jug:
                continue
            jugador_id = jug.id
            club_id_jugador = al.club_id
            es_portero_flag = False
            if al.etiqueta and al.etiqueta.lower().startswith("pt"):
                es_portero_flag = True
            elif jug.posicion_principal == "portero":
                es_portero_flag = True

            if jugador_id not in ranking_jugadores:
                club_info = clasif_lookup.get(club_id_jugador or 0, {})
                ranking_jugadores[jugador_id] = {
                    "jugador_id": jugador_id,
                    "nombre": jug.apodo or jug.nombre,
                    "foto": self._norm_media(jug.foto_url or ""),
                    "club_id": club_id_jugador,
                    "club_nombre": club_info.get("nombre", ""),
                    "club_escudo": club_info.get("escudo", ""),
                    "puntos": 0.0,
                    "es_portero": es_portero_flag,
                }
            else:
                if es_portero_flag:
                    ranking_jugadores[jugador_id]["es_portero"] = True

            pts_pres = 3.0 if al.titular else 1.0
            ranking_jugadores[jugador_id]["puntos"] += pts_pres

            pts_res = 0.0
            if partido.jugado:
                if club_id_jugador == partido.local_id:
                    if gl > gv:
                        pts_res = 2.0
                    elif gl == gv:
                        pts_res = 1.0
                else:
                    if gv > gl:
                        pts_res = 2.0
                    elif gv == gl:
                        pts_res = 1.0
            if pts_res:
                ranking_jugadores[jugador_id]["puntos"] += pts_res

            rival_id = partido.visitante_id if club_id_jugador == partido.local_id else partido.local_id
            coef_rival = coef_lookup.get(rival_id, 0.4)
            if pts_res:
                if coef_rival >= 0.8:
                    ranking_jugadores[jugador_id]["puntos"] += 1.0
                elif coef_rival >= 0.6:
                    ranking_jugadores[jugador_id]["puntos"] += 0.5

            if bonus_duelo_fuertes:
                ranking_jugadores[jugador_id]["puntos"] += bonus_duelo_fuertes
            if bonus_intensidad:
                ranking_jugadores[jugador_id]["puntos"] += bonus_intensidad

        # 2) Eventos
        for ev in eventos:
            if not ev.jugador_id:
                continue
            jug = ev.jugador
            jugador_id = ev.jugador_id
            al_ev = alineacion_por_jugador.get(jugador_id)
            es_portero_ev = False
            if al_ev and al_ev.etiqueta and al_ev.etiqueta.lower().startswith("pt"):
                es_portero_ev = True
            elif jug and jug.posicion_principal == "portero":
                es_portero_ev = True

            if jugador_id not in ranking_jugadores:
                club_id_evento = ev.club_id
                club_info = clasif_lookup.get(club_id_evento or 0, {})
                ranking_jugadores[jugador_id] = {
                    "jugador_id": jugador_id,
                    "nombre": jug.apodo or jug.nombre if jug else f"Jugador {jugador_id}",
                    "foto": self._norm_media(jug.foto_url) if jug else "",
                    "club_id": club_id_evento or None,
                    "club_nombre": club_info.get("nombre", ""),
                    "club_escudo": club_info.get("escudo", ""),
                    "puntos": 0.0,
                    "es_portero": es_portero_ev,
                }
            else:
                if es_portero_ev:
                    ranking_jugadores[jugador_id]["es_portero"] = True

            t = ev.tipo_evento
            pts_ev = 0.0
            if t == "gol":
                pts_ev = 3.0
            elif t == "gol_pp":
                pts_ev = -2.0
            elif t == "amarilla":
                pts_ev = -1.0
            elif t == "doble_amarilla":
                pts_ev = -3.0
            elif t == "roja":
                pts_ev = -5.0
            elif t == "mvp":
                pts_ev = 3.0
            if pts_ev:
                ranking_jugadores[jugador_id]["puntos"] += pts_ev

        # 3) Porteros: goles encajados
        goles_recibidos_local = gv
        goles_recibidos_visit = gl

        porteros_local = [
            al for al in alineaciones
            if al.club_id == partido.local_id and (
                (al.etiqueta and al.etiqueta.lower().startswith("pt")) or
                (al.jugador and al.jugador.posicion_principal == "portero")
            )
        ]
        porteros_visit = [
            al for al in alineaciones
            if al.club_id == partido.visitante_id and (
                (al.etiqueta and al.etiqueta.lower().startswith("pt")) or
                (al.jugador and al.jugador.posicion_principal == "portero")
            )
        ]

        def _penal_goles(g):
            if g <= 2:
                return 0.0
            return float(-(g - 2))

        if porteros_local:
            pen = _penal_goles(goles_recibidos_local)
            for al in porteros_local:
                if al.jugador_id in ranking_jugadores and pen:
                    ranking_jugadores[al.jugador_id]["puntos"] += pen
            if partido.jugado and gl > gv and gv <= 1:
                for al in porteros_local:
                    if al.jugador_id in ranking_jugadores:
                        ranking_jugadores[al.jugador_id]["puntos"] += 1.0

        if porteros_visit:
            pen = _penal_goles(goles_recibidos_visit)
            for al in porteros_visit:
                if al.jugador_id in ranking_jugadores and pen:
                    ranking_jugadores[al.jugador_id]["puntos"] += pen
            if partido.jugado and gv > gl and gl <= 1:
                for al in porteros_visit:
                    if al.jugador_id in ranking_jugadores:
                        ranking_jugadores[al.jugador_id]["puntos"] += 1.0

        # 4) Portero que marca
        for ev in eventos:
            if ev.tipo_evento != "gol" or not ev.jugador_id:
                continue
            al_ev = alineacion_por_jugador.get(ev.jugador_id)
            jug_ev = ev.jugador
            is_gk = False
            if al_ev and al_ev.etiqueta and al_ev.etiqueta.lower().startswith("pt"):
                is_gk = True
            elif jug_ev and jug_ev.posicion_principal == "portero":
                is_gk = True
            if not is_gk:
                continue

            goles_portero = len([e for e in eventos if e.jugador_id == ev.jugador_id and e.tipo_evento == "gol"])
            if goles_portero == 1:
                extra = 5.0
            elif goles_portero == 2:
                extra = 12.0
            else:
                extra = 20.0
            ranking_jugadores[ev.jugador_id]["puntos"] += extra

        for jid, data in ranking_jugadores.items():
            data["puntos"] = ceil(data["puntos"])
        return ranking_jugadores

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")
        only_porteros = request.GET.get("only_porteros") in ["1", "true", "True"]

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grupo = (
                Grupo.objects
                .select_related("competicion", "temporada")
                .get(id=grupo_id)
            )
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs_partidos = (
            Partido.objects
            .filter(grupo=grupo)
            .prefetch_related("eventos", "alineaciones_jugadores")
        )

        jornadas_disponibles = sorted(set(qs_partidos.values_list("jornada_numero", flat=True).distinct()))

        if not jornadas_disponibles:
            return Response({
                "grupo": {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "competicion": grupo.competicion.nombre,
                    "temporada": grupo.temporada.nombre,
                },
                "jornada_aplicada": None,
                "jornadas_disponibles": [],
                "ranking": [],
                "prev_ranking": [],
            }, status=status.HTTP_200_OK)

        if jornada_param:
            try:
                jornada_num = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)
            if jornada_num not in jornadas_disponibles:
                jornada_num = jornadas_disponibles[-1]
        else:
            jugadas = sorted(set(
                qs_partidos.filter(jugado=True).values_list("jornada_numero", flat=True).distinct()
            ))
            if jugadas:
                jornada_num = jugadas[-1]
            else:
                jornada_num = jornadas_disponibles[-1]

        clasif_lookup = self._get_clasif_lookup(grupo)
        coef_lookup = self._get_coef_lookup()

        acumulado: dict[int, dict] = {}
        puntos_jornada_actual: dict[int, int] = {}

        for j in jornadas_disponibles:
            if j > jornada_num:
                break
            partidos_j = list(qs_partidos.filter(jornada_numero=j).order_by("id"))
            ranking_jornada_j: dict[int, dict] = {}
            for p in partidos_j:
                if not p.jugado:
                    continue
                puntos_partido = self._calcular_puntos_de_jornada(p, clasif_lookup, coef_lookup)
                for jid, data in puntos_partido.items():
                    if jid not in ranking_jornada_j:
                        ranking_jornada_j[jid] = data.copy()
                    else:
                        ranking_jornada_j[jid]["puntos"] += data["puntos"]

            for jid, data in ranking_jornada_j.items():
                if jid not in acumulado:
                    acumulado[jid] = {
                        "jugador_id": jid,
                        "nombre": data["nombre"],
                        "foto": data["foto"],
                        "club_id": data["club_id"],
                        "club_nombre": data["club_nombre"],
                        "club_escudo": data["club_escudo"],
                        "puntos_acumulados": data["puntos"],
                        "es_portero": data.get("es_portero", False),
                    }
                else:
                    acumulado[jid]["puntos_acumulados"] += data["puntos"]
                if j == jornada_num:
                    puntos_jornada_actual[jid] = data["puntos"]

        ranking_actual = list(acumulado.values())
        if only_porteros:
            ranking_actual = [r for r in ranking_actual if r.get("es_portero")]

        ranking_actual.sort(key=lambda x: x["puntos_acumulados"], reverse=True)

        for idx, row in enumerate(ranking_actual, start=1):
            jid = row["jugador_id"]
            row["posicion"] = idx
            row["puntos_jornada"] = puntos_jornada_actual.get(jid, 0)

        prev_ranking = []
        if jornada_num > min(jornadas_disponibles):
            prev_jornada_num = max([j for j in jornadas_disponibles if j < jornada_num])
            prev_acumulado: dict[int, dict] = {}
            for j in jornadas_disponibles:
                if j > prev_jornada_num:
                    break
                partidos_j = list(qs_partidos.filter(jornada_numero=j).order_by("id"))
                ranking_jornada_j: dict[int, dict] = {}
                for p in partidos_j:
                    if not p.jugado:
                        continue
                    puntos_partido = self._calcular_puntos_de_jornada(p, clasif_lookup, coef_lookup)
                    for jid, data in puntos_partido.items():
                        if jid not in ranking_jornada_j:
                            ranking_jornada_j[jid] = data.copy()
                        else:
                            ranking_jornada_j[jid]["puntos"] += data["puntos"]
                for jid, data in ranking_jornada_j.items():
                    if jid not in prev_acumulado:
                        prev_acumulado[jid] = {"jugador_id": jid, "puntos_acumulados": data["puntos"]}
                    else:
                        prev_acumulado[jid]["puntos_acumulados"] += data["puntos"]

            prev_ranking = list(prev_acumulado.values())
            if only_porteros:
                porter_ids = {r["jugador_id"] for r in ranking_actual}
                prev_ranking = [r for r in prev_ranking if r["jugador_id"] in porter_ids]
            prev_ranking.sort(key=lambda x: x["puntos_acumulados"], reverse=True)
            for idx, row in enumerate(prev_ranking, start=1):
                row["posicion"] = idx

        for row in ranking_actual:
            row["foto"] = self._abs_media(request, row.get("foto", ""))
            row["club_escudo"] = self._abs_media(request, row.get("club_escudo", ""))

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": grupo.temporada.nombre,
            },
            "jornada_aplicada": jornada_num,
            "jornadas_disponibles": jornadas_disponibles,
            "ranking": ranking_actual,
            "prev_ranking": prev_ranking,
        }
        return Response(payload, status=status.HTTP_200_OK)


# ===================== EQUIPO DE LA JORNADA — GLOBAL =====================
class EquipoJornadaGlobalView(APIView):
    """
    GET /api/valoraciones/equipo-jornada-global/?temporada_id=4&top=20
    Opcionales: weekend, date_from/date_to, strict, min_matches
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    MIN_TOTAL_MATCHES = 10
    MAX_WEEKS_LOOKBACK = 20

    def _bonus_rival_fuerte(self, coef_rival: float) -> float:
        if coef_rival >= 0.8:
            return 0.35
        if coef_rival >= 0.6:
            return 0.20
        if coef_rival >= 0.4:
            return 0.10
        return 0.0

    def _bonus_diferencia(self, dif_goles: int) -> float:
        if dif_goles >= 3:
            return 0.35
        if dif_goles == 2:
            return 0.20
        if dif_goles == 1:
            return 0.10
        return 0.0

    def _penalizacion_rival_debil(self, pos_rival: int | None) -> float:
        if not pos_rival:
            return 0.0
        return -0.15 if pos_rival >= 14 else 0.0

    def _bonus_rompe_racha(self, racha_rival: str | None) -> float:
        if not racha_rival:
            return 0.0
        r = racha_rival.strip().upper()
        streak_v = 0
        for ch in r:
            if ch == "V":
                streak_v += 1
            else:
                break
        return 0.15 if streak_v >= 3 else 0.0

    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _wed_sun_window_from_date(self, d):
        from datetime import datetime, time, timedelta
        from django.utils import timezone
        monday = d - timedelta(days=d.weekday())
        wednesday = monday + timedelta(days=2)
        sunday = monday + timedelta(days=6)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(wednesday, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(sunday, time(21, 0, 0)), tz)
        return start, end

    def _detect_last_window(self, temporada_id: int):
        from django.utils import timezone
        p = (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True)
            .order_by("-fecha_hora")
            .first()
        )
        if not p:
            return None, None
        ref_d = p.fecha_hora.astimezone(timezone.get_current_timezone()).date()
        return self._wed_sun_window_from_date(ref_d)

    def _compute_window(self, request, temporada_id: int):
        from datetime import datetime, time
        from django.utils import timezone
        dfrom = self._parse_date(request.GET.get("date_from"))
        dto = self._parse_date(request.GET.get("date_to"))
        if dfrom and dto:
            tz = timezone.get_current_timezone()
            start = timezone.make_aware(datetime.combine(dfrom, time.min), tz)
            end = timezone.make_aware(datetime.combine(dto, time.max), tz)
            return start, end, {
                "start": dfrom.isoformat(),
                "end": dto.isoformat(),
                "mode": "custom_range",
                "schema": "free"
            }
        w = self._parse_date(request.GET.get("weekend"))
        if w:
            start, end = self._wed_sun_window_from_date(w)
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "week_param",
                "schema": "wed19-sun21"
            }
        start, end = self._detect_last_window(temporada_id)
        if start and end:
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "auto_last_week",
                "schema": "wed19-sun21"
            }
        return None, None, {"start": None, "end": None, "mode": "empty", "schema": "wed19-sun21"}

    def _count_partidos_in_window(self, temporada_id: int, start_dt, end_dt) -> int:
        return (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            .count()
        )

    def _shift_window_back_one_week(self, start_dt, end_dt):
        from datetime import timedelta
        return start_dt - timedelta(days=7), end_dt - timedelta(days=7)

    def _find_valid_window_with_min(self, temporada_id: int, start_dt, end_dt, min_required: int):
        s, e = start_dt, end_dt
        for i in range(self.MAX_WEEKS_LOOKBACK + 1):
            matched = self._count_partidos_in_window(temporada_id, s, e)
            if matched >= min_required:
                return s, e, True, i, matched
            s, e = self._shift_window_back_one_week(s, e)
        return start_dt, end_dt, False, self.MAX_WEEKS_LOOKBACK, 0

    def get(self, request, format=None):
        from django.utils import timezone
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        try:
            top_n = int(request.GET.get("top", "30"))
        except ValueError:
            top_n = 30
        strict = _get_bool(request, "strict", False)
        min_matches = _get_int(request, "min_matches", self.MIN_TOTAL_MATCHES)
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        coef_club = _coef_club_lookup(temporada_id, self.JORNADA_REF_COEF)

        start_dt, end_dt, window_meta = self._compute_window(request, temporada_id)
        if not start_dt or not end_dt:
            return Response({
                "temporada_id": temporada_id,
                "window": {**window_meta, "status": "no-window"},
                "equipo_de_la_jornada_global": None,
                "ranking_global": [],
                "detail": "No hay partidos jugados para determinar ventana temporal."
            }, status=status.HTTP_200_OK)

        if strict:
            matched = self._count_partidos_in_window(temporada_id, start_dt, end_dt)
            window_meta = {
                **window_meta,
                "status": "strict",
                "matched_games": matched,
                "min_required": min_matches,
                "effective_start": start_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": end_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
        else:
            valid_s, valid_e, ok, tries, matched = self._find_valid_window_with_min(
                temporada_id, start_dt, end_dt, min_matches
            )
            window_meta = {
                **window_meta,
                "status": "ok" if ok else "fallback_failed",
                "matched_games": matched,
                "min_required": min_matches,
                "fallback_weeks": tries,
                "effective_start": valid_s.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": valid_e.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
            if not ok:
                return Response({
                    "temporada_id": temporada_id,
                    "window": window_meta,
                    "equipo_de_la_jornada_global": None,
                    "ranking_global": [],
                    "detail": "No hay una ventana con partidos suficientes (umbral) en el histórico reciente."
                }, status=status.HTTP_200_OK)
            start_dt, end_dt = valid_s, valid_e

        grupos = list(
            Grupo.objects
            .select_related("competicion", "temporada")
            .filter(temporada_id=temporada_id)
            .order_by("competicion__nombre", "nombre")
        )

        agregados = []
        for g in grupos:
            qs_partidos = (
                Partido.objects
                .filter(grupo=g, jugado=True, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
                .select_related("local", "visitante")
                .order_by("fecha_hora", "id")
            )
            partidos_j = list(qs_partidos)
            if not partidos_j:
                continue

            clasif_rows = (
                ClubEnGrupo.objects
                .filter(grupo=g)
                .select_related("club")
            )
            clasif_lookup = {
                c.club_id: {
                    "pos": c.posicion_actual,
                    "racha": (c.racha or "").strip().upper(),
                    "escudo": _norm_media(c.club.escudo_url or ""),
                    "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }
                for c in clasif_rows
            }

            ranking_clubes: dict[int, dict] = {}
            for p in partidos_j:
                gl = p.goles_local or 0
                gv = p.goles_visitante or 0
                lid = p.local_id
                vid = p.visitante_id

                base_local = 1.0 if gl > gv else (0.4 if gl == gv else 0.0)
                score_local = (
                    base_local +
                    self._bonus_rival_fuerte(coef_club.get(vid, 0.5)) +
                    self._bonus_diferencia(gl - gv) +
                    self._bonus_rompe_racha(clasif_lookup.get(vid, {}).get("racha")) +
                    self._penalizacion_rival_debil(clasif_lookup.get(vid, {}).get("pos"))
                )
                score_local *= (0.9 + coef_club.get(lid, 0.5))

                if lid not in ranking_clubes:
                    ranking_clubes[lid] = {
                        "club_id": lid,
                        "nombre": clasif_lookup.get(lid, {}).get("nombre", p.local.nombre_corto or p.local.nombre_oficial),
                        "escudo": clasif_lookup.get(lid, {}).get("escudo", _norm_media(p.local.escudo_url or "")),
                        "score": 0.0,
                        "grupo_id": g.id,
                        "grupo_nombre": g.nombre,
                        "competicion_id": g.competicion_id,
                        "competicion_nombre": g.competicion.nombre,
                    }
                ranking_clubes[lid]["score"] += round(score_local, 4)

                base_visit = 1.0 if gv > gl else (0.4 if gv == gl else 0.0)
                bonus_fuera = 0.25 if gv > gl else 0.0
                score_visit = (
                    base_visit +
                    self._bonus_rival_fuerte(coef_club.get(lid, 0.5)) +
                    self._bonus_diferencia(gv - gl) +
                    self._bonus_rompe_racha(clasif_lookup.get(lid, {}).get("racha")) +
                    self._penalizacion_rival_debil(clasif_lookup.get(lid, {}).get("pos")) +
                    bonus_fuera
                )
                score_visit *= (0.9 + coef_club.get(vid, 0.5))

                if vid not in ranking_clubes:
                    ranking_clubes[vid] = {
                        "club_id": vid,
                        "nombre": clasif_lookup.get(vid, {}).get("nombre", p.visitante.nombre_corto or p.visitante.nombre_oficial),
                        "escudo": clasif_lookup.get(vid, {}).get("escudo", _norm_media(p.visitante.escudo_url or "")),
                        "score": 0.0,
                        "grupo_id": g.id,
                        "grupo_nombre": g.nombre,
                        "competicion_id": g.competicion_id,
                        "competicion_nombre": g.competicion.nombre,
                    }
                ranking_clubes[vid]["score"] += round(score_visit, 4)

            if not ranking_clubes:
                continue

            coef_div = float(coef_division.get(g.competicion_id, 1.0))
            for r in ranking_clubes.values():
                agregados.append({
                    **r,
                    "score_global": round(r["score"] * coef_div, 4),
                    "coef_division": coef_div,
                })

        agregados.sort(key=lambda x: (-x["score_global"], -x["score"], x["nombre"].lower()))
        if top_n > 0:
            agregados = agregados[:top_n]

        for row in agregados:
            row["escudo"] = _abs_media(request, row.get("escudo", ""))

        payload = {
            "temporada_id": temporada_id,
            "window": window_meta,
            "equipo_de_la_jornada_global": agregados[0] if agregados else None,
            "ranking_global": agregados,
        }
        return Response(payload, status=status.HTTP_200_OK)


# ===================== JUGADORES DE LA JORNADA — GLOBAL =====================
class JugadoresJornadaGlobalView(APIView):
    """
    GET /api/valoraciones/jugadores-jornada-global/?temporada_id=4&only_porteros=0&top=50
    Opcionales: weekend, date_from/date_to, strict, min_matches
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    MIN_TOTAL_MATCHES = 10
    MAX_WEEKS_LOOKBACK = 20

    def _puntos_presencia(self, titular: bool) -> float:
        return 3.0 if titular else 1.0

    def _puntos_evento(self, t: str) -> float:
        return {
            "gol": 3.0,
            "gol_pp": -2.0,
            "amarilla": -1.0,
            "doble_amarilla": -3.0,
            "roja": -5.0,
            "mvp": 3.0,
        }.get(t, 0.0)

    def _es_portero(self, jug: Jugador | None, al: AlineacionPartidoJugador | None) -> bool:
        if al and al.etiqueta and al.etiqueta.lower().startswith("pt"):
            return True
        if jug and jug.posicion_principal == "portero":
            return True
        return False

    def _bonus_resultado(self, p: Partido, club_id: int | None, gl: int, gv: int) -> float:
        if club_id is None:
            return 0.0
        if p.local_id == club_id:
            return 2.0 if gl > gv else (1.0 if gl == gv else 0.0)
        return 2.0 if gv > gl else (1.0 if gv == gl else 0.0)

    def _bonus_rival_fuerte(self, p: Partido, club_id: int | None, coef_club: dict) -> float:
        if club_id is None:
            return 0.0
        rival_id = p.visitante_id if p.local_id == club_id else p.local_id
        coef_rival = coef_club.get(rival_id, 0.5)
        gl = p.goles_local or 0
        gv = p.goles_visitante or 0
        gano_empato = (gl >= gv) if p.local_id == club_id else (gv >= gl)
        if not gano_empato:
            return 0.0
        if coef_rival >= 0.8:
            return 1.0
        if coef_rival >= 0.6:
            return 0.5
        return 0.0

    def _bonus_duelo_fuertes(self, p: Partido, coef_club: dict) -> float:
        cl = coef_club.get(p.local_id, 0.5)
        cv = coef_club.get(p.visitante_id, 0.5)
        if cl >= 0.8 and cv >= 0.8:
            return 1.0
        if cl >= 0.6 and cv >= 0.6:
            return 0.5
        return 0.0

    def _bonus_intensidad(self, p: Partido) -> float:
        if p.indice_intensidad is None:
            return 0.0
        if p.indice_intensidad >= 90:
            return 1.0
        if p.indice_intensidad >= 80:
            return 0.5
        return 0.0

    def _penal_goles_encajados(self, goles: int) -> float:
        if goles <= 2:
            return 0.0
        return float(-(goles - 2))

    def _extra_portero_gol(self, n: int) -> float:
        if n <= 0:
            return 0.0
        if n == 1:
            return 5.0
        if n == 2:
            return 12.0
        return 20.0

    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _wed_sun_window_from_date(self, d):
        from datetime import datetime, time, timedelta
        from django.utils import timezone
        monday = d - timedelta(days=d.weekday())
        wednesday = monday + timedelta(days=2)
        sunday = monday + timedelta(days=6)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(wednesday, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(sunday, time(21, 0, 0)), tz)
        return start, end

    def _detect_last_window(self, temporada_id: int):
        from django.utils import timezone
        p = (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True)
            .order_by("-fecha_hora")
            .first()
        )
        if not p:
            return None, None
        ref_d = p.fecha_hora.astimezone(timezone.get_current_timezone()).date()
        return self._wed_sun_window_from_date(ref_d)

    def _compute_window(self, request, temporada_id: int):
        from datetime import datetime, time
        from django.utils import timezone
        dfrom = self._parse_date(request.GET.get("date_from"))
        dto = self._parse_date(request.GET.get("date_to"))
        if dfrom and dto:
            tz = timezone.get_current_timezone()
            start = timezone.make_aware(datetime.combine(dfrom, time.min), tz)
            end = timezone.make_aware(datetime.combine(dto, time.max), tz)
            return start, end, {
                "start": dfrom.isoformat(),
                "end": dto.isoformat(),
                "mode": "custom_range",
                "schema": "free"
            }
        w = self._parse_date(request.GET.get("weekend"))
        if w:
            start, end = self._wed_sun_window_from_date(w)
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "week_param",
                "schema": "wed19-sun21"
            }
        start, end = self._detect_last_window(temporada_id)
        if start and end:
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "auto_last_week",
                "schema": "wed19-sun21"
            }
        return None, None, {"start": None, "end": None, "mode": "empty", "schema": "wed19-sun21"}

    def _count_partidos_in_window(self, temporada_id: int, start_dt, end_dt) -> int:
        return (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            .count()
        )

    def _shift_window_back_one_week(self, start_dt, end_dt):
        from datetime import timedelta
        return start_dt - timedelta(days=7), end_dt - timedelta(days=7)

    def _find_valid_window_with_min(self, temporada_id: int, start_dt, end_dt, min_required: int):
        s, e = start_dt, end_dt
        for i in range(self.MAX_WEEKS_LOOKBACK + 1):
            matched = self._count_partidos_in_window(temporada_id, s, e)
            if matched >= min_required:
                return s, e, True, i, matched
            s, e = self._shift_window_back_one_week(s, e)
        return start_dt, end_dt, False, self.MAX_WEEKS_LOOKBACK, 0

    def get(self, request, format=None):
        from django.utils import timezone
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        only_porteros = request.GET.get("only_porteros") in ["1", "true", "True"]
        try:
            top_n = int(request.GET.get("top", "50"))
        except ValueError:
            top_n = 50
        strict = _get_bool(request, "strict", False)
        min_matches = _get_int(request, "min_matches", self.MIN_TOTAL_MATCHES)
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        coef_club = _coef_club_lookup(temporada_id, self.JORNADA_REF_COEF)

        start_dt, end_dt, window_meta = self._compute_window(request, temporada_id)
        if not start_dt or not end_dt:
            return Response({
                "temporada_id": temporada_id,
                "window": {**window_meta, "status": "no-window"},
                "jugador_de_la_jornada_global": None,
                "ranking_global": [],
                "detail": "No hay partidos jugados para determinar ventana temporal."
            }, status=status.HTTP_200_OK)

        if strict:
            matched = self._count_partidos_in_window(temporada_id, start_dt, end_dt)
            window_meta = {
                **window_meta,
                "status": "strict",
                "matched_games": matched,
                "min_required": min_matches,
                "effective_start": start_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": end_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
        else:
            valid_s, valid_e, ok, tries, matched = self._find_valid_window_with_min(
                temporada_id, start_dt, end_dt, min_matches
            )
            window_meta = {
                **window_meta,
                "status": "ok" if ok else "fallback_failed",
                "matched_games": matched,
                "min_required": min_matches,
                "fallback_weeks": tries,
                "effective_start": valid_s.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": valid_e.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
            if not ok:
                return Response({
                    "temporada_id": temporada_id,
                    "window": window_meta,
                    "jugador_de_la_jornada_global": None,
                    "ranking_global": [],
                    "detail": "No hay una ventana con partidos suficientes (umbral) en el histórico reciente."
                }, status=status.HTTP_200_OK)
            start_dt, end_dt = valid_s, valid_e

        grupos = list(
            Grupo.objects
            .select_related("competicion", "temporada")
            .filter(temporada_id=temporada_id)
        )

        ranking_global = []
        for g in grupos:
            qs_partidos = (
                Partido.objects
                .filter(grupo=g, jugado=True, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
                .select_related("local", "visitante")
                .prefetch_related("eventos", "alineaciones_jugadores")
                .order_by("fecha_hora", "id")
            )
            partidos_j = list(qs_partidos)
            if not partidos_j:
                continue

            clasif_rows = (
                ClubEnGrupo.objects
                .filter(grupo=g)
                .select_related("club")
            )
            club_info = {
                c.club_id: {
                    "escudo": _norm_media(c.club.escudo_url or ""),
                    "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }
                for c in clasif_rows
            }

            ranking_jornada: dict[int, dict] = {}
            for p in partidos_j:
                gl = p.goles_local or 0
                gv = p.goles_visitante or 0
                bonus_df = self._bonus_duelo_fuertes(p, coef_club)
                bonus_int = self._bonus_intensidad(p)
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
                    es_gk = self._es_portero(jug, al)
                    if jid not in ranking_jornada:
                        info = club_info.get(cid or 0, {})
                        ranking_jornada[jid] = {
                            "jugador_id": jid,
                            "nombre": jug.apodo or jug.nombre,
                            "foto": _norm_media(jug.foto_url or ""),
                            "club_id": cid,
                            "club_nombre": info.get("nombre", ""),
                            "club_escudo": info.get("escudo", ""),
                            "puntos": 0.0,
                            "es_portero": es_gk,
                            "goles_jornada": 0,
                        }
                    else:
                        if es_gk:
                            ranking_jornada[jid]["es_portero"] = True
                    ranking_jornada[jid]["puntos"] += self._puntos_presencia(al.titular)
                    pr = self._bonus_resultado(p, cid, gl, gv)
                    if pr:
                        ranking_jornada[jid]["puntos"] += pr
                    brf = self._bonus_rival_fuerte(p, cid, coef_club)
                    if brf:
                        ranking_jornada[jid]["puntos"] += brf
                    if bonus_df:
                        ranking_jornada[jid]["puntos"] += bonus_df
                    if bonus_int:
                        ranking_jornada[jid]["puntos"] += bonus_int

                # 2) Eventos
                for ev in eventos:
                    if not ev.jugador_id:
                        continue
                    jid = ev.jugador_id
                    jug = ev.jugador
                    al_ev = al_por_j.get(jid)
                    es_gk = self._es_portero(jug, al_ev)
                    if jid not in ranking_jornada:
                        cid = ev.club_id
                        info = club_info.get(cid or 0, {})
                        ranking_jornada[jid] = {
                            "jugador_id": jid,
                            "nombre": (jug.apodo or jug.nombre) if jug else f"Jugador {jid}",
                            "foto": _norm_media(jug.foto_url) if jug else "",
                            "club_id": cid,
                            "club_nombre": info.get("nombre", ""),
                            "club_escudo": info.get("escudo", ""),
                            "puntos": 0.0,
                            "es_portero": es_gk,
                            "goles_jornada": 0,
                        }
                    else:
                        if es_gk:
                            ranking_jornada[jid]["es_portero"] = True
                    pts_ev = self._puntos_evento(ev.tipo_evento)
                    if pts_ev:
                        ranking_jornada[jid]["puntos"] += pts_ev
                    if ev.tipo_evento == "gol":
                        ranking_jornada[jid]["goles_jornada"] = ranking_jornada[jid].get("goles_jornada", 0) + 1

                # 3) Porteros: goles encajados + portería seria
                g_rec_local, g_rec_visit = gv, gl
                ports_local = [al for al in alineaciones if al.club_id == p.local_id and self._es_portero(al.jugador, al)]
                ports_visit = [al for al in alineaciones if al.club_id == p.visitante_id and self._es_portero(al.jugador, al)]

                if ports_local:
                    pen = self._penal_goles_encajados(g_rec_local)
                    for al in ports_local:
                        if al.jugador_id in ranking_jornada and pen:
                            ranking_jornada[al.jugador_id]["puntos"] += pen
                    if gl > gv and gv <= 1:
                        for al in ports_local:
                            if al.jugador_id in ranking_jornada:
                                ranking_jornada[al.jugador_id]["puntos"] += 1.0

                if ports_visit:
                    pen = self._penal_goles_encajados(g_rec_visit)
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
                    if not self._es_portero(jug_ev, al_ev):
                        continue
                    goles_gk = len([e for e in eventos if e.jugador_id == ev.jugador_id and e.tipo_evento == "gol"])
                    ranking_jornada[ev.jugador_id]["puntos"] += self._extra_portero_gol(goles_gk)

            if not ranking_jornada:
                continue

            rows = []
            for d in ranking_jornada.values():
                d["puntos"] = ceil(d["puntos"])
                if only_porteros and not d.get("es_portero"):
                    continue
                rows.append(d)

            coef_div = float(coef_division.get(g.competicion_id, 1.0))
            for r in rows:
                ranking_global.append({
                    **r,
                    "grupo_id": g.id,
                    "grupo_nombre": g.nombre,
                    "competicion_id": g.competicion_id,
                    "competicion_nombre": g.competicion.nombre,
                    "puntos_global": int(round(r["puntos"] * coef_div)),
                    "coef_division": coef_div,
                    "goles_jornada": r.get("goles_jornada", 0),
                })

        ranking_global.sort(key=lambda x: (-x["puntos_global"], -x["puntos"], x["nombre"].lower()))
        if top_n > 0:
            ranking_global = ranking_global[:top_n]

        for row in ranking_global:
            row["foto"] = _abs_media(request, row.get("foto", ""))
            row["club_escudo"] = _abs_media(request, row.get("club_escudo", ""))

        payload = {
            "temporada_id": temporada_id,
            "window": window_meta,
            "jugador_de_la_jornada_global": ranking_global[0] if ranking_global else None,
            "ranking_global": ranking_global,
        }
        return Response(payload, status=status.HTTP_200_OK)


# ===================== PARTIDOS TOP GLOBAL =====================
class PartidosTopGlobalView(APIView):
    """
    GET /api/valoraciones/partidos-top-global/?temporada_id=4&top=3
    Opcionales: weekend, date_from/date_to, strict, min_matches
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    MIN_TOTAL_MATCHES = 10
    MAX_WEEKS_LOOKBACK = 20

    def _bonus_racha(self, racha_texto: str) -> float:
        if not racha_texto:
            return 0.0
        r = racha_texto.strip().upper()[:5]
        total = 0.0
        for ch in r:
            if ch == "V":
                total += 0.05
            elif ch == "E":
                total += 0.02
            elif ch == "D":
                total -= 0.03
        return total

    def _bonus_goles(self, goles_local: int, goles_visit: int) -> float:
        gl = goles_local or 0
        gv = goles_visit or 0
        if gl >= 35 and gv >= 35:
            return 0.12
        if gl >= 25 and gv >= 25:
            return 0.08
        if gl >= 25 or gv >= 25:
            return 0.04
        return 0.0

    def _penalizacion_desigual(self, pos_local, pos_visit) -> float:
        if not pos_local or not pos_visit:
            return 0.0
        diff = abs(pos_local - pos_visit)
        pen = 0.0
        if diff >= 10:
            pen -= 0.15
        elif diff >= 8:
            pen -= 0.10
        elif diff >= 6:
            pen -= 0.06
        top3 = pos_local <= 3 or pos_visit <= 3
        descenso = pos_local >= 15 or pos_visit >= 15
        if top3 and descenso:
            pen -= 0.05
        return pen

    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _wed_sun_window_from_date(self, d):
        from datetime import datetime, time, timedelta
        from django.utils import timezone
        monday = d - timedelta(days=d.weekday())
        wednesday = monday + timedelta(days=2)
        sunday = monday + timedelta(days=6)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(wednesday, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(sunday, time(21, 0, 0)), tz)
        return start, end

    def _detect_last_window(self, temporada_id: int):
        from django.utils import timezone
        p = (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id)
            .order_by("-fecha_hora")
            .first()
        )
        if not p:
            return None, None
        ref_d = p.fecha_hora.astimezone(timezone.get_current_timezone()).date()
        return self._wed_sun_window_from_date(ref_d)

    def _compute_window(self, request, temporada_id: int):
        from datetime import datetime, time
        from django.utils import timezone
        dfrom = self._parse_date(request.GET.get("date_from"))
        dto = self._parse_date(request.GET.get("date_to"))
        if dfrom and dto:
            tz = timezone.get_current_timezone()
            start = timezone.make_aware(datetime.combine(dfrom, time.min), tz)
            end = timezone.make_aware(datetime.combine(dto, time.max), tz)
            return start, end, {
                "start": dfrom.isoformat(),
                "end": dto.isoformat(),
                "mode": "custom_range",
                "schema": "free"
            }
        w = self._parse_date(request.GET.get("weekend"))
        if w:
            start, end = self._wed_sun_window_from_date(w)
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "week_param",
                "schema": "wed19-sun21"
            }
        start, end = self._detect_last_window(temporada_id)
        if start and end:
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "auto_last_week",
                "schema": "wed19-sun21"
            }
        return None, None, {"start": None, "end": None, "mode": "empty", "schema": "wed19-sun21"}

    def _count_partidos_in_window(self, temporada_id: int, start_dt, end_dt) -> int:
        return (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            .count()
        )

    def _shift_window_back_one_week(self, start_dt, end_dt):
        from datetime import timedelta
        return start_dt - timedelta(days=7), end_dt - timedelta(days=7)

    def _find_valid_window_with_min(self, temporada_id: int, start_dt, end_dt, min_required: int):
        s, e = start_dt, end_dt
        for i in range(self.MAX_WEEKS_LOOKBACK + 1):
            matched = self._count_partidos_in_window(temporada_id, s, e)
            if matched >= min_required:
                return s, e, True, i, matched
            s, e = self._shift_window_back_one_week(s, e)
        return start_dt, end_dt, False, self.MAX_WEEKS_LOOKBACK, 0

    def get(self, request, format=None):
        from django.utils import timezone
        from arbitros.models import ArbitrajePartido
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        try:
            top_n = int(request.GET.get("top", "3"))
        except ValueError:
            top_n = 3
        strict = _get_bool(request, "strict", False)
        min_matches = _get_int(request, "min_matches", self.MIN_TOTAL_MATCHES)
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        coef_club = _coef_club_lookup(temporada_id, self.JORNADA_REF_COEF)

        start_dt, end_dt, window_meta = self._compute_window(request, temporada_id)
        if not start_dt or not end_dt:
            return Response({
                "temporada_id": temporada_id,
                "window": {**window_meta, "status": "no-window"},
                "top_matches": [],
                "ranking_partidos": [],
                "detail": "No hay ventana temporal válida."
            }, status=status.HTTP_200_OK)

        if strict:
            matched = self._count_partidos_in_window(temporada_id, start_dt, end_dt)
            window_meta = {
                **window_meta,
                "status": "strict",
                "matched_games": matched,
                "min_required": min_matches,
                "effective_start": start_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": end_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M")
            }
        else:
            valid_s, valid_e, ok, tries, matched = self._find_valid_window_with_min(
                temporada_id, start_dt, end_dt, min_matches
            )
            window_meta = {
                **window_meta,
                "status": "ok" if ok else "fallback_failed",
                "matched_games": matched,
                "min_required": min_matches,
                "fallback_weeks": tries,
                "effective_start": valid_s.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": valid_e.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M")
            }
            if not ok:
                return Response({
                    "temporada_id": temporada_id,
                    "window": window_meta,
                    "top_matches": [],
                    "ranking_partidos": [],
                    "detail": "No hay una ventana con partidos suficientes (umbral) en el histórico reciente."
                }, status=status.HTTP_200_OK)
            start_dt, end_dt = valid_s, valid_e

        partidos = list(
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
            .select_related("local", "visitante", "grupo", "grupo__competicion", "grupo__temporada")
            .order_by("fecha_hora", "id")
        )

        if not partidos:
            return Response({
                "temporada_id": temporada_id,
                "window": window_meta,
                "top_matches": [],
                "ranking_partidos": [],
            }, status=status.HTTP_200_OK)

        arbitrajes = (
            ArbitrajePartido.objects
            .filter(partido__in=partidos)
            .select_related("arbitro", "partido")
        )
        arbitros_por_partido = {}
        for arb in arbitrajes:
            pid = arb.partido_id
            arbitros_por_partido.setdefault(pid, [])
            if arb.arbitro and arb.arbitro.nombre:
                arbitros_por_partido[pid].append(arb.arbitro.nombre)

        clasif_cache, goles_cache = {}, {}

        def get_clasif(grupo):
            if grupo.id in clasif_cache:
                return clasif_cache[grupo.id]
            rows = ClubEnGrupo.objects.filter(grupo=grupo).select_related("club")
            lookup = {
                c.club_id: {
                    "pos": c.posicion_actual,
                    "racha": (c.racha or "").strip().upper(),
                    "escudo": _norm_media(c.club.escudo_url or ""),
                    "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }
                for c in rows
            }
            clasif_cache[grupo.id] = lookup
            return lookup

        def get_goles(grupo):
            if grupo.id in goles_cache:
                return goles_cache[grupo.id]
            jugados = (
                Partido.objects
                .filter(grupo=grupo, jugado=True, goles_local__isnull=False, goles_visitante__isnull=False)
                .values("local_id", "visitante_id", "goles_local", "goles_visitante")
            )
            goles = {}
            for p in jugados:
                lid = p["local_id"]
                vid = p["visitante_id"]
                gl = p["goles_local"] or 0
                gv = p["goles_visitante"] or 0
                goles[lid] = goles.get(lid, 0) + gl
                goles[vid] = goles.get(vid, 0) + gv
            goles_cache[grupo.id] = goles
            return goles

        ranking = []
        for p in partidos:
            g = p.grupo
            info = get_clasif(g)
            goles_temporada = get_goles(g)
            lid = p.local_id
            vid = p.visitante_id
            coef_local = float(coef_club.get(lid, 0.5))
            coef_visit = float(coef_club.get(vid, 0.5))
            base_score = coef_local + coef_visit
            pos_local = info.get(lid, {}).get("pos")
            pos_visit = info.get(vid, {}).get("pos")
            bonus_duelo = 0.0
            if pos_local and pos_visit:
                if {pos_local, pos_visit} == {1, 2}:
                    bonus_duelo += 0.25
                elif abs(pos_local - pos_visit) == 1 and max(pos_local, pos_visit) <= 4:
                    bonus_duelo += 0.15
                diff = abs(pos_local - pos_visit)
                if diff <= 2:
                    bonus_duelo += 0.08
                elif diff <= 4:
                    bonus_duelo += 0.04
            racha_local = info.get(lid, {}).get("racha", "")
            racha_visit = info.get(vid, {}).get("racha", "")
            bonus_r = self._bonus_racha(racha_local) + self._bonus_racha(racha_visit)
            gl_temp = goles_temporada.get(lid, 0)
            gv_temp = goles_temporada.get(vid, 0)
            bonus_goles = self._bonus_goles(gl_temp, gv_temp)
            penal = self._penalizacion_desigual(pos_local, pos_visit)
            score = base_score + bonus_duelo + bonus_r + bonus_goles + penal
            coef_div = float(coef_division.get(g.competicion_id, 1.0))
            score_global = round(score * coef_div, 4)

            gl = getattr(p, "goles_local", None)
            gv = getattr(p, "goles_visitante", None)
            jugado_flag = bool(getattr(p, "jugado", False))
            tiene_marcador = jugado_flag and gl is not None and gv is not None

            if tiene_marcador:
                if gl > gv:
                    ganador = "local"
                elif gv > gl:
                    ganador = "visitante"
                else:
                    ganador = "empate"
                resultado = {"gl": int(gl or 0), "gv": int(gv or 0), "texto": f"{int(gl or 0)}-{int(gv or 0)}", "ganador": ganador}
                estado = "finalizado"
            else:
                resultado = None
                estado = "programado"

            try:
                comp_logo = _abs_media(request, getattr(g.competicion, "logo_url", "") or "")
            except Exception:
                comp_logo = ""

            row = {
                "pk": p.id,
                "partido_id": getattr(p, "identificador_federacion", None) or p.id,
                "identificador_federacion": getattr(p, "identificador_federacion", None),
                "jornada_numero": getattr(p, "jornada_numero", None),
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "pabellon": p.pabellon or (p.local.pabellon if p.local else ""),
                "jugado": jugado_flag,
                "estado": estado,
                "resultado": resultado,
                "arbitros": arbitros_por_partido.get(p.id, []),
                "grupo": {
                    "id": g.id,
                    "nombre": g.nombre,
                    "competicion_id": g.competicion_id,
                    "competicion": g.competicion.nombre if g.competicion else "",
                },
                "competicion_nombre": g.competicion.nombre if g.competicion else "",
                "grupo_nombre": g.nombre,
                "competicion_logo": comp_logo,
                "local": {
                    "id": p.local.id if p.local else None,
                    "nombre": info.get(lid, {}).get("nombre", p.local.nombre_corto or p.local.nombre_oficial if p.local else ""),
                    "escudo": info.get(lid, {}).get("escudo", _norm_media(p.local.escudo_url or "")) if p.local else "",
                    "posicion": pos_local,
                    "coeficiente": coef_local,
                    "racha": racha_local,
                    "goles_temporada": gl_temp,
                    "goles": gl if gl is not None else None,
                },
                "visitante": {
                    "id": p.visitante.id if p.visitante else None,
                    "nombre": info.get(vid, {}).get("nombre", p.visitante.nombre_corto or p.visitante.nombre_oficial if p.visitante else ""),
                    "escudo": info.get(vid, {}).get("escudo", _norm_media(p.visitante.escudo_url or "")) if p.visitante else "",
                    "posicion": pos_visit,
                    "coeficiente": coef_visit,
                    "racha": racha_visit,
                    "goles_temporada": gv_temp,
                    "goles": gv if gv is not None else None,
                },
                "coef_division": coef_div,
                "score": round(score, 3),
                "score_global": score_global,
            }
            ranking.append(row)

        ranking.sort(key=lambda x: (-x["score_global"], -x["score"], x["fecha_hora"] or ""))

        for r in ranking:
            r["local"]["escudo"] = _abs_media(request, r["local"].get("escudo", ""))
            r["visitante"]["escudo"] = _abs_media(request, r["visitante"].get("escudo", ""))
            if r.get("competicion_logo"):
                r["competicion_logo"] = _abs_media(request, r["competicion_logo"])

        top_matches = ranking[:top_n] if top_n > 0 else ranking

        payload = {
            "temporada_id": temporada_id,
            "window": window_meta,
            "top_matches": top_matches,
            "ranking_partidos": ranking,
        }
        return Response(payload, status=status.HTTP_200_OK)


# ===================== MVP GLOBAL: acumulado temporada + puntos de la semana =====================
class MVPGlobalView(APIView):
    """
    GET /api/valoraciones/mvp-global/?from=YYYY-MM-DD&to=YYYY-MM-DD
    Params opcionales: temporada_id, only_porteros, top, weekend, date_from/date_to, strict, min_matches
    """
    TEMPORADA_ID_BASE = 4
    JORNADA_REF_COEF = 6
    MIN_TOTAL_MATCHES = 10
    MAX_WEEKS_LOOKBACK = 20

    def _puntos_presencia(self, titular: bool) -> float:
        return 3.0 if titular else 1.0

    def _puntos_evento(self, t: str) -> float:
        return {
            "gol": 3.0,
            "gol_pp": -2.0,
            "amarilla": -1.0,
            "doble_amarilla": -3.0,
            "roja": -5.0,
            "mvp": 3.0,
        }.get(t, 0.0)

    def _es_portero(self, jug: Jugador | None, al: AlineacionPartidoJugador | None) -> bool:
        if al and al.etiqueta and al.etiqueta.lower().startswith("pt"):
            return True
        if jug and jug.posicion_principal == "portero":
            return True
        return False

    def _bonus_resultado(self, p: Partido, club_id: int | None, gl: int, gv: int) -> float:
        if club_id is None:
            return 0.0
        if p.local_id == club_id:
            return 2.0 if gl > gv else (1.0 if gl == gv else 0.0)
        return 2.0 if gv > gl else (1.0 if gv == gl else 0.0)

    def _bonus_rival_fuerte(self, p: Partido, club_id: int | None, coef_club: dict) -> float:
        if club_id is None:
            return 0.0
        rival_id = p.visitante_id if p.local_id == club_id else p.local_id
        coef_rival = coef_club.get(rival_id, 0.5)
        gl = p.goles_local or 0
        gv = p.goles_visitante or 0
        gano_empato = (gl >= gv) if p.local_id == club_id else (gv >= gl)
        if not gano_empato:
            return 0.0
        if coef_rival >= 0.8:
            return 1.0
        if coef_rival >= 0.6:
            return 0.5
        return 0.0

    def _bonus_duelo_fuertes(self, p: Partido, coef_club: dict) -> float:
        cl = coef_club.get(p.local_id, 0.5)
        cv = coef_club.get(p.visitante_id, 0.5)
        if cl >= 0.8 and cv >= 0.8:
            return 1.0
        if cl >= 0.6 and cv >= 0.6:
            return 0.5
        return 0.0

    def _bonus_intensidad(self, p: Partido) -> float:
        if p.indice_intensidad is None:
            return 0.0
        if p.indice_intensidad >= 90:
            return 1.0
        if p.indice_intensidad >= 80:
            return 0.5
        return 0.0

    def _penal_goles_encajados(self, goles: int) -> float:
        if goles <= 2:
            return 0.0
        return float(-(goles - 2))

    def _extra_portero_gol(self, n: int) -> float:
        if n <= 0:
            return 0.0
        if n == 1:
            return 5.0
        if n == 2:
            return 12.0
        return 20.0

    def _parse_date(self, s: str | None):
        if not s:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _wed_sun_window_from_date(self, d):
        from datetime import datetime, time, timedelta
        from django.utils import timezone
        monday = d - timedelta(days=d.weekday())
        wednesday = monday + timedelta(days=2)
        sunday = monday + timedelta(days=6)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(wednesday, time(19, 0, 0)), tz)
        end = timezone.make_aware(datetime.combine(sunday, time(21, 0, 0)), tz)
        return start, end

    def _detect_last_window(self, temporada_id: int):
        from django.utils import timezone
        p = (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True)
            .order_by("-fecha_hora")
            .first()
        )
        if not p:
            return None, None
        ref_d = p.fecha_hora.astimezone(timezone.get_current_timezone()).date()
        return self._wed_sun_window_from_date(ref_d)

    def _compute_window(self, request, temporada_id: int):
        from datetime import datetime, time
        from django.utils import timezone
        dfrom = self._parse_date(request.GET.get("from")) or self._parse_date(request.GET.get("date_from"))
        dto = self._parse_date(request.GET.get("to")) or self._parse_date(request.GET.get("date_to"))
        if dfrom and dto:
            tz = timezone.get_current_timezone()
            start = timezone.make_aware(datetime.combine(dfrom, time.min), tz)
            end = timezone.make_aware(datetime.combine(dto, time.max), tz)
            return start, end, {
                "start": dfrom.isoformat(),
                "end": dto.isoformat(),
                "mode": "from_to",
                "schema": "free",
            }
        w = self._parse_date(request.GET.get("weekend"))
        if w:
            start, end = self._wed_sun_window_from_date(w)
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "week_param",
                "schema": "wed19-sun21",
            }
        start, end = self._detect_last_window(temporada_id)
        if start and end:
            return start, end, {
                "start": start.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "end": end.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "mode": "auto_last_week",
                "schema": "wed19-sun21",
            }
        return None, None, {"start": None, "end": None, "mode": "empty", "schema": "wed19-sun21"}

    def _count_partidos_in_window(self, temporada_id: int, start_dt, end_dt) -> int:
        return (
            Partido.objects
            .filter(
                grupo__temporada_id=temporada_id,
                jugado=True,
                fecha_hora__gte=start_dt,
                fecha_hora__lte=end_dt,
            )
            .count()
        )

    def _shift_window_back_one_week(self, start_dt, end_dt):
        from datetime import timedelta
        return start_dt - timedelta(days=7), end_dt - timedelta(days=7)

    def _find_valid_window_with_min(self, temporada_id: int, start_dt, end_dt, min_required: int):
        s, e = start_dt, end_dt
        for i in range(self.MAX_WEEKS_LOOKBACK + 1):
            matched = self._count_partidos_in_window(temporada_id, s, e)
            if matched >= min_required:
                return s, e, True, i, matched
            s, e = self._shift_window_back_one_week(s, e)
        return start_dt, end_dt, False, self.MAX_WEEKS_LOOKBACK, 0

    def _compute_ranking_for_range(
        self,
        temporada_id: int,
        start_dt,
        end_dt,
        only_porteros: bool,
        coef_division: dict,
        coef_club: dict,
    ):
        ranking_global = []
        grupos = (
            Grupo.objects
            .select_related("competicion", "temporada")
            .filter(temporada_id=temporada_id)
        )
        for g in grupos:
            qs_partidos = (
                Partido.objects
                .filter(grupo=g, jugado=True, fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)
                .select_related("local", "visitante")
                .prefetch_related("eventos", "alineaciones_jugadores")
                .order_by("fecha_hora", "id")
            )
            partidos_j = list(qs_partidos)
            if not partidos_j:
                continue

            clasif_rows = (
                ClubEnGrupo.objects
                .filter(grupo=g)
                .select_related("club")
            )
            club_info = {
                c.club_id: {
                    "escudo": _norm_media(c.club.escudo_url or ""),
                    "nombre": c.club.nombre_corto or c.club.nombre_oficial,
                }
                for c in clasif_rows
            }

            ranking_jornada: dict[int, dict] = {}
            for p in partidos_j:
                gl = p.goles_local or 0
                gv = p.goles_visitante or 0
                bonus_df = self._bonus_duelo_fuertes(p, coef_club)
                bonus_int = self._bonus_intensidad(p)
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
                    es_gk = self._es_portero(jug, al)
                    if jid not in ranking_jornada:
                        info = club_info.get(cid or 0, {})
                        ranking_jornada[jid] = {
                            "jugador_id": jid,
                            "nombre": jug.apodo or jug.nombre,
                            "foto": _norm_media(jug.foto_url or ""),
                            "club_id": cid,
                            "club_nombre": info.get("nombre", ""),
                            "club_escudo": info.get("escudo", ""),
                            "puntos": 0.0,
                            "es_portero": es_gk,
                            "goles_jornada": 0,
                        }
                    else:
                        if es_gk:
                            ranking_jornada[jid]["es_portero"] = True
                    ranking_jornada[jid]["puntos"] += self._puntos_presencia(al.titular)
                    pr = self._bonus_resultado(p, cid, gl, gv)
                    if pr:
                        ranking_jornada[jid]["puntos"] += pr
                    brf = self._bonus_rival_fuerte(p, cid, coef_club)
                    if brf:
                        ranking_jornada[jid]["puntos"] += brf
                    if bonus_df:
                        ranking_jornada[jid]["puntos"] += bonus_df
                    if bonus_int:
                        ranking_jornada[jid]["puntos"] += bonus_int

                # 2) Eventos
                for ev in eventos:
                    if not ev.jugador_id:
                        continue
                    jid = ev.jugador_id
                    jug = ev.jugador
                    al_ev = al_por_j.get(jid)
                    es_gk = self._es_portero(jug, al_ev)
                    if jid not in ranking_jornada:
                        cid = ev.club_id
                        info = club_info.get(cid or 0, {})
                        ranking_jornada[jid] = {
                            "jugador_id": jid,
                            "nombre": (jug.apodo or jug.nombre) if jug else f"Jugador {jid}",
                            "foto": _norm_media(jug.foto_url) if jug else "",
                            "club_id": cid,
                            "club_nombre": info.get("nombre", ""),
                            "club_escudo": info.get("escudo", ""),
                            "puntos": 0.0,
                            "es_portero": es_gk,
                            "goles_jornada": 0,
                        }
                    else:
                        if es_gk:
                            ranking_jornada[jid]["es_portero"] = True
                    pts_ev = self._puntos_evento(ev.tipo_evento)
                    if pts_ev:
                        ranking_jornada[jid]["puntos"] += pts_ev
                    if ev.tipo_evento == "gol":
                        ranking_jornada[jid]["goles_jornada"] = (
                            ranking_jornada[jid].get("goles_jornada", 0) + 1
                        )

                # 3) Porteros: goles encajados + portería seria
                g_rec_local, g_rec_visit = gv, gl
                ports_local = [
                    al for al in alineaciones
                    if al.club_id == p.local_id and self._es_portero(al.jugador, al)
                ]
                ports_visit = [
                    al for al in alineaciones
                    if al.club_id == p.visitante_id and self._es_portero(al.jugador, al)
                ]

                if ports_local:
                    pen = self._penal_goles_encajados(g_rec_local)
                    for al in ports_local:
                        if al.jugador_id in ranking_jornada and pen:
                            ranking_jornada[al.jugador_id]["puntos"] += pen
                    if gl > gv and gv <= 1:
                        for al in ports_local:
                            if al.jugador_id in ranking_jornada:
                                ranking_jornada[al.jugador_id]["puntos"] += 1.0

                if ports_visit:
                    pen = self._penal_goles_encajados(g_rec_visit)
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
                    if not self._es_portero(jug_ev, al_ev):
                        continue
                    goles_gk = len(
                        [e for e in eventos if e.jugador_id == ev.jugador_id and e.tipo_evento == "gol"]
                    )
                    ranking_jornada[ev.jugador_id]["puntos"] += self._extra_portero_gol(goles_gk)

            if not ranking_jornada:
                continue

            rows = []
            for d in ranking_jornada.values():
                d["puntos"] = ceil(d["puntos"])
                if only_porteros and not d.get("es_portero"):
                    continue
                rows.append(d)

            coef_div = float(coef_division.get(g.competicion_id, 1.0))
            for r in rows:
                ranking_global.append({
                    **r,
                    "grupo_id": g.id,
                    "grupo_nombre": g.nombre,
                    "competicion_id": g.competicion_id,
                    "competicion_nombre": g.competicion.nombre,
                    "puntos_global": int(round(r["puntos"] * coef_div)),
                    "coef_division": coef_div,
                })

        ranking_global.sort(key=lambda x: (-x["puntos_global"], -x["puntos"], x["nombre"].lower()))
        return ranking_global

    def get(self, request, format=None):
        from django.utils import timezone
        temporada_id = _get_temporada_id(request, self.TEMPORADA_ID_BASE)
        only_porteros = request.GET.get("only_porteros") in ["1", "true", "True"]
        try:
            top_n = int(request.GET.get("top", "50"))
        except ValueError:
            top_n = 50
        strict = _get_bool(request, "strict", False)
        min_matches = _get_int(request, "min_matches", self.MIN_TOTAL_MATCHES)
        coef_division = _coef_division_lookup(temporada_id, self.JORNADA_REF_COEF)
        coef_club = _coef_club_lookup(temporada_id, self.JORNADA_REF_COEF)

        start_dt, end_dt, window_meta = self._compute_window(request, temporada_id)
        if not start_dt or not end_dt:
            return Response({
                "temporada_id": temporada_id,
                "window": {**window_meta, "status": "no-window"},
                "jugador_de_la_jornada_global": None,
                "ranking_global": [],
                "detail": "No hay partidos jugados para determinar ventana temporal."
            }, status=status.HTTP_200_OK)

        if strict:
            matched = self._count_partidos_in_window(temporada_id, start_dt, end_dt)
            window_meta = {
                **window_meta,
                "status": "strict",
                "matched_games": matched,
                "min_required": min_matches,
                "effective_start": start_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": end_dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
        else:
            valid_s, valid_e, ok, tries, matched = self._find_valid_window_with_min(
                temporada_id, start_dt, end_dt, min_matches
            )
            window_meta = {
                **window_meta,
                "status": "ok" if ok else "fallback_failed",
                "matched_games": matched,
                "min_required": min_matches,
                "fallback_weeks": tries,
                "effective_start": valid_s.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
                "effective_end": valid_e.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M"),
            }
            if not ok:
                return Response({
                    "temporada_id": temporada_id,
                    "window": window_meta,
                    "jugador_de_la_jornada_global": None,
                    "ranking_global": [],
                    "detail": "No hay una ventana con partidos suficientes (umbral) en el histórico reciente."
                }, status=status.HTTP_200_OK)
            start_dt, end_dt = valid_s, valid_e

        first_match = (
            Partido.objects
            .filter(grupo__temporada_id=temporada_id, jugado=True, fecha_hora__lte=end_dt)
            .order_by("fecha_hora")
            .first()
        )
        if not first_match:
            return Response({
                "temporada_id": temporada_id,
                "window": window_meta,
                "jugador_de_la_jornada_global": None,
                "ranking_global": [],
                "detail": "No hay partidos jugados en toda la temporada."
            }, status=status.HTTP_200_OK)

        temporada_start = first_match.fecha_hora

        ranking_semana = self._compute_ranking_for_range(
            temporada_id, start_dt, end_dt, only_porteros, coef_division, coef_club
        )
        semana_por_id = {r["jugador_id"]: r for r in ranking_semana}

        ranking_total = self._compute_ranking_for_range(
            temporada_id, temporada_start, end_dt, only_porteros, coef_division, coef_club
        )

        for row in ranking_total:
            jid = row["jugador_id"]
            total_unscaled = row["puntos"]
            total_scaled = row["puntos_global"]
            week_row = semana_por_id.get(jid)
            week_unscaled = week_row["puntos"] if week_row else 0
            week_scaled = week_row["puntos_global"] if week_row else 0

            row["puntos_totales"] = total_unscaled
            row["puntos_global_totales"] = total_scaled
            row["puntos_semana"] = week_scaled
            row["puntos"] = week_unscaled
            row["puntos_global"] = total_scaled

        ranking_total.sort(key=lambda x: (-x["puntos_global"], -x["puntos"], x["nombre"].lower()))
        if top_n > 0:
            ranking_total = ranking_total[:top_n]

        for row in ranking_total:
            row["foto"] = _abs_media(request, row.get("foto", ""))
            row["club_escudo"] = _abs_media(request, row.get("club_escudo", ""))

        payload = {
            "temporada_id": temporada_id,
            "window": window_meta,
            "jugador_de_la_jornada_global": ranking_total[0] if ranking_total else None,
            "ranking_global": ranking_total,
        }
        return Response(payload, status=status.HTTP_200_OK)


class CalcularScoreInteresView(APIView):
    """View stub - implementar según necesidades."""
    pass
