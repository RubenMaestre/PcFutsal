# src/core/cargar_equipos.py

import csv
from src.core.equipo import Equipo

def cargar_equipos(file_path):
    equipos = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    equipo = Equipo(
                        id_equipo=row['id_equipo'],
                        nombre_equipo=row['nombre_equipo'],
                        pais=row['pais'],
                        liga=row['liga'],
                        presupuesto=int(row['budget'])
                    )
                    equipos.append(equipo)
                except KeyError as e:
                    print(f"Error: Columna no encontrada en CSV: {e}")
                except ValueError as e:
                    print(f"Error: Valor incorrecto en CSV: {e}")
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
    return equipos

def asignar_equipos_a_ligas(equipos):
    ligas_dict = {
        "Primera División": [],
        "Segunda División": []
    }
    for equipo in equipos:
        if equipo.liga == "Primera División":
            ligas_dict["Primera División"].append(equipo)
        elif equipo.liga == "Segunda División":
            ligas_dict["Segunda División"].append(equipo)
    return ligas_dict
