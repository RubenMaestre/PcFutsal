# src/core/cargar_equipos.py

import csv
from src.core.equipo import Equipo
from src.core.liga import Liga

def cargar_equipos(ruta_archivo):
    equipos = []
    with open(ruta_archivo, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            equipo = Equipo(row['team_name'], int(row['budget']))
            equipos.append((equipo, row['country'], row['league']))
    return equipos

def asignar_equipos_a_ligas(equipos):
    ligas = {}
    for equipo, pais, nombre_liga in equipos:
        if nombre_liga not in ligas:
            ligas[nombre_liga] = Liga(nombre_liga, pais, 1)
        ligas[nombre_liga].agregar_equipo(equipo)
    return ligas
