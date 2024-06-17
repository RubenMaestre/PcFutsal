import pygame
import settings
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

# Dibujar jugadores
def draw_players(screen, team):
    y_offset = 100
    for player in team.players:
        player_text = f"{player.name} - {player.position} - Skills: {player.skills} - Morale: {player.morale} - Fitness: {player.fitness}"
        player_surface = FONT.render(player_text, True, WHITE)
        screen.blit(player_surface, (50, y_offset))
        y_offset += 40

# Ajustar moral de los jugadores
def adjust_player_morale(team):
    for player in team.players:
        played_minutes = 90  # Ejemplo de minutos jugados
        is_injured = False  # Ejemplo de estado de lesión
        contract_status = "uncertain"  # Ejemplo de estado del contrato
        coach_confidence = True  # Ejemplo de confianza del entrenador
        training_quality = 5  # Ejemplo de calidad del entrenamiento

        player.adjust_morale_based_on_factors(played_minutes, is_injured, contract_status, coach_confidence, training_quality)

# Gestión de equipo
def team_management(team):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión de Equipo")
    
    buttons = [
        create_button("Añadir Jugador", (settings.WIDTH // 2, settings.HEIGHT - 150)),
        create_button("Eliminar Jugador", (settings.WIDTH // 2, settings.HEIGHT - 100)),
        create_button("Editar Jugador", (settings.WIDTH // 2, settings.HEIGHT - 50)),
        create_button("Ajustar Moral", (settings.WIDTH // 2, settings.HEIGHT - 20)),
        create_button("Volver", (settings.WIDTH // 2, settings.HEIGHT + 30))
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
                            # Añadir Jugador (ejemplo de cómo se podría hacer)
                            new_player = Player("Nuevo Jugador", 20, "Midfielder", {"dribbling": 70, "passing": 65})
                            team.add_player(new_player)
                        elif i == 1:
                            # Eliminar Jugador (ejemplo de cómo se podría hacer)
                            if team.players:
                                team.remove_player(team.players[-1].name)
                        elif i == 2:
                            # Editar Jugador (ejemplo de cómo se podría hacer)
                            if team.players:
                                player = team.players[0]
                                player.name = "Jugador Editado"
                                player.skills["dribbling"] = 80
                        elif i == 3:
                            # Ajustar Moral
                            adjust_player_morale(team)
                        elif i == 4:
                            # Volver al menú principal
                            running = False

        draw_players(screen, team)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión de equipo.
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.equipo import Team
    team = Team("Mi Equipo", 1000000)
    team.add_player(Player("Jugador 1", 20, "Midfielder", {"dribbling": 70, "passing": 65}))
    team_management(team)
