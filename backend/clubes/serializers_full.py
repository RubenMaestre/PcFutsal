# clubes/serializers_full.py
from rest_framework import serializers
from django.db.models import Q
from .models import (
    Club,
    ClubEnGrupo,
    ClubSeasonProgress,
    ClubSeasonHistory,
    ClubAward,
    ClubMedia,
    ClubNota,
    ClubTravelStat,
    ValoracionClub,
    ClubStaffMember,
)
from jugadores.models import JugadorEnClubTemporada


# --- Helpers ---
def norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --- Serializers básicos ---
class ClubLiteSerializer(serializers.ModelSerializer):
    localidad = serializers.CharField(source="ciudad", allow_blank=True, required=False)
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ["id", "slug", "nombre_oficial", "nombre_corto", "localidad", "escudo_url"]

    def get_escudo_url(self, obj):
        return norm_media(getattr(obj, "escudo_url", ""))


class ClasificacionActualSerializer(serializers.ModelSerializer):
    # Mapear campos del modelo a los nombres que espera el frontend
    posicion = serializers.SerializerMethodField()
    v = serializers.SerializerMethodField()
    e = serializers.SerializerMethodField()
    d = serializers.SerializerMethodField()
    gf = serializers.SerializerMethodField()
    gc = serializers.SerializerMethodField()
    
    # Campos calculados para tarjetas
    tarjetas_amarillas = serializers.SerializerMethodField()
    tarjetas_dobles_amarillas = serializers.SerializerMethodField()
    tarjetas_rojas = serializers.SerializerMethodField()
    
    class Meta:
        model = ClubEnGrupo
        fields = [
            "posicion",
            "puntos",
            "partidos_jugados",
            "v",
            "e",
            "d",
            "gf",
            "gc",
            "diferencia_goles",
            "racha",
            "tarjetas_amarillas",
            "tarjetas_dobles_amarillas",
            "tarjetas_rojas",
        ]
    
    def get_posicion(self, obj):
        """Devuelve la posición actual o None"""
        return obj.posicion_actual if obj else None
    
    def get_v(self, obj):
        """Devuelve victorias, calculando desde partidos si es necesario"""
        if not obj:
            return 0
        
        # Si hay victorias en el modelo, usarlas
        if obj.victorias and obj.victorias > 0:
            return obj.victorias
        
        # Si no, calcular desde partidos
        return self._calcular_victorias_desde_partidos(obj)
    
    def get_e(self, obj):
        """Devuelve empates, calculando desde partidos si es necesario"""
        if not obj:
            return 0
        
        # Si hay empates en el modelo, usarlos
        if obj.empates and obj.empates > 0:
            return obj.empates
        
        # Si no, calcular desde partidos
        return self._calcular_empates_desde_partidos(obj)
    
    def get_d(self, obj):
        """Devuelve derrotas, calculando desde partidos si es necesario"""
        if not obj:
            return 0
        
        # Si hay derrotas en el modelo, usarlas
        if obj.derrotas and obj.derrotas > 0:
            return obj.derrotas
        
        # Si no, calcular desde partidos
        return self._calcular_derrotas_desde_partidos(obj)
    
    def get_gf(self, obj):
        """Devuelve goles a favor, calculando desde partidos si es necesario"""
        if not obj:
            return 0
        
        # Si hay goles en el modelo, usarlos
        if obj.goles_favor and obj.goles_favor > 0:
            return obj.goles_favor
        
        # Si no, calcular desde partidos
        return self._calcular_goles_favor_desde_partidos(obj)
    
    def get_gc(self, obj):
        """Devuelve goles en contra, calculando desde partidos si es necesario"""
        if not obj:
            return 0
        
        # Si hay goles en el modelo, usarlos
        if obj.goles_contra and obj.goles_contra > 0:
            return obj.goles_contra
        
        # Si no, calcular desde partidos
        return self._calcular_goles_contra_desde_partidos(obj)
    
    def _calcular_victorias_desde_partidos(self, obj):
        """Calcula victorias desde los partidos del grupo"""
        from partidos.models import Partido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        partidos = Partido.objects.filter(
            grupo=obj.grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        ).filter(
            Q(local=obj.club) | Q(visitante=obj.club)
        )
        
        victorias = 0
        for p in partidos:
            if p.local == obj.club and p.goles_local > p.goles_visitante:
                victorias += 1
            elif p.visitante == obj.club and p.goles_visitante > p.goles_local:
                victorias += 1
        
        return victorias
    
    def _calcular_empates_desde_partidos(self, obj):
        """Calcula empates desde los partidos del grupo"""
        from partidos.models import Partido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        partidos = Partido.objects.filter(
            grupo=obj.grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        ).filter(
            Q(local=obj.club) | Q(visitante=obj.club)
        )
        
        empates = 0
        for p in partidos:
            if p.goles_local == p.goles_visitante:
                empates += 1
        
        return empates
    
    def _calcular_derrotas_desde_partidos(self, obj):
        """Calcula derrotas desde los partidos del grupo"""
        from partidos.models import Partido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        partidos = Partido.objects.filter(
            grupo=obj.grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        ).filter(
            Q(local=obj.club) | Q(visitante=obj.club)
        )
        
        derrotas = 0
        for p in partidos:
            if p.local == obj.club and p.goles_local < p.goles_visitante:
                derrotas += 1
            elif p.visitante == obj.club and p.goles_visitante < p.goles_local:
                derrotas += 1
        
        return derrotas
    
    def _calcular_goles_favor_desde_partidos(self, obj):
        """Calcula goles a favor desde los partidos del grupo"""
        from partidos.models import Partido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        partidos = Partido.objects.filter(
            grupo=obj.grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        ).filter(
            Q(local=obj.club) | Q(visitante=obj.club)
        )
        
        goles_favor = 0
        for p in partidos:
            if p.local == obj.club:
                goles_favor += (p.goles_local or 0)
            elif p.visitante == obj.club:
                goles_favor += (p.goles_visitante or 0)
        
        return goles_favor
    
    def _calcular_goles_contra_desde_partidos(self, obj):
        """Calcula goles en contra desde los partidos del grupo"""
        from partidos.models import Partido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        partidos = Partido.objects.filter(
            grupo=obj.grupo,
            jugado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        ).filter(
            Q(local=obj.club) | Q(visitante=obj.club)
        )
        
        goles_contra = 0
        for p in partidos:
            if p.local == obj.club:
                goles_contra += (p.goles_visitante or 0)
            elif p.visitante == obj.club:
                goles_contra += (p.goles_local or 0)
        
        return goles_contra
    
    def get_tarjetas_amarillas(self, obj):
        """Calcula tarjetas amarillas del club en el grupo"""
        from partidos.models import EventoPartido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        # Obtener todos los partidos del grupo
        partidos_ids = obj.grupo.partidos.values_list("id", flat=True)
        
        # Contar tarjetas amarillas del club en esos partidos
        count = EventoPartido.objects.filter(
            partido_id__in=partidos_ids,
            club=obj.club,
            tipo_evento="amarilla"
        ).count()
        
        return count
    
    def get_tarjetas_dobles_amarillas(self, obj):
        """Calcula dobles amarillas del club en el grupo"""
        from partidos.models import EventoPartido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        # Obtener todos los partidos del grupo
        partidos_ids = obj.grupo.partidos.values_list("id", flat=True)
        
        # Contar dobles amarillas del club en esos partidos
        count = EventoPartido.objects.filter(
            partido_id__in=partidos_ids,
            club=obj.club,
            tipo_evento="doble_amarilla"
        ).count()
        
        return count
    
    def get_tarjetas_rojas(self, obj):
        """Calcula tarjetas rojas del club en el grupo"""
        from partidos.models import EventoPartido
        if not obj or not obj.grupo or not obj.club:
            return 0
        
        # Obtener todos los partidos del grupo
        partidos_ids = obj.grupo.partidos.values_list("id", flat=True)
        
        # Contar tarjetas rojas del club en esos partidos
        count = EventoPartido.objects.filter(
            partido_id__in=partidos_ids,
            club=obj.club,
            tipo_evento="roja"
        ).count()
        
        return count


class JugadorLiteSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="jugador.nombre", default="", allow_blank=True)
    apodo = serializers.CharField(source="jugador.apodo", default="", allow_blank=True, allow_null=True)
    slug = serializers.CharField(source="jugador.slug", default="", allow_blank=True, allow_null=True)
    posicion_principal = serializers.CharField(source="jugador.posicion_principal", default="", allow_blank=True)
    foto_url = serializers.SerializerMethodField()
    edad_display = serializers.SerializerMethodField()

    class Meta:
        model = JugadorEnClubTemporada
        fields = ["id", "nombre", "apodo", "slug", "posicion_principal", "dorsal", "foto_url", "partidos_jugados", "goles", "edad_display"]

    def get_foto_url(self, obj):
        return norm_media(getattr(obj.jugador, "foto_url", ""))
    
    def get_edad_display(self, obj):
        """Calcula la edad del jugador si tiene fecha de nacimiento"""
        if not obj.jugador or not obj.jugador.fecha_nacimiento:
            return None
        from datetime import date
        today = date.today()
        born = obj.jugador.fecha_nacimiento
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age


class StaffLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubStaffMember
        fields = ["nombre", "rol", "email", "telefono", "visible_publico"]


class ValoracionClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValoracionClub
        exclude = ["id", "club", "temporada"]


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubAward
        fields = ["tipo", "grupo_id", "jornada", "notas"]


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubMedia
        fields = ["tipo", "titulo", "url"]


class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubNota
        fields = ["titulo", "texto", "enlace", "grupo_id"]


class TravelStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubTravelStat
        exclude = ["id", "club", "grupo", "temporada", "actualizado_en"]


