# src/core/competicion.py

import random
from src.core.estadisticas_jugadores import EstadisticasJugador
from src.core.estadisticas_equipos import EstadisticasEquipo
from src.core.calendario_liga import CalendarioLiga
from src.core.calendario_copa import CalendarioCopa
from src.core.copa_spain import CalendarioCopaSpain
from src.core.simular_partidos import simular_partido

class Competicion:
    def __init__(self, liga, puntos_por_victoria=3, puntos_por_empate=1, puntos_por_derrota=0):
        self.liga = liga
        self.puntos_por_victoria = puntos_por_victoria
        self.puntos_por_empate = puntos_por_empate
        self.puntos_por_derrota = puntos_por_derrota
        self.clasificacion = {equipo: 0 for equipo in liga.obtener_equipos()}
        self.estadisticas_equipos = {equipo.nombre: EstadisticasEquipo(equipo.nombre) for equipo in liga.obtener_equipos()}
        self.calendario = CalendarioLiga(liga.obtener_equipos()).generar_calendario()
        self.campeon_liga = None
        self.campeon_copa_rey = None
        self.subcampeon_copa_rey = None

    def registrar_partido(self, equipo1, equipo2, puntuacion1, puntuacion2):
        """Registrar el resultado de un partido"""
        self.estadisticas_equipos[equipo1.nombre].actualizar_estadisticas(puntuacion1, puntuacion2)
        self.estadisticas_equipos[equipo2.nombre].actualizar_estadisticas(puntuacion2, puntuacion1)
        if puntuacion1 > puntuacion2:
            self.clasificacion[equipo1] += self.puntos_por_victoria
            self.clasificacion[equipo2] += self.puntos_por_derrota
        elif puntuacion1 < puntuacion2:
            self.clasificacion[equipo1] += self.puntos_por_derrota
            self.clasificacion[equipo2] += self.puntos_por_victoria
        else:
            self.clasificacion[equipo1] += self.puntos_por_empate
            self.clasificacion[equipo2] += self.puntos_por_empate

    def jugar_jornada(self, numero_jornada):
        """Jugar una jornada de la liga"""
        resultados = []
        for partido in self.calendario[numero_jornada]:
            equipo1, equipo2 = partido
            puntuacion1, puntuacion2 = simular_partido(equipo1, equipo2)
            resultados.append((equipo1, equipo2, puntuacion1, puntuacion2))
            self.registrar_partido(equipo1, equipo2, puntuacion1, puntuacion2)
        return resultados

    def obtener_clasificacion(self):
        """Obtener la clasificación de la liga"""
        clasificacion_ordenada = sorted(self.clasificacion.items(), key=lambda x: x[1], reverse=True)
        lista_clasificacion = [(equipo.nombre, puntos) for equipo, puntos in clasificacion_ordenada]
        return lista_clasificacion

    def mostrar_clasificacion(self):
        """Mostrar la clasificación de la liga"""
        clasificacion = self.obtener_clasificacion()
        print("Clasificación:")
        for posicion, (nombre_equipo, puntos) in enumerate(clasificacion, start=1):
            print(f"{posicion}. {nombre_equipo} - {puntos} puntos")

    def manejar_ascensos_descensos(self, num_ascenso, num_descenso):
        """Manejar los ascensos y descensos de la liga"""
        equipos_ordenados = self.obtener_clasificacion()
        equipos_ascendidos = equipos_ordenados[:num_ascenso]
        equipos_descendidos = equipos_ordenados[-num_descenso:]
        return equipos_ascendidos, equipos_descendidos

    def jugar_playoffs_primera(self):
        """Jugar los playoffs de la Primera División"""
        clasificacion = self.obtener_clasificacion()
        equipos_playoff = clasificacion[:8]
        emparejamientos = [
            (equipos_playoff[0][0], equipos_playoff[7][0]),
            (equipos_playoff[1][0], equipos_playoff[6][0]),
            (equipos_playoff[2][0], equipos_playoff[5][0]),
            (equipos_playoff[3][0], equipos_playoff[4][0])
        ]
        self.campeon_liga = self.jugar_ronda_eliminatoria(emparejamientos)
        return self.campeon_liga

    def jugar_playoffs_segunda(self):
        """Jugar los playoffs de la Segunda División"""
        clasificacion = self.obtener_clasificacion()
        equipos_playoff = clasificacion[1:5]  # Equipos clasificados del 2 al 5
        emparejamientos = [
            (equipos_playoff[0][0], equipos_playoff[3][0]),  # 2 vs 5
            (equipos_playoff[1][0], equipos_playoff[2][0])   # 3 vs 4
        ]
        ganadores = self.jugar_ronda_eliminatoria(emparejamientos)
        final_playoff = [(ganadores[0], ganadores[1])]
        return self.jugar_ronda_eliminatoria(final_playoff)

    def jugar_ronda_eliminatoria(self, emparejamientos):
        """Jugar una ronda eliminatoria de los playoffs"""
        siguiente_ronda = []
        for equipo1, equipo2 in emparejamientos:
            victorias_equipo1, victorias_equipo2 = 0, 0
            for _ in range(3):  # Mejor de 3 partidos
                puntuacion1, puntuacion2 = simular_partido(equipo1, equipo2)
                if puntuacion1 > puntuacion2:
                    victorias_equipo1 += 1
                else:
                    victorias_equipo2 += 1
                if victorias_equipo1 == 2 or victorias_equipo2 == 2:
                    break
            siguiente_ronda.append(equipo1 if victorias_equipo1 == 2 else equipo2)
        if len(siguiente_ronda) > 1:
            return self.jugar_ronda_eliminatoria([(siguiente_ronda[i], siguiente_ronda[i+1]) for i in range(0, len(siguiente_ronda), 2)])
        return siguiente_ronda[0]  # Ganador del playoff

    def jugar_copa_espana(self):
        """Jugar el torneo de la Copa de España"""
        if len(self.liga.obtener_equipos()) != 8:
            raise ValueError("La Copa de España debe tener exactamente 8 equipos")
        calendario_copa = CalendarioCopaSpain(self.liga.obtener_equipos())
        ganador = calendario_copa.jugar_torneo()
        return ganador

    def jugar_copa_del_rey(self):
        """Jugar el torneo de la Copa del Rey"""
        copa_del_rey = Copa(self.liga)
        ganador_copa = copa_del_rey.jugar_copa()
        self.campeon_copa_rey = ganador_copa
        return ganador_copa

