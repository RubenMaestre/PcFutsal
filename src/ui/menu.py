import pygame
import settings
from datetime import datetime
from proyecto_pcfutbol.manager.src.core.juego import Game
from proyecto_pcfutbol.manager.src.core.cargar_equipos import load_teams, assign_teams_to_leagues
from proyecto_pcfutbol.manager.src.core.cargar_entrenadores import load_coaches
from proyecto_pcfutbol.manager.src.core.cargar_directores_deportivos import load_sporting_directors
from proyecto_pcfutbol.manager.src.core.cargar_presidentes import load_presidents
from proyecto_pcfutbol.manager.src.core.competicion import Competition
from ui.ui_helpers import create_button, draw_buttons, wrap_text  # Importar desde ui_helpers
import utils

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores
WHITE = settings.WHITE
BLACK = settings.BLACK
RED = settings.RED

# Definir fuentes
FONT = pygame.font.Font(None, 74)
BUTTON_FONT = pygame.font.Font(None, 50)
COMMENT_FONT = pygame.font.Font(None, 30)

# Cargar la imagen de fondo del menú
MENU_BACKGROUND = pygame.image.load('assets/menu_background.png')

# Mostrar la animación de inicio
def show_intro(screen):
    intro_images = ['assets/intro/frame1.png', 'assets/intro/frame2.png', 'assets/intro/frame3.png']  # Añade más frames según sea necesario
    for img_path in intro_images:
        img = pygame.image.load(img_path)
        screen.blit(img, (0, 0))
        pygame.display.flip()
        pygame.time.wait(3000)  # Espera 3000 milisegundos entre frames

# Guardar el estado del juego
def save_state(game):
    state = {
        'date': game.current_date.strftime('%Y-%m-%d'),
        'leagues': {
            league_name: {
                'standings': {
                    team.name: points
                    for team, points in competition.standings.items()
                },
                'team_stats': {
                    team_name: {
                        'matches_played': team_stats.matches_played,
                        'wins': team_stats.wins,
                        'draws': team_stats.draws,
                        'losses': team_stats.losses,
                        'goals_for': team_stats.goals_for,
                        'goals_against': team_stats.goals_against,
                        'points': team_stats.points,
                    }
                    for team_name, team_stats in competition.team_stats.items()
                }
            }
            for league_name, competition in game.leagues.items()
        }
    }
    utils.save_game(state)

# Cargar el estado del juego
def load_state():
    state = utils.load_game()
    start_date = datetime.strptime(state['date'], '%Y-%m-%d')
    teams = load_teams('data/teams.csv')
    leagues_dict = assign_teams_to_leagues(teams)
    
    game_leagues = {}
    for league_name, league_data in state['leagues'].items():
        competition = Competition(leagues_dict[league_name])
        competition.standings = {
            team: points
            for team, points in league_data['standings'].items()
        }
        competition.team_stats = {
            team_name: TeamStats(
                team_name,
                stats['matches_played'],
                stats['wins'],
                stats['draws'],
                stats['losses'],
                stats['goals_for'],
                stats['goals_against'],
                stats['points']
            )
            for team_name, stats in league_data['team_stats'].items()
        }
        game_leagues[league_name] = competition
    
    return Game(start_date, game_leagues)

# Menú principal
def main_menu():
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Menú Principal")
    
    show_intro(screen)  # Muestra la animación de inicio
    
    buttons = [
        create_button("Nueva Partida", (settings.WIDTH // 2, settings.HEIGHT // 2 - 100), BUTTON_FONT),
        create_button("Cargar Partida", (settings.WIDTH // 2, settings.HEIGHT // 2), BUTTON_FONT),
        create_button("Salir", (settings.WIDTH // 2, settings.HEIGHT // 2 + 100), BUTTON_FONT)
    ]

    game = None
    
    running = True
    while running:
        screen.blit(MENU_BACKGROUND, (0, 0))  # Dibujar la imagen de fondo
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text_surface, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            from ui.menu1 import game_mode_menu  # Importar solo cuando sea necesario
                            game_mode_menu(screen)
                        elif i == 1:
                            # Cargar Partida
                            game = load_state()
                            game.run()
                        elif i == 2:
                            running = False

        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()
    return None

# Si ejecutas este archivo directamente, muestra el menú principal.
if __name__ == "__main__":
    main_menu()
