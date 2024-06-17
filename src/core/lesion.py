# src/core/lesion.py

import random

class Lesion:
    def __init__(self, severidad, duracion):
        self.severidad = severidad  # 'grave', 'moderada', 'leve', 'ligera'
        self.duracion = duracion  # Duración en semanas

    @staticmethod
    def generar_lesion_aleatoria():
        opciones_severidad = {
            'grave': (24, 52),  # Lesión muy grave: 6-12 meses
            'moderada': (12, 23),  # Lesión grave: 3-6 meses
            'leve': (4, 11),  # Lesión importante: 1-3 meses
            'ligera': (1, 3)  # Lesión leve: 1-4 semanas
        }

        severidad = random.choices(
            ['grave', 'moderada', 'leve', 'ligera'],
            [0.01, 0.05, 0.15, 0.79]  # Probabilidades ajustadas para la frecuencia de lesiones
        )[0]

        duracion = random.randint(*opciones_severidad[severidad])

        return Lesion(severidad, duracion)
