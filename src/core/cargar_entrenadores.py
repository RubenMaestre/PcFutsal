# src/core/cargar_entrenadores.py

import csv
from src.core.entrenador import Entrenador

def cargar_entrenadores(ruta_archivo):
    entrenadores = []
    with open(ruta_archivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entrenador = Entrenador(
                id=row['id'],
                nombre=row['name'],
                sistema_preferido=row['preferred_system'],
                sistemas_secundarios=row['secondary_systems'].split(','),
                tipos_jugador_preferidos=row['preferred_player_types'].split(' and '),
                control_vestuario=row['control_vestuario'],
                cantera=row['cantera'],
                aguante=row['aguante'],
                dejar_aconsejar=row['dejar_aconsejar']
            )
            entrenadores.append(entrenador)
    return entrenadores
