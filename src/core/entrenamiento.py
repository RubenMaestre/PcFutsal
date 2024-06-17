# src/core/entrenamiento.py

class Entrenamiento:
    def __init__(self, sesiones):
        self.sesiones = sesiones  # Diccionario con rutinas de entrenamiento (ej. {"dribbling": 3, "passing": 2})

    def agregar_sesion(self, habilidad, intensidad):
        if habilidad in self.sesiones:
            self.sesiones[habilidad] += intensidad
        else:
            self.sesiones[habilidad] = intensidad

    def ejecutar_entrenamiento(self, equipo):
        """Ejecutar sesiones de entrenamiento y mejorar habilidades de los jugadores"""
        for jugador in equipo.jugadores:
            for habilidad, intensidad in self.sesiones.items():
                if habilidad in jugador.habilidades:
                    jugador.habilidades[habilidad] = min(jugador.habilidades[habilidad] + intensidad, 100)  # Mejorar habilidad sin exceder 100
                    jugador.cambiar_condicion_fisica(-intensidad)  # Reducir condición física basada en la intensidad
