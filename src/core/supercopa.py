# src/core/supercopa.py

class Supercopa:
    def __init__(self, nombre, pais, campeon_liga, campeon_copa_rey, subcampeon_copa_rey):
        self.nombre = nombre
        self.pais = pais
        self.campeon_liga = campeon_liga
        self.campeon_copa_rey = campeon_copa_rey
        self.subcampeon_copa_rey = subcampeon_copa_rey

    def obtener_equipos(self):
        """Obtener los equipos que juegan la Supercopa"""
        if self.campeon_liga == self.campeon_copa_rey:
            return [self.campeon_liga, self.subcampeon_copa_rey]
        return [self.campeon_liga, self.campeon_copa_rey]
