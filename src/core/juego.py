# src/core/game.py

from datetime import datetime, timedelta
from proyecto_pcfutbol.manager.src.core.cargar_equipos import load_teams, assign_teams_to_leagues
from proyecto_pcfutbol.manager.src.core.competicion import Competencia, Copa, SuperCopa
from proyecto_pcfutbol.manager.src.core.simulador_partidos import jugar_jornada_liga
from proyecto_pcfutbol.manager.src.core.calendario_liga import LeagueSchedule
from proyecto_pcfutbol.manager.src.core.calendario_copa import CalendarioCopa
from core.despido import Despido
import random

class Juego:
    def __init__(self, fecha_inicio, ligas, equipo_seleccionado, puede_ser_despedido, modo_juego):
        self.fecha_actual = fecha_inicio
        self.ligas = ligas
        self.equipo_seleccionado = equipo_seleccionado
        self.despido = Despido(puede_ser_despedido)
        self.eventos = []
        self.modo_juego = modo_juego

    def avanzar_semana(self):
        self.fecha_actual += timedelta(weeks=1)
        print(f"Avanzando a la semana del {self.fecha_actual.strftime('%Y-%m-%d')}")
        self.manejar_eventos_semanales()

    def manejar_eventos_semanales(self):
        for nombre_liga, competencia in self.ligas.items():
            numero_jornada = (self.fecha_actual - datetime(2024, 7, 1)).days // 7
            if numero_jornada < len(competencia.calendario):
                print(f"Jugando la jornada {numero_jornada + 1} de {nombre_liga}")
                resultados = competencia.jugar_jornada(numero_jornada)
                for resultado in resultados:
                    equipo1, equipo2, puntuacion1, puntuacion2 = resultado
                    print(f"{equipo1.nombre} {puntuacion1} - {puntuacion2} {equipo2.nombre}")
                competencia.mostrar_clasificacion()
            self.verificar_eventos(competencia, numero_jornada)
        self.verificar_despido()

    def verificar_eventos(self, competencia, numero_jornada):
        # Ejemplo de evento: oferta de fichaje
        if numero_jornada % 4 == 0:  # Cada 4 semanas
            for equipo in competencia.liga.obtener_equipos():
                if random.random() < 0.1:  # 10% de probabilidad de oferta de fichaje
                    evento = f"Oferta de fichaje para {equipo.nombre}"
                    self.interrumpir_por_evento(evento)

    def verificar_despido(self):
        if self.despido.puede_ser_despedido:
            rendimiento_equipo = self.ligas['Primera División'].estadisticas_equipos[self.equipo_seleccionado['team_name']].puntos  # Ejemplo para Primera División
            if self.despido.verificar_despido(rendimiento_equipo):
                print(f"Has sido despedido del equipo {self.equipo_seleccionado['team_name']}")

    def interrumpir_por_evento(self, evento):
        print(f"Interrupción: {evento}")
        # Lógica para manejar la interrupción (ej. ofertas de jugadores, lesiones, etc.)

    def ejecutar(self):
        while True:
            comando = input("Presiona Enter para avanzar una semana, 'salir' para salir: ")
            if comando == 'salir':
                break
            self.avanzar_semana()

def principal(equipo_seleccionado, puede_ser_despedido, modo_juego):
    equipos = load_teams('data/teams.csv')
    ligas_dict = assign_teams_to_leagues(equipos)
    
    ligas = {
        "Primera División": Competencia(ligas_dict['Primera División']),
        "Segunda División": Competencia(ligas_dict['Segunda División'])
    }

    fecha_inicio = datetime(2024, 7, 1)
    juego = Juego(fecha_inicio, ligas, equipo_seleccionado, puede_ser_despedido, modo_juego)
    juego.ejecutar()

if __name__ == "__main__":
    principal()

