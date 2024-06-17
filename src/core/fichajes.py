# src/core/fichajes.py

class Fichaje:
    def __init__(self, jugador, equipo_origen, equipo_destino, cuota_transferencia, terminos_contrato):
        self.jugador = jugador
        self.equipo_origen = equipo_origen
        self.equipo_destino = equipo_destino
        self.cuota_transferencia = cuota_transferencia
        self.terminos_contrato = terminos_contrato

    def ejecutar_fichaje(self):
        """Ejecutar la transferencia de un jugador"""
        if self.equipo_destino.presupuesto >= self.cuota_transferencia:
            self.equipo_origen.eliminar_jugador(self.jugador.nombre)
            self.equipo_destino.agregar_jugador(self.jugador)
            self.equipo_origen.finanzas.agregar_ingreso(self.cuota_transferencia)
            self.equipo_destino.finanzas.agregar_gasto(self.cuota_transferencia)
            return True
        else:
            return False