# --- Series para gráficas ---
class ClubSeriesSerializer(serializers.Serializer):
    progreso_jornada = serializers.SerializerMethodField()
    historico_pos_final = serializers.SerializerMethodField()

    def get_progreso_jornada(self, club: Club):
        qs = ClubSeasonProgress.objects.filter(club=club).order_by("jornada")
        return {
            "labels": [x.jornada for x in qs],
            "puntos_acum": [x.puntos_acum for x in qs],
            "posicion": [x.pos_clasif for x in qs],
        }

    def get_historico_pos_final(self, club: Club):
        qs = ClubSeasonHistory.objects.filter(club=club).order_by("temporada__nombre")
        return {
            "labels": [x.temporada.nombre for x in qs],
            "pos_final": [x.pos_final for x in qs],
            "puntos": [x.puntos for x in qs],
        }


# --- Serializer principal ---
class ClubFullSerializer(serializers.ModelSerializer):
    localidad = serializers.CharField(source="ciudad", allow_blank=True, required=False)
    escudo_url = serializers.SerializerMethodField()
    clasificacion_actual = serializers.SerializerMethodField()
    plantilla = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    valoracion = serializers.SerializerMethodField()
    series = serializers.SerializerMethodField()
    awards = AwardSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    notas = NotaSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "slug",
            "nombre_oficial",
            "nombre_corto",
            "siglas",
            "localidad",
            "provincia",
            "escudo_url",
            "pabellon",
            "web",
            "email_contacto",
            "telefono",
            "fundado_en",
            "historia_resumida",
            "clasificacion_actual",
            "plantilla",
            "staff",
            "valoracion",
            "series",
            "awards",
            "media",
            "notas",
        ]

    def get_escudo_url(self, obj):
        return norm_media(getattr(obj, "escudo_url", ""))

    def get_clasificacion_actual(self, obj):
        grupo = self.context.get("grupo")
        if not grupo:
            return None
        cg = ClubEnGrupo.objects.filter(club=obj, grupo=grupo).first()
        return ClasificacionActualSerializer(cg).data if cg else None

    def get_plantilla(self, obj):
        temporada = self.context.get("temporada")
        if not temporada:
            return []
        jugadores = JugadorEnClubTemporada.objects.filter(club=obj, temporada=temporada).select_related("jugador")
        return JugadorLiteSerializer(jugadores, many=True).data

    def get_staff(self, obj):
        temporada = self.context.get("temporada")
        if not temporada:
            return []
        staff = ClubStaffMember.objects.filter(club=obj, temporada=temporada, visible_publico=True)
        return StaffLiteSerializer(staff, many=True).data

    def get_valoracion(self, obj):
        temporada = self.context.get("temporada")
        if not temporada:
            return None
        val = ValoracionClub.objects.filter(club=obj, temporada=temporada).first()
        return ValoracionClubSerializer(val).data if val else None

    def get_series(self, obj):
        return ClubSeriesSerializer().to_representation(obj)


# --- Función helper para construir respuesta completa ---
def club_full_serializer(club: Club, request) -> dict:
    """
    Construye la respuesta completa de un club usando ClubFullSerializer.
    Determina el grupo y temporada activa automáticamente.
    """
    from nucleo.models import Temporada
    
    # Obtener temporada activa (más reciente)
    temporada_activa = Temporada.objects.order_by("-id").first()
    
    # Obtener el grupo actual del club (si existe)
    grupo_actual = None
    if temporada_activa:
        # Buscar ClubEnGrupo en temporada activa
        ceg_activa = ClubEnGrupo.objects.filter(
            club=club,
            grupo__temporada=temporada_activa
        ).select_related("grupo").first()
        
        if ceg_activa:
            grupo_actual = ceg_activa.grupo
    
    # Si no hay grupo en temporada activa, buscar en cualquier temporada
    if not grupo_actual:
        ceg_cualquiera = ClubEnGrupo.objects.filter(
            club=club
        ).select_related("grupo", "grupo__temporada").order_by("-grupo__temporada__id").first()
        
        if ceg_cualquiera:
            grupo_actual = ceg_cualquiera.grupo
            temporada_activa = ceg_cualquiera.grupo.temporada
    
    # Construir contexto para el serializer
    context = {
        "request": request,
        "temporada": temporada_activa,
        "grupo": grupo_actual,
    }
    
    # Serializar
    serializer = ClubFullSerializer(club, context=context)
    club_data = serializer.data
    
    # Envolver en estructura esperada por el frontend
    return {
        "club": club_data,
        "contexto": {
            "temporada": {
                "id": temporada_activa.id if temporada_activa else None,
                "nombre": temporada_activa.nombre if temporada_activa else None,
            } if temporada_activa else None,
            "grupo": {
                "id": grupo_actual.id if grupo_actual else None,
                "nombre": grupo_actual.nombre if grupo_actual else None,
                "competicion": grupo_actual.competicion.nombre if grupo_actual and grupo_actual.competicion else None,
                "temporada": grupo_actual.temporada.nombre if grupo_actual and grupo_actual.temporada else None,
            } if grupo_actual else None,
        } if (temporada_activa or grupo_actual) else None,
    }
