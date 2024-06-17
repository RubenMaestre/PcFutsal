# src/ui/ui_helpers.py

import pygame
import settings

# Crear botones
def crear_boton(texto, posicion, fuente, color=settings.BLANCO):
    superficie_texto = fuente.render(texto, True, color)
    rect = superficie_texto.get_rect(center=posicion)
    return superficie_texto, rect

# Dibujar botones
def dibujar_botones(pantalla, botones):
    for superficie_texto, rect in botones:
        pygame.draw.rect(pantalla, settings.ROJO, rect.inflate(20, 20))
        pantalla.blit(superficie_texto, rect)

# Ajustar texto para dividirlo en múltiples líneas
def ajustar_texto(texto, fuente, max_ancho):
    palabras = texto.split(' ')
    lineas = []
    linea_actual = []
    ancho_actual = 0

    for palabra in palabras:
        ancho_palabra, _ = fuente.size(palabra + ' ')
        if ancho_actual + ancho_palabra <= max_ancho:
            linea_actual.append(palabra)
            ancho_actual += ancho_palabra
        else:
            lineas.append(' '.join(linea_actual))
            linea_actual = [palabra]
            ancho_actual = ancho_palabra

    if linea_actual:
        lineas.append(' '.join(linea_actual))

    return lineas
