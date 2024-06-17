import pygame
import settings
from proyecto_pcfutbol.manager.src.core.tacticas import Tactics

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

# Dibujar tácticas
def draw_tactics(screen, tactics):
    y_offset = 100
    formation_text = f"Formación: {tactics.formation}"
    formation_surface = FONT.render(formation_text, True, WHITE)
    screen.blit(formation_surface, (50, y_offset))
    
    y_offset += 40
    offensive_text = f"Estrategia Ofensiva: {tactics.offensive_strategy}"
    offensive_surface = FONT.render(offensive_text, True, WHITE)
    screen.blit(offensive_surface, (50, y_offset))
    
    y_offset += 40
    defensive_text = f"Estrategia Defensiva: {tactics.defensive_strategy}"
    defensive_surface = FONT.render(defensive_text, True, WHITE)
    screen.blit(defensive_surface, (50, y_offset))
    
    y_offset += 40
    roles_text = f"Roles: {tactics.roles}"
    roles_surface = FONT.render(roles_text, True, WHITE)
    screen.blit(roles_surface, (50, y_offset))

# Gestión de tácticas
def tactics_management(tactics):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión de Tácticas")
    
    buttons = [
        create_button("Formación: 4-4-2", (settings.WIDTH // 2, settings.HEIGHT - 250)),
        create_button("Estrategia Ofensiva: Posesión", (settings.WIDTH // 2, settings.HEIGHT - 200)),
        create_button("Estrategia Defensiva: Presión Alta", (settings.WIDTH // 2, settings.HEIGHT - 150)),
        create_button("Establecer Roles", (settings.WIDTH // 2, settings.HEIGHT - 100)),
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
                            # Establecer formación
                            tactics.set_formation("4-4-2")
                            buttons[i] = create_button("Formación: 4-4-2", (settings.WIDTH // 2, settings.HEIGHT - 250))
                        elif i == 1:
                            # Establecer estrategia ofensiva
                            tactics.set_offensive_strategy("possession")
                            buttons[i] = create_button("Estrategia Ofensiva: Posesión", (settings.WIDTH // 2, settings.HEIGHT - 200))
                        elif i == 2:
                            # Establecer estrategia defensiva
                            tactics.set_defensive_strategy("high-press")
                            buttons[i] = create_button("Estrategia Defensiva: Presión Alta", (settings.WIDTH // 2, settings.HEIGHT - 150))
                        elif i == 3:
                            # Establecer roles
                            tactics.set_roles({"forward": "target man", "midfielder": "playmaker"})
                        elif i == 4:
                            # Volver al menú principal
                            running = False

        draw_tactics(screen, tactics)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión de tácticas.
if __name__ == "__main__":
    tactics = Tactics("4-4-2", "possession", "high-press", {"forward": "target man", "midfielder": "playmaker"})
    tactics_management(tactics)
