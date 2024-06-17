# src/core/juego.py

from datetime import datetime, timedelta
from src.core.cargar_equipos import cargar_equipos, asignar_equipos_a_ligas
from src.core.competicion import Competicion, Copa, SuperCopa
from src.core.simular_partidos import jugar_jornada_liga
from src.core.calendario_liga import CalendarioLiga
from src.core.calendario_copa import CalendarioCopa
from src.core.despido import Despido
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
        for nombre_liga, competicion in self.ligas.items():
            numero_jornada = (self.fecha_actual - datetime(2024, 7, 1)).days // 7
            if numero_jornada < len(competicion.calendario):
                print(f"Jugando la jornada {numero_jornada + 1} de {nombre_liga}")
                resultados = competicion.jugar_jornada(numero_jornada)
                for resultado in resultados:
                    equipo1, equipo2, puntuacion1, puntuacion2 = resultado
                    print(f"{equipo1.nombre} {puntuacion1} - {puntuacion2} {equipo2.nombre}")
                competicion.mostrar_clasificacion()
            self.verificar_eventos(competicion, numero_jornada)
        self.verificar_despido()

    def verificar_eventos(self, competicion, numero_jornada):
        # Ejemplo de evento: oferta de fichaje
        if numero_jornada % 4 == 0:  # Cada 4 semanas
            for equipo in competicion.liga.obtener_equipos():
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
    equipos = cargar_equipos('data/equipos.csv')
    ligas_dict = asignar_equipos_a_ligas(equipos)
    
    ligas = {
        "Primera División": Competicion(ligas_dict['Primera División']),
        "Segunda División": Competicion(ligas_dict['Segunda División'])
    }

    fecha_inicio = datetime(2024, 7, 1)
    juego = Juego(fecha_inicio, ligas, equipo_seleccionado, puede_ser_despedido, modo_juego)
    juego.ejecutar()

if __name__ == "__main__":
    principal()
