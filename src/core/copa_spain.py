# src/core/copa_spain.py

from core.calendario_copa_spain import CalendarioCopaSpain

class CopaEspaña:
    def __init__(self, nombre, equipos=None):
        self.nombre = nombre
        self.equipos = equipos if equipos else []
        self.calendario = None

    def agregar_equipo(self, equipo):
        """Añadir un equipo a la Copa de España"""
        self.equipos.append(equipo)

    def eliminar_equipo(self, equipo):
        """Eliminar un equipo de la Copa de España"""
        if equipo in self.equipos:
            self.equipos.remove(equipo)
        else:
            print(f"El equipo {equipo} no se encuentra en la copa.")

    def obtener_equipos(self):
        """Obtener la lista de equipos en la Copa de España"""
        return self.equipos

    def generar_calendario(self):
        """Generar el calendario de la Copa de España"""
        if len(self.equipos) != 8:
            raise ValueError("La Copa de España debe tener exactamente 8 equipos")
        self.calendario = CalendarioCopaSpain(self.equipos).generar_calendario()
        return self.calendario

    def jugar_copa(self):
        """Jugar el torneo completo de la Copa de España"""
        if not self.calendario:
            self.generar_calendario()
        return CalendarioCopaSpain(self.equipos).jugar_torneo()
