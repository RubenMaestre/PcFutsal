# jugadores/serializers.py
from rest_framework import serializers

from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped

# Importar desde valoraciones
from valoraciones.models import ValoracionJugador

# Importar Club
from clubes.models import Club

# Importar modelos de fantasy
try:
    from fantasy.models import PuntosMVPJornada, PuntosMVPTotalJugador
    HAS_FANTASY = True
except ImportError:
    HAS_FANTASY = False
    PuntosMVPJornada = None
    PuntosMVPTotalJugador = None

# Helper para normalizar URLs de media
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --------------------------------------------
# Jugador básico
# --------------------------------------------
class JugadorSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    edad_display = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = [
            "id",
            "nombre",
            "apodo",
            "slug",
            "foto_url",
            "posicion_principal",
            "fecha_nacimiento",
            "edad_estimacion",
            "edad_display",
            "informe_scout",
            "activo",
        ]

    def get_foto_url(self, obj):
        return _norm_media(getattr(obj, "foto_url", ""))

    def get_edad_display(self, obj):
        """Calcula la edad a mostrar (fecha_nacimiento o edad_estimacion)"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return obj.edad_estimacion


# --------------------------------------------
# Jugador Lite (para listados)
# --------------------------------------------
class JugadorLiteSerializer(serializers.Serializer):
    """Serializer para listados de jugadores con info básica + club actual"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apodo = serializers.CharField(allow_blank=True, allow_null=True)
    foto_url = serializers.CharField(allow_blank=True)
    posicion_principal = serializers.CharField(allow_blank=True, allow_null=True)
    edad_display = serializers.IntegerField(allow_null=True)
    
    # Info del club actual
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    club_escudo_url = serializers.CharField(allow_null=True)
    temporada_nombre = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_blank=True, allow_null=True)
    
    # Mini stats
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)


# --------------------------------------------
# Club lite (para enlaces)
# --------------------------------------------
class ClubLiteSerializer(serializers.ModelSerializer):
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "nombre_oficial",
            "nombre_corto",
            "escudo_url",
        ]

    def get_escudo_url(self, obj):
        return _norm_media(getattr(obj, "escudo_url", ""))


# --------------------------------------------
# JugadorEnClubTemporada (reutilizar de clubes o crear aquí)
# --------------------------------------------
class JugadorEnClubTemporadaSerializer(serializers.ModelSerializer):
    jugador = JugadorSerializer()
    club = ClubLiteSerializer()
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = JugadorEnClubTemporada
        fields = [
            "id",
            "jugador",
            "club",
            "temporada",
            "temporada_nombre",
            "dorsal",
            "partidos_jugados",
            "goles",
            "tarjetas_amarillas",
            "tarjetas_rojas",
            "convocados",
            "titular",
            "suplente",
        ]


# --------------------------------------------
# Valoración FIFA
# --------------------------------------------
class ValoracionJugadorSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = ValoracionJugador
        fields = [
            "id",
            "temporada",
            "temporada_nombre",
            "ataque",
            "defensa",
            "pase",
            "regate",
            "potencia",
            "intensidad",
            "vision",
            "regularidad",
            "carisma",
            "media_global",
        ]


# --------------------------------------------
# Historial consolidado
# --------------------------------------------
class HistorialJugadorScrapedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialJugadorScraped
        fields = [
            "id",
            "temporada_texto",
            "competicion_texto",
            "equipo_texto",
        ]


# --------------------------------------------
# Historial completo (combinado)
# --------------------------------------------
class HistorialCompletoSerializer(serializers.Serializer):
    """Serializer para historial consolidado de JugadorEnClubTemporada + HistorialJugadorScraped"""
    temporada = serializers.CharField()
    temporada_id = serializers.IntegerField(allow_null=True)
    competicion = serializers.CharField()
    competicion_id = serializers.IntegerField(allow_null=True)
    grupo = serializers.CharField()
    grupo_id = serializers.IntegerField(allow_null=True)
    club = serializers.CharField()
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_null=True)
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)
    tarjetas_amarillas = serializers.IntegerField(default=0)
    tarjetas_rojas = serializers.IntegerField(default=0)
    es_scraped = serializers.BooleanField()  # True si viene de HistorialJugadorScraped


