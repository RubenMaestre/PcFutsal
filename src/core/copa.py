# src/core/copa.py

class Copa:
    def __init__(self, nombre, pais, equipos=None):
        self.nombre = nombre
        self.pais = pais
        self.equipos = equipos if equipos else []

    def agregar_equipo(self, equipo):
        """Añadir un equipo a la copa"""
        self.equipos.append(equipo)

    def eliminar_equipo(self, equipo):
        """Eliminar un equipo de la copa"""
        if equipo in self.equipos:
            self.equipos.remove(equipo)
        else:
            print(f"El equipo {equipo} no se encuentra en la copa.")

    def obtener_equipos(self):
        """Obtener la lista de equipos en la copa"""
        return self.equipos
