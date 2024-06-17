import pygame
import settings
from proyecto_pcfutbol.manager.src.core.fichajes import Transfer
from proyecto_pcfutbol.manager.src.core.jugador import Player

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

# Dibujar jugadores y presupuesto
def draw_team_info(screen, team):
    y_offset = 100
    budget_text = f"Presupuesto: {team.finance.budget}"
    budget_surface = FONT.render(budget_text, True, WHITE)
    screen.blit(budget_surface, (50, y_offset))
    y_offset += 40
    
    for player in team.players:
        player_text = f"{player.name} - {player.position} - Skills: {player.skills}"
        player_surface = FONT.render(player_text, True, WHITE)
        screen.blit(player_surface, (50, y_offset))
        y_offset += 40

# Gestión de transferencias
def transfer_management(from_team, to_team):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión de Transferencias")
    
    buttons = [
        create_button("Transferir Jugador", (settings.WIDTH // 2, settings.HEIGHT - 150)),
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
                            # Transferir Jugador (ejemplo de cómo se podría hacer)
                            if from_team.players:
                                player = from_team.players[0]  # El primer jugador del equipo de origen
                                transfer = Transfer(player, from_team, to_team, 50000, "Contrato de 3 años")
                                transfer.execute_transfer()
                        elif i == 1:
                            running = False

        draw_team_info(screen, from_team)
        draw_team_info(screen, to_team)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión de transferencias.
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.equipo import Team
    team1 = Team("Equipo 1", 1000000)
    team1.finance = Finance(1000000)
    team1.add_player(Player("Jugador 1", 20, "Midfielder", {"dribbling": 70, "passing": 65}))
    
    team2 = Team("Equipo 2", 1000000)
    team2.finance = Finance(1000000)
    
    transfer_management(team1, team2)
