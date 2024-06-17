# src/core/partidos.py

import random

class Partido:
    def __init__(self, equipo1, equipo2):
        self.equipo1 = equipo1
        self.equipo2 = equipo2
        self.resultado = None
        self.eventos = []

    def simular(self):
        """Simular el partido y determinar el resultado"""
        puntuacion_equipo1 = 0
        puntuacion_equipo2 = 0

        # Simular eventos del partido (esto es un ejemplo simplificado)
        for minuto in range(40):  # 40 minutos en lugar de 90
            evento = random.random()
            if evento < 0.05:  # 5% de probabilidad de un gol
                if random.random() < 0.5:
                    puntuacion_equipo1 += 1
                    self.eventos.append((minuto, self.equipo1.nombre, "GOL"))
                else:
                    puntuacion_equipo2 += 1
                    self.eventos.append((minuto, self.equipo2.nombre, "GOL"))
            elif evento < 0.1:  # 5% de probabilidad de una tarjeta
                if random.random() < 0.5:
                    self.eventos.append((minuto, self.equipo1.nombre, "TARJETA"))
                else:
                    self.eventos.append((minuto, self.equipo2.nombre, "TARJETA"))

        self.resultado = (puntuacion_equipo1, puntuacion_equipo2)
        return self.resultado

    def obtener_eventos(self):
        """Devolver la lista de eventos del partido"""
        return self.eventos
