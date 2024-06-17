# src/ui/gestion_entrenamiento.py

import pygame
import settings
from src.core.entrenamiento import Entrenamiento

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

# Dibujar sesiones de entrenamiento
def dibujar_sesiones_entrenamiento(pantalla, entrenamiento):
    y_offset = 100
    for habilidad, intensidad in entrenamiento.sesiones.items():
        texto_sesion = f"Entrenamiento: {habilidad} - Intensidad: {intensidad}"
        superficie_sesion = FUENTE.render(texto_sesion, True, BLANCO)
        pantalla.blit(superficie_sesion, (50, y_offset))
        y_offset += 40

# Gestión de entrenamientos
def gestion_entrenamiento(entrenamiento, equipo):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión de Entrenamientos")
    
    botones = [
        crear_boton("Añadir Entrenamiento: Regate", (settings.ANCHO // 2, settings.ALTO - 150)),
        crear_boton("Añadir Entrenamiento: Pase", (settings.ANCHO // 2, settings.ALTO - 100)),
        crear_boton("Ejecutar Entrenamientos", (settings.ANCHO // 2, settings.ALTO - 50)),
        crear_boton("Volver", (settings.ANCHO // 2, settings.ALTO - 20))
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
                            # Añadir entrenamiento de regate
                            entrenamiento.agregar_sesion("regate", 3)
                        elif i == 1:
                            # Añadir entrenamiento de pase
                            entrenamiento.agregar_sesion("pase", 2)
                        elif i == 2:
                            # Ejecutar entrenamientos
                            entrenamiento.ejecutar_entrenamiento(equipo)
                        elif i == 3:
                            # Volver al menú principal
                            corriendo = False

        dibujar_sesiones_entrenamiento(pantalla, entrenamiento)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
