# src/core/calendario_copa.py

import random

class CalendarioCopa:
    def __init__(self, equipos):
        self.equipos = equipos
        self.calendario = []

    def generar_calendario(self):
        """Generar el calendario de partidos para la copa"""
        random.shuffle(self.equipos)
        self.calendario = [(self.equipos[i], self.equipos[i+1]) for i in range(0, len(self.equipos) - 1, 2)]
        return self.calendario

    def jugar_ronda(self):
        """Jugar una ronda de la copa"""
        ganadores = []
        siguiente_ronda = []
        for partido in self.calendario:
            equipo1, equipo2 = partido
            puntuacion1, puntuacion2 = self.simular_partido(equipo1, equipo2)
            ganadores.append((equipo1 if puntuacion1 > puntuacion2 else equipo2))
            siguiente_ronda.append((equipo1, equipo2, puntuacion1, puntuacion2))
        self.calendario = [(ganadores[i], ganadores[i+1]) for i in range(0, len(ganadores) - 1, 2)]
        return siguiente_ronda

    def simular_partido(self, equipo1, equipo2):
        """Simular un partido de fútbol sala"""
        return random.randint(0, 5), random.randint(0, 5)  # Ejemplo simple de simulación de partido
