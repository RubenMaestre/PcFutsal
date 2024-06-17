import pygame
import settings

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

# Pantalla de opciones
def options_menu():
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Opciones")
    
    volume = settings.SOUND_VOLUME
    fps = settings.FPS
    
    buttons = [
        create_button("Volumen: " + str(volume), (settings.WIDTH // 2, settings.HEIGHT // 2 - 100)),
        create_button("FPS: " + str(fps), (settings.WIDTH // 2, settings.HEIGHT // 2)),
        create_button("Volver", (settings.WIDTH // 2, settings.HEIGHT // 2 + 100))
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
                            # Ajustar volumen
                            volume = (volume + 0.1) % 1.1
                            settings.SOUND_VOLUME = volume
                            buttons[i] = create_button("Volumen: " + str(round(volume, 1)), (settings.WIDTH // 2, settings.HEIGHT // 2 - 100))
                        elif i == 1:
                            # Ajustar FPS
                            fps = (fps + 10) % 121
                            settings.FPS = fps
                            buttons[i] = create_button("FPS: " + str(fps), (settings.WIDTH // 2, settings.HEIGHT // 2))
                        elif i == 2:
                            # Volver al menú principal
                            running = False

        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la pantalla de opciones.
if __name__ == "__main__":
    options_menu()
