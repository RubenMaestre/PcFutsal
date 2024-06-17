# src/core/cargar_jugadores.py

import csv
from src.core.jugador import Jugador
from src.core.equipo import Equipo
from src.core.liga import Liga

def cargar_jugadores(ruta_archivo):
    jugadores = []
    with open(ruta_archivo, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            jugador = Jugador(
                id_jugador=row['player_id'],
                url_jugador=None,
                version_fifa=None,
                actualizacion_fifa=None,
                actualizacion_al_dia=None,
                nombre_corto=row['player_name'],
                nombre_largo=row['player_name'],
                posiciones_jugador=row['position'],
                general=int(row['overall']),
                potencial=int(row['potential']),
                valor_eur=int(row['value_eur']),
                salario_eur=int(row['wage_eur']),
                edad=int(row['age']),
                fecha_nacimiento=None,
                altura_cm=None,
                peso_kg=None,
                id_equipo_club=None,
                nombre_club=row['team_name'],
                id_liga=None,
                nombre_liga=None,
                nivel_liga=None,
                posicion_club=None,
                numero_camiseta_club=None,
                cedido_desde_club=None,
                fecha_ingreso_club=None,
                contrato_valido_hasta=None,
                id_nacionalidad=None,
                nombre_nacionalidad=None,
                id_equipo_nacional=None,
                posicion_nacion=None,
                numero_camiseta_nacion=None,
                pie_preferido=row['preferred_foot'],
                pie_debil=None,
                movimientos_habilidad=int(row['skill_moves']),
                reputacion_internacional=None,
                tasa_trabajo=None,
                tipo_cuerpo=None,
                cara_real=None,
                clausula_rescision_eur=None,
                etiquetas_jugador=None,
                rasgos_jugador=None,
                ritmo=int(row['pace']),
                tiro=int(row['shooting']),
                pase=int(row['passing']),
                regate=int(row['dribbling']),
                defensa=int(row['defending']),
                fisico=int(row['physic']),
                ataque_centros=None,
                ataque_definicion=None,
                ataque_precision_cabeza=None,
                ataque_pase_corto=None,
                ataque_voleas=None,
                habilidad_regate=None,
                habilidad_efecto=None,
                habilidad_precision_tiro_libre=None,
                habilidad_pase_largo=None,
                habilidad_control_balon=None,
                movimiento_aceleracion=None,
                movimiento_velocidad_sprint=None,
                movimiento_agilidad=None,
                movimiento_reacciones=None,
                movimiento_equilibrio=None,
                potencia_fuerza_tiro=None,
                potencia_salto=None,
                potencia_resistencia=None,
                potencia_fuerza=None,
                potencia_tiros_lejanos=None,
                mentalidad_agresion=None,
                mentalidad_intercepciones=None,
                mentalidad_posicionamiento=None,
                mentalidad_vision=None,
                mentalidad_penaltis=None,
                mentalidad_compostura=None,
                defensa_marcaje=None,
                defensa_entrada=None,
                defensa_entrada_deslizante=None,
                portero_estirada=None,
                portero_manejo=None,
                portero_saque=None,
                portero_colocacion=None,
                portero_reflejos=None,
                portero_velocidad=None,
                portero=None,
                cierre=None,
                ala_cierre=None,
                ala_izquierda=None,
                ala_derecha=None,
                ala_pivot=None,
                pivot=None,
                universal=None,
                estrellas_talento=float(row['talent_stars'])
            )
            jugadores.append(jugador)
    return jugadores

def asignar_jugadores_a_equipos(jugadores, equipos):
    equipo_dict = {equipo.nombre: equipo for equipo in equipos}
    for jugador in jugadores:
        if jugador.nombre_club in equipo_dict:
            equipo_dict[jugador.nombre_club].agregar_jugador(jugador)
