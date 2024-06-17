import pygame
import settings
from ui.menu2 import team_selection_menu, random_team_menu, career_mode_menu  # Importar las nuevas funciones
from ui.menu3 import user_info_menu  # Importar la función de ingreso de datos del usuario
from ui.ui_helpers import create_button, draw_buttons, wrap_text  # Importar desde ui_helpers

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

# Mostrar el menú del modo de juego
def game_mode_menu(screen):
    modes = [
        ("Modo Entrenador", "Como entrenador, gestionarás el equipo, entrenamientos y tácticas."),
        ("Modo Director Deportivo", "Como director deportivo, manejarás fichajes y contrataciones."),
        ("Modo Presidente", "Como presidente, tomarás decisiones clave para el club.")
    ]
    mode_buttons = [
        create_button(mode[0], (settings.WIDTH // 6, settings.HEIGHT // 2 - 100 + i * 100), BUTTON_FONT) for i, mode in enumerate(modes)
    ]

    option_buttons = []
    option_comments = [
        "Selecciona el equipo con el que quieres jugar.",
        "El equipo será asignado aleatoriamente.",
        "Recibe ofertas y elige tu carrera."
    ]

    selected_mode = None
    running = True
    
    while running:
        screen.blit(MENU_BACKGROUND, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text_surface, rect) in enumerate(mode_buttons):
                    if rect.collidepoint(event.pos):
                        selected_mode = modes[i]
                        option_buttons = [
                            create_button("Elegir Equipo", (settings.WIDTH * 5 // 6, settings.HEIGHT // 2 - 100), BUTTON_FONT),
                            create_button("Modo Aleatorio", (settings.WIDTH * 5 // 6, settings.HEIGHT // 2), BUTTON_FONT),
                            create_button("Modo Carrera", (settings.WIDTH * 5 // 6, settings.HEIGHT // 2 + 100), BUTTON_FONT)
                        ]

            if option_buttons:
                for i, (text_surface, rect) in enumerate(option_buttons):
                    if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos):
                        print(f"Seleccionado: {['Elegir Equipo', 'Modo Aleatorio', 'Modo Carrera'][i]}")
                        if i == 0:
                            selected_team, can_be_fired = team_selection_menu(screen)
                            print(f"Equipo elegido: {selected_team}, Puede ser despedido: {can_be_fired}")
                            user_info, responses = user_info_menu(screen)
                            print("Información del usuario:", user_info)
                            print("Respuestas:", responses)
                            running = False
                        elif i == 1:
                            selected_team, can_be_fired = random_team_menu(screen)
                            print(f"Equipo aleatorio: {selected_team}, Puede ser despedido: {can_be_fired}")
                            user_info, responses = user_info_menu(screen)
                            print("Información del usuario:", user_info)
                            print("Respuestas:", responses)
                            running = False
                        elif i == 2:
                            selected_team = career_mode_menu(screen)
                            print(f"Equipo elegido en modo carrera: {selected_team}")
                            user_info, responses = user_info_menu(screen)
                            print("Información del usuario:", user_info)
                            print("Respuestas:", responses)
                            running = False

        draw_buttons(screen, mode_buttons)
        
        if selected_mode:
            description = selected_mode[1]
            wrapped_text = wrap_text(description, BUTTON_FONT, 500)  # Limitar a 500px de ancho
            for idx, line in enumerate(wrapped_text):
                desc_surface = BUTTON_FONT.render(line, True, WHITE)
                desc_rect = desc_surface.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + idx * 40))
                screen.blit(desc_surface, desc_rect)
            
            draw_buttons(screen, option_buttons)
            for j, (text_surface, rect) in enumerate(option_buttons):
                comment_surface = COMMENT_FONT.render(option_comments[j], True, WHITE)
                comment_rect = comment_surface.get_rect(center=(rect.centerx, rect.centery + 40))
                screen.blit(comment_surface, comment_rect)

        # Botón de Volver
        back_button = create_button("VOLVER", (settings.WIDTH // 2, settings.HEIGHT - 50), COMMENT_FONT)
        draw_buttons(screen, [back_button])
        if back_button[1].collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            running = False
        
        pygame.display.flip()
    
    return selected_mode
