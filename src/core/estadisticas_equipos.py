# src/core/estadisticas_equipos.py

class EstadisticasEquipo:
    def __init__(self, nombre_equipo, partidos_jugados=0, victorias=0, empates=0, derrotas=0, goles_a_favor=0, goles_en_contra=0, puntos=0):
        self.nombre_equipo = nombre_equipo
        self.partidos_jugados = partidos_jugados
        self.victorias = victorias
        self.empates = empates
        self.derrotas = derrotas
        self.goles_a_favor = goles_a_favor
        self.goles_en_contra = goles_en_contra
        self.puntos = puntos

    def actualizar_estadisticas(self, goles_a_favor, goles_en_contra):
        """Actualizar las estadísticas del equipo"""
        self.partidos_jugados += 1
        self.goles_a_favor += goles_a_favor
        self.goles_en_contra += goles_en_contra
        if goles_a_favor > goles_en_contra:
            self.victorias += 1
            self.puntos += 3
        elif goles_a_favor == goles_en_contra:
            self.empates += 1
            self.puntos += 1
        else:
            self.derrotas += 1

    def obtener_estadisticas(self):
        """Obtener las estadísticas del equipo"""
        return {
            "partidos_jugados": self.partidos_jugados,
            "victorias": self.victorias,
            "empates": self.empates,
            "derrotas": self.derrotas,
            "goles_a_favor": self.goles_a_favor,
            "goles_en_contra": self.goles_en_contra,
            "puntos": self.puntos
        }
