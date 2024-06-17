# src/utils.py

import csv
import json
import pygame
import math

# Funciones para Manejo de Archivos
def leer_csv(ruta_archivo):
    """Leer un archivo CSV y devolver una lista de diccionarios"""
    data = []
    with open(ruta_archivo, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def escribir_csv(ruta_archivo, datos, encabezados):
    """Escribir datos en un archivo CSV"""
    with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(datos)

def leer_json(ruta_archivo):
    """Leer un archivo JSON y devolver los datos"""
    with open(ruta_archivo, mode='r', encoding='utf-8') as file:
        return json.load(file)

def escribir_json(ruta_archivo, datos):
    """Escribir datos en un archivo JSON"""
    with open(ruta_archivo, mode='w', encoding='utf-8') as file:
        json.dump(datos, file, indent=4)

# Funciones para Manipulación de Imágenes
def cargar_imagen(ruta_archivo):
    """Cargar una imagen y devolver una superficie de Pygame"""
    return pygame.image.load(ruta_archivo)

def escalar_imagen(imagen, ancho, alto):
    """Escalar una imagen a las dimensiones especificadas"""
    return pygame.transform.scale(imagen, (ancho, alto))

def rotar_imagen(imagen, angulo):
    """Rotar una imagen en el ángulo especificado"""
    return pygame.transform.rotate(imagen, angulo)

# Funciones de Conversión y Formato
def rgb_a_hex(rgb):
    """Convertir un color RGB a formato hexadecimal"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def hex_a_rgb(color_hex):
    """Convertir un color hexadecimal a formato RGB"""
    color_hex = color_hex.lstrip('#')
    return tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))

def formatear_texto(texto, fuente, tamano, color):
    """Formatear texto para renderizar en pantalla"""
    fuente = pygame.font.Font(fuente, tamano)
    return fuente.render(texto, True, color)

# Funciones Matemáticas Comunes
def calcular_distancia(punto1, punto2):
    """Calcular la distancia entre dos puntos"""
    return math.sqrt((punto2[0] - punto1[0]) ** 2 + (punto2[1] - punto1[1]) ** 2)

def calcular_angulo(punto1, punto2):
    """Calcular el ángulo entre dos puntos"""
    return math.degrees(math.atan2(punto2[1] - punto1[1], punto2[0] - punto1[0]))

def guardar_juego(estado, nombre_archivo='savegame.json'):
    """Guardar el estado del juego en un archivo JSON"""
    with open(nombre_archivo, 'w') as file:
        json.dump(estado, file, indent=4)

def cargar_juego(nombre_archivo='savegame.json'):
    """Cargar el estado del juego desde un archivo JSON"""
    with open(nombre_archivo, 'r') as file:
        return json.load(file)