# --------------------------------------------
# Puntos Fantasy MVP
# --------------------------------------------
class PuntosFantasySerializer(serializers.Serializer):
    """Serializer para puntos de fantasy MVP del jugador"""
    temporada_id = serializers.IntegerField()
    temporada_nombre = serializers.CharField()
    
    # Puntos totales acumulados (de PuntosMVPTotalJugador)
    puntos_base_total = serializers.FloatField(default=0.0)
    puntos_con_coef_total = serializers.FloatField(default=0.0)
    goles_total = serializers.IntegerField(default=0)
    partidos_total = serializers.IntegerField(default=0)
    
    # Puntos por jornada (array de PuntosMVPJornada)
    puntos_por_jornada = serializers.ListField(
        child=serializers.DictField(),
        default=list
    )



from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped

# Importar desde valoraciones
from valoraciones.models import ValoracionJugador

# Importar Club
from clubes.models import Club

# Importar modelos de fantasy
try:
    from fantasy.models import PuntosMVPJornada, PuntosMVPTotalJugador
    HAS_FANTASY = True
except ImportError:
    HAS_FANTASY = False
    PuntosMVPJornada = None
    PuntosMVPTotalJugador = None

# Helper para normalizar URLs de media
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --------------------------------------------
# Jugador básico
# --------------------------------------------
class JugadorSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    edad_display = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = [
            "id",
            "nombre",
            "apodo",
            "slug",
            "foto_url",
            "posicion_principal",
            "fecha_nacimiento",
            "edad_estimacion",
            "edad_display",
            "informe_scout",
            "activo",
        ]

    def get_foto_url(self, obj):
        return _norm_media(getattr(obj, "foto_url", ""))

    def get_edad_display(self, obj):
        """Calcula la edad a mostrar (fecha_nacimiento o edad_estimacion)"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return obj.edad_estimacion


# --------------------------------------------
# Jugador Lite (para listados)
# --------------------------------------------
class JugadorLiteSerializer(serializers.Serializer):
    """Serializer para listados de jugadores con info básica + club actual"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apodo = serializers.CharField(allow_blank=True, allow_null=True)
    foto_url = serializers.CharField(allow_blank=True)
    posicion_principal = serializers.CharField(allow_blank=True, allow_null=True)
    edad_display = serializers.IntegerField(allow_null=True)
    
    # Info del club actual
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    club_escudo_url = serializers.CharField(allow_null=True)
    temporada_nombre = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_blank=True, allow_null=True)
    
    # Mini stats
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)


# --------------------------------------------
# Club lite (para enlaces)
# --------------------------------------------
class ClubLiteSerializer(serializers.ModelSerializer):
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "nombre_oficial",
            "nombre_corto",
            "escudo_url",
        ]

    def get_escudo_url(self, obj):
        return _norm_media(getattr(obj, "escudo_url", ""))


# --------------------------------------------
# JugadorEnClubTemporada (reutilizar de clubes o crear aquí)
# --------------------------------------------
class JugadorEnClubTemporadaSerializer(serializers.ModelSerializer):
    jugador = JugadorSerializer()
    club = ClubLiteSerializer()
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = JugadorEnClubTemporada
        fields = [
            "id",
            "jugador",
            "club",
            "temporada",
            "temporada_nombre",
            "dorsal",
            "partidos_jugados",
            "goles",
            "tarjetas_amarillas",
            "tarjetas_rojas",
            "convocados",
            "titular",
            "suplente",
        ]


# --------------------------------------------
# Valoración FIFA
# --------------------------------------------
class ValoracionJugadorSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = ValoracionJugador
        fields = [
            "id",
            "temporada",
            "temporada_nombre",
            "ataque",
            "defensa",
            "pase",
            "regate",
            "potencia",
            "intensidad",
            "vision",
            "regularidad",
            "carisma",
            "media_global",
        ]


