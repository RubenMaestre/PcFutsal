# src/core/evento.py

class Evento:
    def __init__(self, descripcion, tipo_evento, impacto):
        self.descripcion = descripcion
        self.tipo_evento = tipo_evento  # Por ejemplo, 'lesion', 'transferencia', 'mejora'
        self.impacto = impacto  # Por ejemplo, {'jugador': 'nombre', 'duracion': '2 semanas'}

    def aplicar_evento(self, equipo):
        """Aplicar el impacto del evento en el equipo"""
        # Implementar la lógica para aplicar el impacto del evento
        pass
