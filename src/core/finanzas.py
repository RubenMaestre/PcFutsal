# src/core/finanzas.py

class Finanzas:
    def __init__(self, presupuesto):
        self.presupuesto = presupuesto
        self.ingresos = 0
        self.gastos = 0

    def agregar_ingreso(self, cantidad):
        """Añadir ingresos al presupuesto"""
        self.ingresos += cantidad
        self.presupuesto += cantidad

    def agregar_gasto(self, cantidad):
        """Añadir gastos al presupuesto"""
        self.gastos += cantidad
        self.presupuesto -= cantidad

    def generar_reporte_financiero(self):
        """Generar un reporte financiero"""
        return {
            "Presupuesto": self.presupuesto,
            "Ingresos": self.ingresos,
            "Gastos": self.gastos
        }