# --------------------------------------------
# Historial consolidado
# --------------------------------------------
class HistorialJugadorScrapedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialJugadorScraped
        fields = [
            "id",
            "temporada_texto",
            "competicion_texto",
            "equipo_texto",
        ]


# --------------------------------------------
# Historial completo (combinado)
# --------------------------------------------
class HistorialCompletoSerializer(serializers.Serializer):
    """Serializer para historial consolidado de JugadorEnClubTemporada + HistorialJugadorScraped"""
    temporada = serializers.CharField()
    temporada_id = serializers.IntegerField(allow_null=True)
    competicion = serializers.CharField()
    competicion_id = serializers.IntegerField(allow_null=True)
    grupo = serializers.CharField()
    grupo_id = serializers.IntegerField(allow_null=True)
    club = serializers.CharField()
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_null=True)
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)
    tarjetas_amarillas = serializers.IntegerField(default=0)
    tarjetas_rojas = serializers.IntegerField(default=0)
    es_scraped = serializers.BooleanField()  # True si viene de HistorialJugadorScraped


# --------------------------------------------
# Puntos Fantasy MVP
# --------------------------------------------
class PuntosFantasySerializer(serializers.Serializer):
    """Serializer para puntos de fantasy MVP del jugador"""
    temporada_id = serializers.IntegerField()
    temporada_nombre = serializers.CharField()
    
    # Puntos totales acumulados (de PuntosMVPTotalJugador)
    puntos_base_total = serializers.FloatField(default=0.0)
    puntos_con_coef_total = serializers.FloatField(default=0.0)
    goles_total = serializers.IntegerField(default=0)
    partidos_total = serializers.IntegerField(default=0)
    
    # Puntos por jornada (array de PuntosMVPJornada)
    puntos_por_jornada = serializers.ListField(
        child=serializers.DictField(),
        default=list
    )



from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped

# Importar desde valoraciones
from valoraciones.models import ValoracionJugador

# Importar Club
from clubes.models import Club

# Importar modelos de fantasy
try:
    from fantasy.models import PuntosMVPJornada, PuntosMVPTotalJugador
    HAS_FANTASY = True
except ImportError:
    HAS_FANTASY = False
    PuntosMVPJornada = None
    PuntosMVPTotalJugador = None

# Helper para normalizar URLs de media
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --------------------------------------------
# Jugador básico
# --------------------------------------------
class JugadorSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    edad_display = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = [
            "id",
            "nombre",
            "apodo",
            "slug",
            "foto_url",
            "posicion_principal",
            "fecha_nacimiento",
            "edad_estimacion",
            "edad_display",
            "informe_scout",
            "activo",
        ]

    def get_foto_url(self, obj):
        return _norm_media(getattr(obj, "foto_url", ""))

    def get_edad_display(self, obj):
        """Calcula la edad a mostrar (fecha_nacimiento o edad_estimacion)"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return obj.edad_estimacion


# --------------------------------------------
# Jugador Lite (para listados)
# --------------------------------------------
class JugadorLiteSerializer(serializers.Serializer):
    """Serializer para listados de jugadores con info básica + club actual"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apodo = serializers.CharField(allow_blank=True, allow_null=True)
    foto_url = serializers.CharField(allow_blank=True)
    posicion_principal = serializers.CharField(allow_blank=True, allow_null=True)
    edad_display = serializers.IntegerField(allow_null=True)
    
    # Info del club actual
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    club_escudo_url = serializers.CharField(allow_null=True)
    temporada_nombre = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_blank=True, allow_null=True)
    
    # Mini stats
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)


# --------------------------------------------
# Club lite (para enlaces)
# --------------------------------------------
class ClubLiteSerializer(serializers.ModelSerializer):
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "nombre_oficial",
            "nombre_corto",
            "escudo_url",
        ]

    def get_escudo_url(self, obj):
        return _norm_media(getattr(obj, "escudo_url", ""))


