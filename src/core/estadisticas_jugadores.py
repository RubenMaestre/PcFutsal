# src/core/estadisticas_jugadores.py

class EstadisticasJugador:
    def __init__(self, id_jugador, partidos_jugados=0, goles=0, asistencias=0, tarjetas_amarillas=0, tarjetas_rojas=0):
        self.id_jugador = id_jugador
        self.partidos_jugados = partidos_jugados
        self.goles = goles
        self.asistencias = asistencias
        self.tarjetas_amarillas = tarjetas_amarillas
        self.tarjetas_rojas = tarjetas_rojas

    def actualizar_estadisticas(self, goles=0, asistencias=0, tarjetas_amarillas=0, tarjetas_rojas=0):
        """Actualizar las estadísticas del jugador"""
        self.partidos_jugados += 1
        self.goles += goles
        self.asistencias += asistencias
        self.tarjetas_amarillas += tarjetas_amarillas
        self.tarjetas_rojas += tarjetas_rojas

    def obtener_estadisticas(self):
        """Obtener las estadísticas del jugador"""
        return {
            "partidos_jugados": self.partidos_jugados,
            "goles": self.goles,
            "asistencias": self.asistencias,
            "tarjetas_amarillas": self.tarjetas_amarillas,
            "tarjetas_rojas": self.tarjetas_rojas
        }
