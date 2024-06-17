# src/core/despido.py

class Despido:
    def __init__(self, puede_ser_despedido):
        self.puede_ser_despedido = puede_ser_despedido

    def verificar_despido(self, rendimiento_equipo):
        if self.puede_ser_despedido and rendimiento_equipo < self.umbral_rendimiento():
            return True
        return False

    def umbral_rendimiento(self):
        return 30  # Ejemplo: porcentaje de puntos mínimos para evitar el despido
