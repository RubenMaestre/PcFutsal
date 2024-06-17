import pygame
import settings
from proyecto_pcfutbol.manager.src.core.partidos import Match

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

# Dibujar eventos del partido
def draw_events(screen, match):
    y_offset = 100
    for event in match.get_events():
        event_text = f"{event[0]}': {event[1]} - {event[2]}"
        event_surface = FONT.render(event_text, True, WHITE)
        screen.blit(event_surface, (50, y_offset))
        y_offset += 30

# Simulación del partido
def match_simulation(team1, team2):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Simulación del Partido")
    
    match = Match(team1, team2)
    result = match.simulate()
    
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

        draw_events(screen, match)
        draw_buttons(screen, buttons)
        
        result_text = f"Resultado Final: {team1.name} {result[0]} - {result[1]} {team2.name}"
        result_surface = FONT.render(result_text, True, WHITE)
        screen.blit(result_surface, (settings.WIDTH // 2 - result_surface.get_width() // 2, 50))
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la simulación del partido.
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.equipo import Team
    team1 = Team("Equipo 1", 1000000)
    team2 = Team("Equipo 2", 1000000)
    match_simulation(team1, team2)
