# estadisticas/views_coeficientes.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from nucleo.models import Grupo
from clubes.models import ClubEnGrupo
from valoraciones.models import CoeficienteClub


class CoeficientesClubesView(APIView):
    """
    GET /api/estadisticas/coeficientes-clubes/?grupo_id=15
    GET /api/estadisticas/coeficientes-clubes/?grupo_id=15&jornada=6

    Devuelve para cada club del grupo su coeficiente:
    - intenta coger el de esa jornada
    - si no hay, coge el último creado para esa temporada
    - si tampoco hay, devuelve 0.5

    POST /api/estadisticas/coeficientes-clubes/
    Body JSON:
    {
      "club_id": 12,
      "temporada_id": 3,
      "jornada_referencia": 6,   // opcional
      "valor": 0.85,
      "comentario": "ajuste manual"
    }
    """

    def get(self, request, format=None):
        grupo_id = request.GET.get("grupo_id")
        jornada_param = request.GET.get("jornada")

        if not grupo_id:
            return Response({"detail": "Falta grupo_id"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. grupo
        try:
            grupo = Grupo.objects.select_related("temporada").get(id=grupo_id)
        except Grupo.DoesNotExist:
            return Response({"detail": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        temporada = grupo.temporada

        # 2. clubes del grupo
        filas = (
            ClubEnGrupo.objects
            .filter(grupo=grupo)
            .select_related("club")
            .order_by("posicion_actual", "club__nombre_oficial")
        )

        # 3. queremos los coef de ESTA temporada y para ESTOS clubs
        club_ids = [f.club_id for f in filas]

        qs_coef = (
            CoeficienteClub.objects
            .filter(club_id__in=club_ids, temporada=temporada)
        )

        # si pasan jornada, intentamos clavar esa
        jref = None
        if jornada_param:
            try:
                jref = int(jornada_param)
            except ValueError:
                return Response({"detail": "jornada debe ser número"}, status=status.HTTP_400_BAD_REQUEST)

        # Construimos dos lookups para manejar la prioridad de coeficientes:
        # 1. coef_por_club_jornada: coeficiente de una jornada específica (si se solicita)
        # 2. coef_por_club_ultimo: último coeficiente calculado (fallback si no hay de esa jornada)
        coef_por_club_jornada = {}
        coef_por_club_ultimo = {}

        for c in qs_coef:
            # Guardar el último coeficiente por fecha de actualización (más reciente)
            prev = coef_por_club_ultimo.get(c.club_id)
            if not prev or c.actualizado_en > prev.actualizado_en:
                coef_por_club_ultimo[c.club_id] = c

            # Si se solicita una jornada específica, guardar el coeficiente de esa jornada
            if jref is not None and c.jornada_referencia == jref:
                coef_por_club_jornada[c.club_id] = c

        # 4. Montar respuesta club por club con prioridad:
        # - Si hay jornada solicitada y existe coef de esa jornada → usar ese
        # - Si no, usar el último coeficiente disponible
        # - Si no hay ninguno → 0.5 (valor por defecto neutral)
        resultados = []
        for f in filas:
            cid = f.club_id

            # Prioridad 1: coeficiente de la jornada específica solicitada
            if jref is not None and cid in coef_por_club_jornada:
                obj = coef_por_club_jornada[cid]
                valor = obj.valor
                j_used = obj.jornada_referencia
            # Prioridad 2: último coeficiente disponible (más reciente)
            elif cid in coef_por_club_ultimo:
                obj = coef_por_club_ultimo[cid]
                valor = obj.valor
                j_used = obj.jornada_referencia
            # prioridad 3: default
            else:
                valor = 0.5
                j_used = None

            resultados.append({
                "club_id": cid,
                "club_nombre": f.club.nombre_corto or f.club.nombre_oficial,
                "club_escudo": f.club.escudo_url or "",
                "posicion_actual": f.posicion_actual,
                "coeficiente": float(f"{valor:.2f}"),
                "jornada_origen": j_used,
            })

        payload = {
            "grupo": {
                "id": grupo.id,
                "nombre": grupo.nombre,
                "competicion": grupo.competicion.nombre,
                "temporada": temporada.nombre,
            },
            "jornada_solicitada": jref,
            "resultados": resultados,
        }

        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Inserta/actualiza un coeficiente a mano.
        Esto lo puedes llamar desde tu frontend de admin.
        """
        club_id = request.data.get("club_id")
        temporada_id = request.data.get("temporada_id")
        valor = request.data.get("valor")
        jornada_referencia = request.data.get("jornada_referencia")
        comentario = request.data.get("comentario", "")

        if not club_id or not temporada_id or valor is None:
            return Response(
                {"detail": "club_id, temporada_id y valor son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            valor = float(valor)
        except ValueError:
            return Response({"detail": "valor debe ser numérico."}, status=status.HTTP_400_BAD_REQUEST)

        # normalizamos jornada_referencia
        if jornada_referencia == "" or jornada_referencia is None:
            jornada_referencia = None

        obj, created = CoeficienteClub.objects.update_or_create(
            club_id=club_id,
            temporada_id=temporada_id,
            jornada_referencia=jornada_referencia,
            defaults={
                "valor": valor,
                "comentario": comentario,
            }
        )

        return Response(
            {
                "id": obj.id,
                "created": created,
                "club_id": obj.club_id,
                "temporada_id": obj.temporada_id,
                "jornada_referencia": obj.jornada_referencia,
                "valor": obj.valor,
                "comentario": obj.comentario,
            },
            status=status.HTTP_200_OK,
        )
