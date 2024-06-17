import csv
import json
import pygame
import math

# Funciones para Manejo de Archivos
def read_csv(file_path):
    """Leer un archivo CSV y devolver una lista de diccionarios"""
    data = []
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def write_csv(file_path, data, fieldnames):
    """Escribir datos en un archivo CSV"""
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def read_json(file_path):
    """Leer un archivo JSON y devolver los datos"""
    with open(file_path, mode='r', encoding='utf-8') as file:
        return json.load(file)

def write_json(file_path, data):
    """Escribir datos en un archivo JSON"""
    with open(file_path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Funciones para Manipulación de Imágenes
def load_image(file_path):
    """Cargar una imagen y devolver una superficie de Pygame"""
    return pygame.image.load(file_path)

def scale_image(image, width, height):
    """Escalar una imagen a las dimensiones especificadas"""
    return pygame.transform.scale(image, (width, height))

def rotate_image(image, angle):
    """Rotar una imagen en el ángulo especificado"""
    return pygame.transform.rotate(image, angle)

# Funciones de Conversión y Formato
def rgb_to_hex(rgb):
    """Convertir un color RGB a formato hexadecimal"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def hex_to_rgb(hex_color):
    """Convertir un color hexadecimal a formato RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def format_text(text, font, size, color):
    """Formatear texto para renderizar en pantalla"""
    font = pygame.font.Font(font, size)
    return font.render(text, True, color)

# Funciones Matemáticas Comunes
def calculate_distance(point1, point2):
    """Calcular la distancia entre dos puntos"""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def calculate_angle(point1, point2):
    """Calcular el ángulo entre dos puntos"""
    return math.degrees(math.atan2(point2[1] - point1[1], point2[0] - point1[0]))

def save_game(state, filename='savegame.json'):
    """Guardar el estado del juego en un archivo JSON"""
    with open(filename, 'w') as file:
        json.dump(state, file, indent=4)

def load_game(filename='savegame.json'):
    """Cargar el estado del juego desde un archivo JSON"""
    with open(filename, 'r') as file:
        return json.load(file)
