# src/ui/gestion_equipo.py

import pygame
import settings
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

# Dibujar jugadores
def dibujar_jugadores(pantalla, equipo):
    y_offset = 100
    for jugador in equipo.jugadores:
        texto_jugador = f"{jugador.nombre_corto} - {jugador.posiciones_jugador} - Habilidades: {jugador.habilidades} - Moral: {jugador.moral} - Condición Física: {jugador.condicion_fisica}"
        superficie_jugador = FUENTE.render(texto_jugador, True, BLANCO)
        pantalla.blit(superficie_jugador, (50, y_offset))
        y_offset += 40

# Ajustar moral de los jugadores
def ajustar_moral_jugadores(equipo):
    for jugador in equipo.jugadores:
        minutos_jugados = 90  # Ejemplo de minutos jugados
        esta_lesionado = False  # Ejemplo de estado de lesión
        estado_contrato = "incierto"  # Ejemplo de estado del contrato
        confianza_entrenador = True  # Ejemplo de confianza del entrenador
        calidad_entrenamiento = 5  # Ejemplo de calidad del entrenamiento

        jugador.ajustar_moral(minutos_jugados, esta_lesionado, estado_contrato, confianza_entrenador, calidad_entrenamiento)

# Gestión de equipo
def gestion_equipo(equipo):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Gestión de Equipo")
    
    botones = [
        crear_boton("Añadir Jugador", (settings.ANCHO // 2, settings.ALTO - 150)),
        crear_boton("Eliminar Jugador", (settings.ANCHO // 2, settings.ALTO - 100)),
        crear_boton("Editar Jugador", (settings.ANCHO // 2, settings.ALTO - 50)),
        crear_boton("Ajustar Moral", (settings.ANCHO // 2, settings.ALTO - 20)),
        crear_boton("Volver", (settings.ANCHO // 2, settings.ALTO + 30))
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
                            # Añadir Jugador (ejemplo de cómo se podría hacer)
                            nuevo_jugador = Jugador("Nuevo Jugador", 20, "Ala", {"regate": 70, "pase": 65})
                            equipo.agregar_jugador(nuevo_jugador)
                        elif i == 1:
                            # Eliminar Jugador (ejemplo de cómo se podría hacer)
                            if equipo.jugadores:
                                equipo.eliminar_jugador(equipo.jugadores[-1].nombre_corto)
                        elif i == 2:
                            # Editar Jugador (ejemplo de cómo se podría hacer)
                            if equipo.jugadores:
                                jugador = equipo.jugadores[0]
                                jugador.nombre_corto = "Jugador Editado"
                                jugador.habilidades["regate"] = 80
                        elif i == 3:
                            # Ajustar Moral
                            ajustar_moral_jugadores(equipo)
                        elif i == 4:
                            # Volver al menú principal
                            corriendo = False

        dibujar_jugadores(pantalla, equipo)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
