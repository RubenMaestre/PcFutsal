# src/core/calendario_liga.py

class CalendarioLiga:
    def __init__(self, equipos):
        self.equipos = equipos
        self.calendario = []

    def generar_calendario(self):
        """Generar el calendario de partidos para la liga"""
        self.calendario = []
        num_equipos = len(self.equipos)
        rondas = num_equipos - 1
        for num_ronda in range(rondas):
            partidos_ronda = []
            for i in range(num_equipos // 2):
                equipo1 = self.equipos[i]
                equipo2 = self.equipos[num_equipos - 1 - i]
                partidos_ronda.append((equipo1, equipo2))
            self.equipos.insert(1, self.equipos.pop())  # Rotar equipos
            self.calendario.append(partidos_ronda)
        # Añadir partidos de vuelta
        partidos_vuelta = [[(partido[1], partido[0]) for partido in partidos_ronda] for partidos_ronda in self.calendario]
        self.calendario.extend(partidos_vuelta)
        return self.calendario

    def mostrar_calendario(self):
        """Mostrar el calendario de partidos"""
        for i, partidos_ronda in enumerate(self.calendario):
            print(f"Ronda {i+1}")
            for partido in partidos_ronda:
                print(f"{partido[0].nombre} vs {partido[1].nombre}")
            print()
