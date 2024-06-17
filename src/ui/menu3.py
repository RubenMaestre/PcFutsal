import pygame
import settings
import csv
from ui.ui_helpers import create_button, draw_buttons, wrap_text

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir fuentes
FONT = pygame.font.Font(None, 40)
BUTTON_FONT = pygame.font.Font(None, 30)
COMMENT_FONT = pygame.font.Font(None, 25)

# Preguntas y opciones
questions = [
    ("¿Qué tipo de táctica te gusta?", ["4-4-2", "4-3-3", "4-2-3-1", "4-2-4", "4-3-2-1", "3-4-3", "3-5-2", "3-3-3-1", "3-6-1", "2-3-2-3", "5-3-2", "5-4-1", "otra personalizada"]),
    ("¿Qué tipo de fútbol te gusta?", ["Ofensivo", "Defensivo", "Control", "Posesión", "Defensa adelantada", "Salir a la contra", "Equilibrado"]),
    ("¿Qué tipo de personalidad tienes?", ["Impulsivo", "Tranquilo", "Equilibrado", "Analítico", "Pensador", "Creativo"]),
    ("¿Qué tipo de jugador prefieres?", ["Fichar a los mejores", "Formar jugadores de la base", "Apostar por jóvenes", "Apostar por talentos desconocidos", "Formador", "Exigente"]),
    ("¿Qué emoción te define más?", ["Ganador", "Trabajador", "Constante", "Impulsivo", "Creativo", "Desarrollar carrera", "Especialista en situaciones de crisis"])
]

# Función para cargar los países desde el CSV
def load_countries(file_path):
    countries = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            countries.append(row['country_name'])
    return countries

# Función para mostrar el menú de ingreso de datos del usuario y preguntas
def user_info_menu(screen):
    countries = load_countries('data/countries.csv')
    user_info = {"nombre": "", "apellido": "", "edad": "", "nacionalidad": ""}
    responses = {}

    input_boxes = {
        "nombre": pygame.Rect(settings.WIDTH // 2 - 100, 150, 200, 40),
        "apellido": pygame.Rect(settings.WIDTH // 2 - 100, 200, 200, 40),
        "edad": pygame.Rect(settings.WIDTH // 2 - 100, 250, 200, 40)
    }
    active_box = None
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    nationality_button = create_button("Seleccionar nacionalidad", (settings.WIDTH // 2, 300), BUTTON_FONT)
    nationality_selected = None

    running = True
    while running:
        screen.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, box in input_boxes.items():
                    if box.collidepoint(event.pos):
                        active_box = key
                        color = color_active
                    else:
                        color = color_inactive
                if nationality_button[1].collidepoint(event.pos):
                    nationality_selected = countries

                # Botón de "Volver"
                if back_button[1].collidepoint(event.pos):
                    running = False
                # Botón de "Siguiente"
                if next_button[1].collidepoint(event.pos):
                    print("Información del usuario:", user_info)
                    print("Respuestas:", responses)
                    running = False
            elif event.type == pygame.KEYDOWN:
                if active_box is not None:
                    if event.key == pygame.K_RETURN:
                        active_box = None
                        color = color_inactive
                    elif event.key == pygame.K_BACKSPACE:
                        user_info[active_box] = user_info[active_box][:-1]
                    else:
                        user_info[active_box] += event.unicode

        for key, box in input_boxes.items():
            txt_surface = FONT.render(user_info[key], True, color)
            width = max(200, txt_surface.get_width() + 10)
            box.w = width
            screen.blit(txt_surface, (box.x + 5, box.y + 5))
            pygame.draw.rect(screen, color, box, 2)

        # Dibujar etiquetas para los campos de entrada
        labels = ["Nombre", "Apellido", "Edad", "Nacionalidad"]
        y_offset = 150
        for i, label in enumerate(labels):
            label_surface = FONT.render(label, True, settings.WHITE)
            screen.blit(label_surface, (settings.WIDTH // 2 - 300, y_offset))
            y_offset += 50

        # Dibujar el botón de nacionalidad
        draw_buttons(screen, [nationality_button])
        if nationality_selected:
            for i, country in enumerate(countries):
                country_button = create_button(country, (settings.WIDTH // 2, 350 + i * 40), BUTTON_FONT)
                draw_buttons(screen, [country_button])
                if country_button[1].collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    user_info["nacionalidad"] = country
                    nationality_selected = False
                    break

        # Dibujar texto de preguntas y opciones
        y_offset = 400 + len(countries) * 40 if nationality_selected else 350
        for i, (question, options) in enumerate(questions):
            question_surface = FONT.render(question, True, settings.WHITE)
            screen.blit(question_surface, (50, y_offset))
            y_offset += 40
            for j, option in enumerate(options):
                option_button = create_button(option, (settings.WIDTH // 4 * (j % 4 + 1), y_offset), BUTTON_FONT)
                draw_buttons(screen, [option_button])
                if option_button[1].collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    responses[question] = option
            y_offset += 40

        # Botón de "Volver"
        back_button = create_button("VOLVER", (settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [back_button])

        # Botón de "Siguiente"
        next_button = create_button("SIGUIENTE", (3 * settings.WIDTH // 4, settings.HEIGHT - 50), settings.COMMENT_FONT)
        draw_buttons(screen, [next_button])

        pygame.display.flip()

    return user_info, responses
