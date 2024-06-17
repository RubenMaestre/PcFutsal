# src/ui/menu/inicio.py

import pygame
import settings
from datetime import datetime
from src.core.juego import Juego
from src.core.cargar_equipos import cargar_equipos, asignar_equipos_a_ligas
from src.core.competicion import Competicion
from src.core.estadisticas_equipos import EstadisticasEquipo  # Asegúrate de importar la clase correcta
from src.ui.ui_helpers import crear_boton, dibujar_botones
import utils

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores
BLANCO = settings.BLANCO
NEGRO = settings.NEGRO
ROJO = settings.ROJO

# Definir fuentes
FUENTE_BOTON = pygame.font.Font(None, 50)

# Cargar la imagen de fondo del menú
FONDO_MENU = pygame.image.load(settings.RUTA_RECURSOS + 'menu_background.png')

# Mostrar la animación de inicio
def mostrar_intro(pantalla):
    imagenes_intro = [settings.RUTA_RECURSOS + 'intro/frame1.png', settings.RUTA_RECURSOS + 'intro/frame2.png', settings.RUTA_RECURSOS + 'intro/frame3.png']
    for ruta_img in imagenes_intro:
        img = pygame.image.load(ruta_img)
        pantalla.blit(img, (0, 0))
        pygame.display.flip()
        pygame.time.wait(3000)  # Espera 3000 milisegundos entre frames

# Guardar el estado del juego
def guardar_estado(juego):
    estado = {
        'fecha': juego.fecha_actual.strftime('%Y-%m-%d'),
        'ligas': {
            nombre_liga: {
                'clasificacion': {
                    equipo.nombre: puntos
                    for equipo, puntos in competicion.clasificacion.items()
                },
                'estadisticas_equipos': {
                    nombre_equipo: {
                        'partidos_jugados': estadisticas_equipos.partidos_jugados,
                        'victorias': estadisticas_equipos.victorias,
                        'empates': estadisticas_equipos.empates,
                        'derrotas': estadisticas_equipos.derrotas,
                        'goles_a_favor': estadisticas_equipos.goles_a_favor,
                        'goles_en_contra': estadisticas_equipos.goles_en_contra,
                        'puntos': estadisticas_equipos.puntos,
                    }
                    for nombre_equipo, estadisticas_equipos in competicion.estadisticas_equipos.items()
                }
            }
            for nombre_liga, competicion in juego.ligas.items()
        }
    }
    utils.guardar_juego(estado)

# Cargar el estado del juego
def cargar_estado():
    estado = utils.cargar_juego()
    fecha_inicio = datetime.strptime(estado['fecha'], '%Y-%m-%d')
    equipos = cargar_equipos('data/equipos.csv')
    ligas_dict = asignar_equipos_a_ligas(equipos)
    
    ligas_juego = {}
    for nombre_liga, datos_liga in estado['ligas'].items():
        competicion = Competicion(ligas_dict[nombre_liga])
        competicion.clasificacion = {
            equipo: puntos
            for equipo, puntos in datos_liga['clasificacion'].items()
        }
        competicion.estadisticas_equipos = {
            nombre_equipo: EstadisticasEquipo(
                nombre_equipo,
                estadisticas['partidos_jugados'],
                estadisticas['victorias'],
                estadisticas['empates'],
                estadisticas['derrotas'],
                estadisticas['goles_a_favor'],
                estadisticas['goles_en_contra'],
                estadisticas['puntos']
            )
            for nombre_equipo, estadisticas in datos_liga['estadisticas_equipos'].items()
        }
        ligas_juego[nombre_liga] = competicion
    
    return Juego(fecha_inicio, ligas_juego)

# Menú principal
def menu_principal():
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Menú Principal")
    
    mostrar_intro(pantalla)  # Muestra la animación de inicio
    
    botones = [
        crear_boton("Nueva Partida", (settings.ANCHO // 2, settings.ALTO // 2 - 100), FUENTE_BOTON),
        crear_boton("Cargar Partida", (settings.ANCHO // 2, settings.ALTO // 2), FUENTE_BOTON),
        crear_boton("Salir", (settings.ANCHO // 2, settings.ALTO // 2 + 100), FUENTE_BOTON)
    ]

    corriendo = True
    while corriendo:
        pantalla.blit(FONDO_MENU, (0, 0))  # Dibujar la imagen de fondo
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, (superficie_texto, rect) in enumerate(botones):
                    if rect.collidepoint(evento.pos):
                        if i == 0:
                            from src.ui.menu.nueva_partida import menu_modo_juego  # Importar solo cuando sea necesario
                            menu_modo_juego(pantalla)
                        elif i == 1:
                            # Cargar Partida
                            juego = cargar_estado()
                            juego.ejecutar()
                        elif i == 2:
                            corriendo = False

        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
    return None
