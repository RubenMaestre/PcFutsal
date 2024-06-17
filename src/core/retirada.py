# src/core/retirada.py

import random

def deberia_retirarse(jugador):
    """Determinar si un jugador debe retirarse basado en varios factores"""
    edad = jugador.edad
    posicion = jugador.posicion
    lesiones = jugador.lesion
    partidos_jugados = jugador.partidos_jugados_ultima_temporada
    confianza_entrenador = jugador.confianza_entrenador

    if edad >= 40:
        if posicion == "portero":
            return random.random() < 0.7
        elif posicion == "universal":
            return random.random() < 0.5
        else:
            return random.random() < 0.2

    if edad >= 35:
        if lesiones and lesiones.severidad in ['grave', 'moderada']:
            return random.random() < 0.5
        if partidos_jugados < 10:
            return random.random() < 0.3
        if not confianza_entrenador:
            return random.random() < 0.2

    if edad >= 34:
        if posicion in ["ala izquierda", "ala derecha", "ala-cierre"] and not confianza_entrenador:
            return random.random() < 0.4
        if lesiones and lesiones.severidad in ['grave', 'moderada']:
            return random.random() < 0.3

    if edad >= 33:
        if posicion in ["ala izquierda", "ala derecha", "ala-cierre"]:
            return random.random() < 0.2
        if lesiones and lesiones.severidad in ['grave', 'moderada']:
            return random.random() < 0.1

    return False
