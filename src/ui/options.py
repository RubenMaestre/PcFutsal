# src/ui/opciones.py

import pygame
import settings

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores y fuentes
BLANCO = settings.WHITE
NEGRO = settings.BLACK
ROJO = settings.RED
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

# Pantalla de opciones
def menu_opciones():
    pantalla = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Opciones")
    
    volumen = settings.SOUND_VOLUME
    fps = settings.FPS
    
    botones = [
        crear_boton("Volumen: " + str(volumen), (settings.WIDTH // 2, settings.HEIGHT // 2 - 100)),
        crear_boton("FPS: " + str(fps), (settings.WIDTH // 2, settings.HEIGHT // 2)),
        crear_boton("Volver", (settings.WIDTH // 2, settings.HEIGHT // 2 + 100))
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
                            # Ajustar volumen
                            volumen = (volumen + 0.1) % 1.1
                            settings.SOUND_VOLUME = volumen
                            botones[i] = crear_boton("Volumen: " + str(round(volumen, 1)), (settings.WIDTH // 2, settings.HEIGHT // 2 - 100))
                        elif i == 1:
                            # Ajustar FPS
                            fps = (fps + 10) % 121
                            settings.FPS = fps
                            botones[i] = crear_boton("FPS: " + str(fps), (settings.WIDTH // 2, settings.HEIGHT // 2))
                        elif i == 2:
                            # Volver al menú principal
                            corriendo = False

        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()