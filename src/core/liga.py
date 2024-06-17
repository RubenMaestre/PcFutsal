# src/core/liga.py

class Liga:
    def __init__(self, nombre, pais, nivel, equipos=None):
        self.nombre = nombre
        self.pais = pais
        self.nivel = nivel
        self.equipos = equipos if equipos else []

    def agregar_equipo(self, equipo):
        """Añadir un equipo a la liga"""
        self.equipos.append(equipo)

    def eliminar_equipo(self, equipo):
        """Eliminar un equipo de la liga"""
        if equipo in self.equipos:
            self.equipos.remove(equipo)
        else:
            print(f"El equipo {equipo} no se encuentra en la liga.")

    def obtener_equipos(self):
        """Obtener la lista de equipos en la liga"""
        return self.equipos
