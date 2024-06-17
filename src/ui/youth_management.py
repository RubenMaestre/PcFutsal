import pygame
import settings
from proyecto_pcfutbol.manager.src.core.jugador import YouthPlayer

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

# Dibujar jugadores de cantera
def draw_youth_players(screen, team):
    y_offset = 100
    for player in team.youth_players:
        player_text = f"{player.name} - {player.position} - Skills: {player.skills} - Potential: {player.potential}"
        player_surface = FONT.render(player_text, True, WHITE)
        screen.blit(player_surface, (50, y_offset))
        y_offset += 40

# Gestión de cantera
def youth_management(team):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión de Cantera")
    
    buttons = [
        create_button("Entrenar Jugadores", (settings.WIDTH // 2, settings.HEIGHT - 150)),
        create_button("Promover Jugador", (settings.WIDTH // 2, settings.HEIGHT - 100)),
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
                            # Entrenar Jugadores
                            for player in team.youth_players:
                                player.develop()
                        elif i == 1:
                            # Promover Jugador
                            if team.youth_players:
                                player = team.youth_players.pop(0)  # Promover el primer jugador de la lista
                                team.add_player(player)
                        elif i == 2:
                            # Volver al menú principal
                            running = False

        draw_youth_players(screen, team)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión de cantera.
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.equipo import Team
    team = Team("Mi Equipo", 1000000)
    team.youth_players = [
        YouthPlayer("Joven 1", 16, "Midfielder", {"dribbling": 50, "passing": 45}, potential=80),
        YouthPlayer("Joven 2", 17, "Forward", {"dribbling": 60, "shooting": 55}, potential=85)
    ]
    youth_management(team)
