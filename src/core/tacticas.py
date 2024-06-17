# src/core/tacticas.py

class Tacticas:
    def __init__(self, formacion, estrategia_ofensiva, estrategia_defensiva, roles):
        self.formacion = formacion  # Ejemplo: "4-4-2", "3-5-2"
        self.estrategia_ofensiva = estrategia_ofensiva  # Ejemplo: "posesión", "contraataque"
        self.estrategia_defensiva = estrategia_defensiva  # Ejemplo: "presión alta", "bloque bajo"
        self.roles = roles  # Diccionario con roles específicos para jugadores (ej. {"delantero": "hombre objetivo", "centrocampista": "creador de juego"})

    def establecer_formacion(self, formacion):
        self.formacion = formacion

    def establecer_estrategia_ofensiva(self, estrategia):
        self.estrategia_ofensiva = estrategia

    def establecer_estrategia_defensiva(self, estrategia):
        self.estrategia_defensiva = estrategia

    def establecer_roles(self, roles):
        self.roles = roles