# --------------------------------------------
# JugadorEnClubTemporada (reutilizar de clubes o crear aquí)
# --------------------------------------------
class JugadorEnClubTemporadaSerializer(serializers.ModelSerializer):
    jugador = JugadorSerializer()
    club = ClubLiteSerializer()
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = JugadorEnClubTemporada
        fields = [
            "id",
            "jugador",
            "club",
            "temporada",
            "temporada_nombre",
            "dorsal",
            "partidos_jugados",
            "goles",
            "tarjetas_amarillas",
            "tarjetas_rojas",
            "convocados",
            "titular",
            "suplente",
        ]


# --------------------------------------------
# Valoración FIFA
# --------------------------------------------
class ValoracionJugadorSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = ValoracionJugador
        fields = [
            "id",
            "temporada",
            "temporada_nombre",
            "ataque",
            "defensa",
            "pase",
            "regate",
            "potencia",
            "intensidad",
            "vision",
            "regularidad",
            "carisma",
            "media_global",
        ]


# --------------------------------------------
# Historial consolidado
# --------------------------------------------
class HistorialJugadorScrapedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialJugadorScraped
        fields = [
            "id",
            "temporada_texto",
            "competicion_texto",
            "equipo_texto",
        ]


# --------------------------------------------
# Historial completo (combinado)
# --------------------------------------------
class HistorialCompletoSerializer(serializers.Serializer):
    """Serializer para historial consolidado de JugadorEnClubTemporada + HistorialJugadorScraped"""
    temporada = serializers.CharField()
    temporada_id = serializers.IntegerField(allow_null=True)
    competicion = serializers.CharField()
    competicion_id = serializers.IntegerField(allow_null=True)
    grupo = serializers.CharField()
    grupo_id = serializers.IntegerField(allow_null=True)
    club = serializers.CharField()
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_null=True)
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)
    tarjetas_amarillas = serializers.IntegerField(default=0)
    tarjetas_rojas = serializers.IntegerField(default=0)
    es_scraped = serializers.BooleanField()  # True si viene de HistorialJugadorScraped


# --------------------------------------------
# Puntos Fantasy MVP
# --------------------------------------------
class PuntosFantasySerializer(serializers.Serializer):
    """Serializer para puntos de fantasy MVP del jugador"""
    temporada_id = serializers.IntegerField()
    temporada_nombre = serializers.CharField()
    
    # Puntos totales acumulados (de PuntosMVPTotalJugador)
    puntos_base_total = serializers.FloatField(default=0.0)
    puntos_con_coef_total = serializers.FloatField(default=0.0)
    goles_total = serializers.IntegerField(default=0)
    partidos_total = serializers.IntegerField(default=0)
    
    # Puntos por jornada (array de PuntosMVPJornada)
    puntos_por_jornada = serializers.ListField(
        child=serializers.DictField(),
        default=list
    )



from .models import Jugador, JugadorEnClubTemporada, HistorialJugadorScraped

# Importar desde valoraciones
from valoraciones.models import ValoracionJugador

# Importar Club
from clubes.models import Club

# Importar modelos de fantasy
try:
    from fantasy.models import PuntosMVPJornada, PuntosMVPTotalJugador
    HAS_FANTASY = True
except ImportError:
    HAS_FANTASY = False
    PuntosMVPJornada = None
    PuntosMVPTotalJugador = None

# Helper para normalizar URLs de media
def _norm_media(url: str | None) -> str:
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/media/"):
        return u
    return "/media/" + u.lstrip("/")


# --------------------------------------------
# Jugador básico
# --------------------------------------------
class JugadorSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    edad_display = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = [
            "id",
            "nombre",
            "apodo",
            "slug",
            "foto_url",
            "posicion_principal",
            "fecha_nacimiento",
            "edad_estimacion",
            "edad_display",
            "informe_scout",
            "activo",
        ]

    def get_foto_url(self, obj):
        return _norm_media(getattr(obj, "foto_url", ""))

    def get_edad_display(self, obj):
        """Calcula la edad a mostrar (fecha_nacimiento o edad_estimacion)"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return obj.edad_estimacion


# --------------------------------------------
# Jugador Lite (para listados)
# --------------------------------------------
class JugadorLiteSerializer(serializers.Serializer):
    """Serializer para listados de jugadores con info básica + club actual"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apodo = serializers.CharField(allow_blank=True, allow_null=True)
    foto_url = serializers.CharField(allow_blank=True)
    posicion_principal = serializers.CharField(allow_blank=True, allow_null=True)
    edad_display = serializers.IntegerField(allow_null=True)
    
    # Info del club actual
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    club_escudo_url = serializers.CharField(allow_null=True)
    temporada_nombre = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_blank=True, allow_null=True)
    
    # Mini stats
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)


