import pygame
import settings
from proyecto_pcfutbol.manager.src.core.entrenamiento import Training

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

# Dibujar sesiones de entrenamiento
def draw_training_sessions(screen, training):
    y_offset = 100
    for skill, intensity in training.sessions.items():
        session_text = f"Entrenamiento: {skill} - Intensidad: {intensity}"
        session_surface = FONT.render(session_text, True, WHITE)
        screen.blit(session_surface, (50, y_offset))
        y_offset += 40

# Gestión de entrenamientos
def training_management(training, team):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión de Entrenamientos")
    
    buttons = [
        create_button("Añadir Entrenamiento: Dribbling", (settings.WIDTH // 2, settings.HEIGHT - 150)),
        create_button("Añadir Entrenamiento: Passing", (settings.WIDTH // 2, settings.HEIGHT - 100)),
        create_button("Ejecutar Entrenamientos", (settings.WIDTH // 2, settings.HEIGHT - 50)),
        create_button("Volver", (settings.WIDTH // 2, settings.HEIGHT - 20))
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
                            # Añadir entrenamiento de dribbling
                            training.add_session("dribbling", 3)
                        elif i == 1:
                            # Añadir entrenamiento de passing
                            training.add_session("passing", 2)
                        elif i == 2:
                            # Ejecutar entrenamientos
                            training.execute_training(team)
                        elif i == 3:
                            # Volver al menú principal
                            running = False

        draw_training_sessions(screen, training)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión de entrenamientos.
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.equipo import Team
    from proyecto_pcfutbol.manager.src.core.jugador import Player

    team = Team("Mi Equipo", 1000000)
    team.add_player(Player("Jugador 1", 20, "Midfielder", {"dribbling": 70, "passing": 65}))
    
    training = Training({"dribbling": 3, "passing": 2})
    training_management(training, team)
