# src/ui/gestion_finanzas.py

import pygame
import settings
from src.core.finanzas import Finanzas

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

# Dibujar reporte financiero
def dibujar_reporte_financiero(pantalla, finanzas):
    y_offset = 100
    reporte = finanzas.generar_reporte_financiero()
    for clave, valor in reporte.items():
        texto_reporte = f"{clave}: {valor}"
        superficie_reporte = FUENTE.render(texto_reporte, True, BLANCO)
        pantalla.blit(superficie_reporte, (50, y_offset))
        y_offset += 40

# Gestión financiera
def gestion_financiera(finanzas):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión Financiera")
    
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

        dibujar_reporte_financiero(pantalla, finanzas)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()