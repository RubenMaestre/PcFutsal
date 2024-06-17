# src/ui/gestion_cantera.py

import pygame
import settings
from src.core.jugador import JugadorJuvenil

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores y fuentes
BLANCO = settings.BLANCO
NEGRO = settings.NEGRO
ROJO = settings.ROJO
FUENTE = pygame.font.Font(None, 36)
FUENTE_BOTON = pygame.font.Font(None, 24)

# Crear botones
def crear_boton(texto, pos):
    superficie_texto = FUENTE_BOTON.render(texto, True, BLANCO)
    rect = superficie_texto.get_rect(center=pos)
    return superficie_texto, rect

# Dibujar botones
def dibujar_botones(pantalla, botones):
    for superficie_texto, rect in botones:
        pygame.draw.rect(pantalla, ROJO, rect.inflate(20, 20))
        pantalla.blit(superficie_texto, rect)

# Dibujar jugadores de cantera
def dibujar_jugadores_cantera(pantalla, equipo):
    y_offset = 100
    for jugador in equipo.jugadores_juveniles:
        texto_jugador = f"{jugador.nombre_corto} - {jugador.posicion} - Habilidades: {jugador.habilidades} - Potencial: {jugador.potencial}"
        superficie_jugador = FUENTE.render(texto_jugador, True, BLANCO)
        pantalla.blit(superficie_jugador, (50, y_offset))
        y_offset += 40

# Gestión de cantera
def gestion_cantera(equipo):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión de Cantera")
    
    botones = [
        crear_boton("Entrenar Jugadores", (settings.ANCHO // 2, settings.ALTO - 150)),
        crear_boton("Promover Jugador", (settings.ANCHO // 2, settings.ALTO - 100)),
        crear_boton("Volver", (settings.ANCHO // 2, settings.ALTO - 50))
    ]
    
    corriendo = True
    while corriendo:
        pantalla.fill(NEGRO)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, (superficie_texto, rect) in enumerate(botones):
                    if rect.collidepoint(evento.pos):
                        if i == 0:
                            # Entrenar Jugadores
                            for jugador in equipo.jugadores_juveniles:
                                jugador.desarrollar()
                        elif i == 1:
                            # Promover Jugador
                            if equipo.jugadores_juveniles:
                                jugador = equipo.jugadores_juveniles.pop(0)  # Promover el primer jugador de la lista
                                equipo.agregar_jugador(jugador)
                        elif i == 2:
                            # Volver al menú principal
                            corriendo = False

        dibujar_jugadores_cantera(pantalla, equipo)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