class Copa:
    def __init__(self, copa):
        self.copa = copa
        self.calendario = CalendarioCopa(copa.obtener_equipos()).generar_calendario()

    def jugar_ronda(self):
        """Jugar una ronda de la copa"""
        siguiente_ronda = []
        ganadores = []
        for equipo1, equipo2 in self.calendario:
            puntuacion1, puntuacion2 = simular_partido(equipo1, equipo2)
            ganadores.append(equipo1 if puntuacion1 > puntuacion2 else equipo2)
            siguiente_ronda.append((equipo1, equipo2, puntuacion1, puntuacion2))
        self.calendario = [(ganadores[i], ganadores[i+1]) for i in range(0, len(ganadores) - 1, 2)]
        return siguiente_ronda

    def jugar_copa(self):
        """Jugar todo el torneo de la copa"""
        rondas = []
        while len(self.calendario) > 1:
            rondas.append(self.jugar_ronda())
        ganador_copa = self.calendario[0][0]
        return ganador_copa  # El ganador de la copa

    def simular_partido(self, equipo1, equipo2):
        """Simular un partido de la copa"""
        return simular_partido(equipo1, equipo2)

class SuperCopa:
    def __init__(self, competicion):
        self.competicion = competicion

    def determinar_equipos_supercopa(self):
        """Determinar los equipos que jugarán la SuperCopa"""
        campeon_liga = self.competicion.campeon_liga
        campeon_copa = self.competicion.campeon_copa_rey
        if campeon_liga == campeon_copa:
            subcampeon_copa = self.competicion.subcampeon_copa_rey
            return campeon_liga, subcampeon_copa
        return campeon_liga, campeon_copa

    def jugar_partido(self):
        """Jugar el partido de la SuperCopa"""
        equipo1, equipo2 = self.determinar_equipos_supercopa()
        puntuacion1, puntuacion2 = simular_partido(equipo1, equipo2)
        return equipo1 if puntuacion1 > puntuacion2 else equipo2

    def simular_partido(self, equipo1, equipo2):
        """Simular un partido de la SuperCopa"""
        return simular_partido(equipo1, equipo2)