# --------------------------------------------
# Club lite (para enlaces)
# --------------------------------------------
class ClubLiteSerializer(serializers.ModelSerializer):
    escudo_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            "id",
            "nombre_oficial",
            "nombre_corto",
            "escudo_url",
        ]

    def get_escudo_url(self, obj):
        return _norm_media(getattr(obj, "escudo_url", ""))


# --------------------------------------------
# JugadorEnClubTemporada (reutilizar de clubes o crear aquí)
# --------------------------------------------
class JugadorEnClubTemporadaSerializer(serializers.ModelSerializer):
    jugador = JugadorSerializer()
    club = ClubLiteSerializer()
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = JugadorEnClubTemporada
        fields = [
            "id",
            "jugador",
            "club",
            "temporada",
            "temporada_nombre",
            "dorsal",
            "partidos_jugados",
            "goles",
            "tarjetas_amarillas",
            "tarjetas_rojas",
            "convocados",
            "titular",
            "suplente",
        ]


# --------------------------------------------
# Valoración FIFA
# --------------------------------------------
class ValoracionJugadorSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)

    class Meta:
        model = ValoracionJugador
        fields = [
            "id",
            "temporada",
            "temporada_nombre",
            "ataque",
            "defensa",
            "pase",
            "regate",
            "potencia",
            "intensidad",
            "vision",
            "regularidad",
            "carisma",
            "media_global",
        ]


# --------------------------------------------
# Historial consolidado
# --------------------------------------------
class HistorialJugadorScrapedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialJugadorScraped
        fields = [
            "id",
            "temporada_texto",
            "competicion_texto",
            "equipo_texto",
        ]


# --------------------------------------------
# Historial completo (combinado)
# --------------------------------------------
class HistorialCompletoSerializer(serializers.Serializer):
    """Serializer para historial consolidado de JugadorEnClubTemporada + HistorialJugadorScraped"""
    temporada = serializers.CharField()
    temporada_id = serializers.IntegerField(allow_null=True)
    competicion = serializers.CharField()
    competicion_id = serializers.IntegerField(allow_null=True)
    grupo = serializers.CharField()
    grupo_id = serializers.IntegerField(allow_null=True)
    club = serializers.CharField()
    club_id = serializers.IntegerField(allow_null=True)
    club_nombre = serializers.CharField(allow_null=True)
    club_slug = serializers.CharField(allow_null=True)
    dorsal = serializers.CharField(allow_null=True)
    partidos_jugados = serializers.IntegerField(default=0)
    goles = serializers.IntegerField(default=0)
    tarjetas_amarillas = serializers.IntegerField(default=0)
    tarjetas_rojas = serializers.IntegerField(default=0)
    es_scraped = serializers.BooleanField()  # True si viene de HistorialJugadorScraped


# --------------------------------------------
# Puntos Fantasy MVP
# --------------------------------------------
class PuntosFantasySerializer(serializers.Serializer):
    """Serializer para puntos de fantasy MVP del jugador"""
    temporada_id = serializers.IntegerField()
    temporada_nombre = serializers.CharField()
    
    # Puntos totales acumulados (de PuntosMVPTotalJugador)
    puntos_base_total = serializers.FloatField(default=0.0)
    puntos_con_coef_total = serializers.FloatField(default=0.0)
    goles_total = serializers.IntegerField(default=0)
    partidos_total = serializers.IntegerField(default=0)
    
    # Puntos por jornada (array de PuntosMVPJornada)
    puntos_por_jornada = serializers.ListField(
        child=serializers.DictField(),
        default=list
    )

