# src/ui/simulador_partidos.py

import pygame
import settings
from src.core.partidos import Partido

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

# Dibujar eventos del partido
def dibujar_eventos(pantalla, partido):
    y_offset = 100
    for evento in partido.obtener_eventos():
        texto_evento = f"{evento[0]}': {evento[1]} - {evento[2]}"
        superficie_evento = FUENTE.render(texto_evento, True, BLANCO)
        pantalla.blit(superficie_evento, (50, y_offset))
        y_offset += 30

# Simulación del partido
def simulacion_partido(equipo1, equipo2):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Simulación del Partido")
    
    partido = Partido(equipo1, equipo2)
    resultado = partido.simular()
    
    botones = [
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
                            corriendo = False

        dibujar_eventos(pantalla, partido)
        dibujar_botones(pantalla, botones)
        
        texto_resultado = f"Resultado Final: {equipo1.nombre} {resultado[0]} - {resultado[1]} {equipo2.nombre}"
        superficie_resultado = FUENTE.render(texto_resultado, True, BLANCO)
        pantalla.blit(superficie_resultado, (settings.ANCHO // 2 - superficie_resultado.get_width() // 2, 50))
        
        pygame.display.flip()

    pygame.quit()
