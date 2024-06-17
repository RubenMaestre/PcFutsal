# src/core/simular_partidos.py

import random

def simular_partido(equipo1, equipo2):
    """Simular un partido entre dos equipos"""
    puntuacion1 = random.randint(0, 5)
    puntuacion2 = random.randint(0, 5)
    return puntuacion1, puntuacion2

def jugar_jornada_liga(calendario, clasificacion):
    """Jugar una jornada de la liga"""
    resultados = []
    for partido in calendario:
        equipo1, equipo2 = partido
        puntuacion1, puntuacion2 = simular_partido(equipo1, equipo2)
        resultados.append((equipo1, equipo2, puntuacion1, puntuacion2))
        clasificacion[equipo1.nombre] += 3 if puntuacion1 > puntuacion2 else 1 if puntuacion1 == puntuacion2 else 0
        clasificacion[equipo2.nombre] += 3 if puntuacion2 > puntuacion1 else 1 if puntuacion1 == puntuacion2 else 0
    return resultados
