import pygame
import settings
import csv
import random
from ui.ui_helpers import create_button, draw_buttons, wrap_text

# Funciones para cargar datos desde CSV
def load_countries(file_path):
    countries = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            countries.append(row)
    return countries

def load_competitions(file_path):
    competitions = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            competitions.append(row)
    return competitions

def load_teams(file_path):
    teams = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            teams.append(row)
    return teams

# Función para mostrar el menú de selección de equipo
def team_selection_menu(screen):
    countries = load_countries('data/countries.csv')
    competitions = load_competitions('data/competitions.csv')
    teams = load_teams('data/teams.csv')

    country_buttons = [(create_button(country['country_name'], (settings.WIDTH // 4, 150 + i * 60), settings.BUTTON_FONT), country) for i, country in enumerate(countries)]
    competition_buttons = []
    team_buttons = []
    selected_country = None
    selected_competition = None
    selected_team = None
    can_be_fired = False  # Inicialmente no puede ser despedido

    running = True
    while running:
        screen.blit(pygame.image.load('assets/menu_background.png'), (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (button_surface, country) in enumerate(country_buttons):
                    if button_surface[1].collidepoint(event.pos):
                        selected_country = country
                        competition_buttons = [
                            (create_button(competition['competition_name'], (settings.WIDTH // 2, 150 + j * 60), settings.BUTTON_FONT), competition)
                            for j, competition in enumerate(competitions)
                            if competition['country_name'] == selected_country['country_name']
                        ]
                        selected_competition = None
                        selected_team = None
                        team_buttons = []
                for i, (button_surface, competition) in enumerate(competition_buttons):
                    if button_surface[1].collidepoint(event.pos):
                        selected_competition = competition
                        team_buttons = [
                            (create_button(team['team_name'], (3 * settings.WIDTH // 4, 150 + k * 60), settings.BUTTON_FONT), team)
                            for k, team in enumerate(teams)
                            if team['league'] == selected_competition['competition_name']
                        ]
                        selected_team = None
                for i, (button_surface, team) in enumerate(team_buttons):
                    if button_surface[1].collidepoint(event.pos):
                        selected_team = team
                # Check para despido
                if dismiss_checkbox.collidepoint(event.pos):
                    can_be_fired = not can_be_fired

        draw_buttons(screen, [button_surface for button_surface, _ in country_buttons])
        draw_buttons(screen, [button_surface for button_surface, _ in competition_buttons])
        draw_buttons(screen, [button_surface for button_surface, _ in team_buttons])

        # Mostrar información de selección
        if selected_country:
            selected_text = f"País seleccionado: {selected_country['country_name']}"
            text_surface = settings.BUTTON_FONT.render(selected_text, True, settings.WHITE)
            text_rect = text_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 150))
            screen.blit(text_surface, text_rect)
        
        if selected_competition:
            selected_text = f"Competición seleccionada: {selected_competition['competition_name']}"
            text_surface = settings.BUTTON_FONT.render(selected_text, True, settings.WHITE)
            text_rect = text_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 100))
            screen.blit(text_surface, text_rect)
        
        if selected_team:
            selected_text = f"Equipo seleccionado: {selected_team['team_name']}"
            text_surface = settings.BUTTON_FONT.render(selected_text, True, settings.WHITE)
            text_rect = text_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 50))
            screen.blit(text_surface, text_rect)

        # Check para despido
        dismiss_checkbox = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT - 200, 20, 20)
        pygame.draw.rect(screen, settings.WHITE, dismiss_checkbox, 2)
        if can_be_fired:
            pygame.draw.rect(screen, settings.WHITE, dismiss_checkbox)
        dismiss_text = settings.BUTTON_FONT.render("Selecciona aquí si puedes ser despedido del club", True, settings.WHITE)
        screen.blit(dismiss_text, (settings.WIDTH // 2 - 70, settings.HEIGHT - 205))

        # Botón de "Volver"
        back_button = create_button("VOLVER", (settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [back_button])
        if back_button[1].collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            running = False

        # Botón de "Siguiente"
        if selected_team:
            next_button = create_button("SIGUIENTE", (3 * settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
            draw_buttons(screen, [next_button])
            if next_button[1].collidepoint(event.pos) and event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Equipo seleccionado: {selected_team['team_name']}")
                running = False

        pygame.display.flip()

    return selected_team, can_be_fired

# Función para mostrar el menú de selección aleatoria de equipo
def random_team_menu(screen):
    teams = load_teams('data/teams.csv')
    selected_team = random.choice(teams)
    can_be_fired = False

    running = True
    while running:
        screen.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check para despido
                if dismiss_checkbox.collidepoint(event.pos):
                    can_be_fired = not can_be_fired
                # Botón de "Volver a Barajar"
                if reshuffle_button[1].collidepoint(event.pos):
                    selected_team = random.choice(teams)
                # Botón de "Volver"
                if back_button[1].collidepoint(event.pos):
                    running = False
                # Botón de "Siguiente"
                if next_button[1].collidepoint(event.pos):
                    print(f"Equipo seleccionado: {selected_team['team_name']}")
                    running = False

        selected_text = f"Equipo seleccionado: {selected_team['team_name']}"
        text_surface = settings.BUTTON_FONT.render(selected_text, True, settings.WHITE)
        text_rect = text_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
        screen.blit(text_surface, text_rect)

        # Check para despido
        dismiss_checkbox = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT - 200, 20, 20)
        pygame.draw.rect(screen, settings.WHITE, dismiss_checkbox, 2)
        if can_be_fired:
            pygame.draw.rect(screen, settings.WHITE, dismiss_checkbox)
        dismiss_text = settings.BUTTON_FONT.render("Selecciona aquí si puedes ser despedido del club", True, settings.WHITE)
        screen.blit(dismiss_text, (settings.WIDTH // 2 - 70, settings.HEIGHT - 205))

        # Botón de "Volver a Barajar"
        reshuffle_button = create_button("Volver a Barajar", (settings.WIDTH // 2, settings.HEIGHT // 2 + 100), settings.COMMENT_FONT)
        draw_buttons(screen, [reshuffle_button])

        # Botón de "Volver"
        back_button = create_button("VOLVER", (settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [back_button])

        # Botón de "Siguiente"
        next_button = create_button("SIGUIENTE", (3 * settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [next_button])

        pygame.display.flip()

    return selected_team, can_be_fired

# Función para mostrar el menú del modo carrera
def career_mode_menu(screen):
    teams = load_teams('data/teams.csv')
    selected_teams = random.sample(teams, 3)  # Seleccionar 3 equipos aleatorios
    selected_team = None

    running = True
    while running:
        screen.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (button_surface, team) in enumerate(team_buttons):
                    if button_surface[1].collidepoint(event.pos):
                        selected_team = team
                # Botón de "Volver"
                if back_button[1].collidepoint(event.pos):
                    running = False
                # Botón de "Siguiente"
                if selected_team and next_button[1].collidepoint(event.pos):
                    print(f"Equipo seleccionado en modo carrera: {selected_team['team_name']}")
                    running = False

        team_buttons = [(create_button(team['team_name'], (settings.WIDTH // 2, 150 + i * 100), settings.BUTTON_FONT), team) for i, team in enumerate(selected_teams)]
        draw_buttons(screen, [button_surface for button_surface, _ in team_buttons])

        # Mostrar equipo seleccionado
        if selected_team:
            selected_text = f"Equipo seleccionado: {selected_team['team_name']}"
            text_surface = settings.BUTTON_FONT.render(selected_text, True, settings.WHITE)
            text_rect = text_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 50))
            screen.blit(text_surface, text_rect)

        # Botón de "Volver"
        back_button = create_button("VOLVER", (settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [back_button])

        # Botón de "Siguiente"
        next_button = create_button("SIGUIENTE", (3 * settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [next_button])

        pygame.display.flip()

    return selected_team
