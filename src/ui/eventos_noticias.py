# src/ui/eventos_noticias.py

import pygame
import settings
from src.core.evento import Evento
from src.core.noticias import Noticia

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

# Dibujar eventos
def dibujar_eventos(pantalla, eventos):
    y_offset = 100
    for evento in eventos:
        texto_evento = f"Evento: {evento.descripcion} - Tipo: {evento.tipo_evento}"
        superficie_evento = FUENTE.render(texto_evento, True, BLANCO)
        pantalla.blit(superficie_evento, (50, y_offset))
        y_offset += 40

# Dibujar noticias
def dibujar_noticias(pantalla, noticias):
    y_offset = 100
    for noticia in noticias:
        texto_noticia = f"{noticia.fecha}: {noticia.titular} - {noticia.contenido}"
        superficie_noticia = FUENTE.render(texto_noticia, True, BLANCO)
        pantalla.blit(superficie_noticia, (50, y_offset))
        y_offset += 40

# Mostrar eventos y noticias
def eventos_noticias(eventos, noticias):
    pantalla = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
    pygame.display.set_caption("Manager - Eventos y Noticias")
    
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

        dibujar_eventos(pantalla, eventos)
        dibujar_noticias(pantalla, noticias)
        dibujar_botones(pantalla, botones)
        
        pygame.display.flip()

    pygame.quit()
