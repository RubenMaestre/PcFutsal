# src/core/entrenador.py

class Entrenador:
    def __init__(self, id, nombre, sistema_preferido, sistemas_secundarios, tipos_jugador_preferidos, control_vestuario, cantera, aguante, dejar_aconsejar):
        self.id = id
        self.nombre = nombre
        self.sistema_preferido = sistema_preferido
        self.sistemas_secundarios = sistemas_secundarios
        self.tipos_jugador_preferidos = tipos_jugador_preferidos
        self.control_vestuario = control_vestuario
        self.cantera = cantera
        self.aguante = aguante
        self.dejar_aconsejar = dejar_aconsejar
