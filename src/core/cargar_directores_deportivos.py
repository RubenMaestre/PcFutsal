# src/core/cargar_directores_deportivos.py

import csv
from src.core.director_deportivo import DirectorDeportivo

def cargar_directores_deportivos(ruta_archivo):
    directores_deportivos = []
    with open(ruta_archivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            director_deportivo = DirectorDeportivo(
                id=row['id'],
                nombre=row['name'],
                tipos_jugador_preferidos=row['preferred_player_types'].split(' and '),
                tipos_entrenador_preferidos=row['preferred_coach_types'].split(' and ')
            )
            directores_deportivos.append(director_deportivo)
    return directores_deportivos
