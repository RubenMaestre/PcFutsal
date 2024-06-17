# src/ui/gestion_tacticas.py

import pygame
import settings
from src.core.tacticas import Tacticas

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

# Dibujar tácticas
def dibujar_tacticas(pantalla, tacticas):
    y_offset = 100
    texto_formacion = f"Formación: {tacticas.formacion}"
    superficie_formacion = FUENTE.render(texto_formacion, True, BLANCO)
    pantalla.blit(superficie_formacion, (50, y_offset))
    
    y_offset += 40
    texto_ofensivo = f"Estrategia Ofensiva: {tacticas.estrategia_ofensiva}"
    superficie_ofensiva = FUENTE.render(texto_ofensivo, True, BLANCO)
    pantalla.blit(superficie_ofensiva, (50, y_offset))
    
    y_offset += 40
    texto_defensivo = f"Estrategia Defensiva: {tacticas.estrategia_defensiva}"
    superficie_defensiva = FUENTE.render(texto_defensivo, True, BLANCO)
    pantalla.blit(superficie_defensiva, (50, y_offset))
    
    y_offset += 40
    texto_roles = f"Roles: {tacticas.roles}"
    superficie_roles = FUENTE.render(texto_roles, True, BLANCO)
    pantalla.blit(superficie_roles, (50, y_offset))

# Gestión de tácticas
def gestion_tacticas(tacticas):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión de Tácticas")
    
    botones = [
        crear_boton("Formación: 4-4-2", (settings.ANCHO // 2, settings.ALTO - 250)),
        crear_boton("Estrategia Ofensiva: Posesión", (settings.ANCHO // 2, settings.ALTO - 200)),
        crear_boton("Estrategia Defensiva: Presión Alta", (settings.ANCHO // 2, settings.ALTO - 150)),
        crear_boton("Establecer Roles", (settings.ANCHO // 2, settings.ALTO - 100)),
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
                            # Establecer formación
                            tacticas.establecer_formacion("4-4-2")
                            botones[i] = crear_boton("Formación: 4-4-2", (settings.ANCHO // 2, settings.ALTO - 250))
                        elif i == 1:
                            # Establecer estrategia ofensiva
                            tacticas.establecer_estrategia_ofensiva("posesión")
                            botones[i] = crear_boton("Estrategia Ofensiva: Posesión", (settings.ANCHO // 2, settings.ALTO - 200))
                        elif i == 2:
                            # Establecer estrategia defensiva
                            tacticas.establecer_estrategia_defensiva("presión alta")
                            botones[i] = crear_boton("Estrategia Defensiva: Presión Alta", (settings.ANCHO // 2, settings.ALTO - 150))
                        elif i == 3:
                            # Establecer roles
                            tacticas.establecer_roles({"delantero": "hombre objetivo", "centrocampista": "creador de juego"})
                        elif i == 4:
                            # Volver al menú principal
                            corriendo = False

        dibujar_tacticas(pantalla, tacticas)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
