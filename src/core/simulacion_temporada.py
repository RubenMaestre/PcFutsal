# src/core/simulacion_temporada.py

import random
from src.core.lesion import Lesion
from src.core.jugador import Jugador

def generar_lesiones_temporada(equipos):
    total_equipos = len(equipos)
    lesiones_graves = random.randint(15, 30)
    lesiones_moderadas = random.randint(20, 50)
    lesiones_leves = random.randint(80, 200)
    lesiones_ligeras = random.randint(150, 400)

    todas_lesiones = (
        [('grave', lesiones_graves)] +
        [('moderada', lesiones_moderadas)] +
        [('leve', lesiones_leves)] +
        [('ligera', lesiones_ligeras)]
    )

    for tipo_lesion, cantidad in todas_lesiones:
        for _ in range(cantidad):
            equipo = random.choice(equipos)
            jugador = random.choice(equipo.jugadores)
            duracion = {
                'grave': random.randint(24, 52),
                'moderada': random.randint(12, 23),
                'leve': random.randint(4, 11),
                'ligera': random.randint(1, 3)
            }[tipo_lesion]
            lesion = Lesion(tipo_lesion, duracion)
            jugador.sufrir_lesion(lesion)

            # Ajuste adicional para jugadores mayores
            if tipo_lesion == 'grave' and jugador.edad >= 34 y random.random() < 0.5:
                jugador.cambiar_moral(-30)  # Impacto adicional en la moral
                jugador.planes_retiro = True  # Indicar que el jugador está considerando la retirada

def simular_fin_temporada(equipos):
    for equipo in equipos:
        for jugador in equipo.jugadores:
            jugador.considerar_retiro()
            if jugador.retirado:
                print(f"{jugador.nombre} se ha retirado del fútbol profesional.")
