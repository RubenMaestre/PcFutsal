# src/ui/gestion_fichajes.py

import pygame
import settings
from src.core.fichajes import Transferencia
from src.core.jugador import Jugador

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

# Dibujar jugadores y presupuesto
def dibujar_info_equipo(pantalla, equipo):
    y_offset = 100
    texto_presupuesto = f"Presupuesto: {equipo.finanzas.presupuesto}"
    superficie_presupuesto = FUENTE.render(texto_presupuesto, True, BLANCO)
    pantalla.blit(superficie_presupuesto, (50, y_offset))
    y_offset += 40
    
    for jugador in equipo.jugadores:
        texto_jugador = f"{jugador.nombre_corto} - {jugador.posicion} - Habilidades: {jugador.habilidades}"
        superficie_jugador = FUENTE.render(texto_jugador, True, BLANCO)
        pantalla.blit(superficie_jugador, (50, y_offset))
        y_offset += 40

# Gestión de transferencias
def gestion_fichajes(equipo_origen, equipo_destino):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión de Fichajes")
    
    botones = [
        crear_boton("Fichar Jugador", (settings.ANCHO // 2, settings.ALTO - 150)),
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
                            # Fichar Jugador (ejemplo de cómo se podría hacer)
                            if equipo_origen.jugadores:
                                jugador = equipo_origen.jugadores[0]  # El primer jugador del equipo de origen
                                transferencia = Transferencia(jugador, equipo_origen, equipo_destino, 50000, "Contrato de 3 años")
                                transferencia.ejecutar_transferencia()
                        elif i == 1:
                            corriendo = False

        dibujar_info_equipo(pantalla, equipo_origen)
        dibujar_info_equipo(pantalla, equipo_destino)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
