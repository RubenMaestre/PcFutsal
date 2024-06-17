# src/core/equipo.py

from .jugador import Jugador

class Equipo:
    def __init__(self, nombre, presupuesto):
        self.nombre = nombre
        self.presupuesto = presupuesto
        self.jugadores = []
        self.tacticas = "Predeterminada"  # Placeholder para tácticas

    def agregar_jugador(self, jugador):
        """Añadir un jugador al equipo"""
        if isinstance(jugador, Jugador):
            self.jugadores.append(jugador)

    def eliminar_jugador(self, nombre_jugador):
        """Eliminar un jugador del equipo por nombre"""
        self.jugadores = [jugador for jugador in self.jugadores if jugador.nombre_corto != nombre_jugador]

    def actualizar_presupuesto(self, cantidad):
        """Actualizar el presupuesto del equipo"""
        self.presupuesto += cantidad

    def establecer_tacticas(self, tacticas):
        """Establecer las tácticas del equipo"""
        self.tacticas = tacticas

    def obtener_jugadores(self):
        """Obtener la lista de jugadores en el equipo"""
        return self.jugadores
