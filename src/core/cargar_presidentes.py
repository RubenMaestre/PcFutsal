# src/core/presidentes.py

import csv
from src.core.presidente import Presidente

def cargar_presidentes(ruta_archivo):
    presidentes = []
    with open(ruta_archivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            presidente = Presidente(
                id=row['id'],
                nombre=row['name'],
                caracter=row['character'],
                paciencia=row['patience'],
                tipos_entrenadores_preferidos=row['preferred_coach_types'].split(' and '),
                tipos_directores_preferidos=row['preferred_director_types'].split(' and ')
            )
            presidentes.append(presidente)
    return presidentes
