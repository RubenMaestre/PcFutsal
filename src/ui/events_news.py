import pygame
import settings
from proyecto_pcfutbol.manager.src.core.evento import Event
from proyecto_pcfutbol.manager.src.core.noticias import News

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores y fuentes
WHITE = settings.WHITE
BLACK = settings.BLACK
RED = settings.RED
FONT = pygame.font.Font(None, 36)
BUTTON_FONT = pygame.font.Font(None, 24)

# Crear botones
def create_button(text, pos):
    text_surface = BUTTON_FONT.render(text, True, WHITE)
    rect = text_surface.get_rect(center=pos)
    return text_surface, rect

# Dibujar botones
def draw_buttons(screen, buttons):
    for text_surface, rect in buttons:
        pygame.draw.rect(screen, RED, rect.inflate(20, 20))
        screen.blit(text_surface, rect)

# Dibujar eventos
def draw_events(screen, events):
    y_offset = 100
    for event in events:
        event_text = f"Evento: {event.description} - Tipo: {event.event_type}"
        event_surface = FONT.render(event_text, True, WHITE)
        screen.blit(event_surface, (50, y_offset))
        y_offset += 40

# Dibujar noticias
def draw_news(screen, news):
    y_offset = 100
    for new in news:
        news_text = f"{new.date}: {new.headline} - {new.content}"
        news_surface = FONT.render(news_text, True, WHITE)
        screen.blit(news_surface, (50, y_offset))
        y_offset += 40

# Mostrar eventos y noticias
def events_news(events, news):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Eventos y Noticias")
    
    buttons = [
        create_button("Volver", (settings.WIDTH // 2, settings.HEIGHT - 50))
    ]
    
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text_surface, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            running = False

        draw_events(screen, events)
        draw_news(screen, news)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra eventos y noticias.
if __name__ == "__main__":
    events = [
        Event("Lesion de jugador", "lesion", {"jugador": "Jugador 1", "duracion": "2 semanas"}),
        Event("Transferencia realizada", "transferencia", {"jugador": "Jugador 2", "equipo_destino": "Equipo B"})
    ]
    news = [
        News("Gran victoria", "El equipo A gana el partido con un marcador de 3-1", "2024-06-14"),
        News("Nuevo fichaje", "El equipo A ficha a un nuevo delantero", "2024-06-15")
    ]
    events_news(events, news)
