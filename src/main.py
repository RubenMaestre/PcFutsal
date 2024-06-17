import pygame
import settings
from ui.menu import main_menu

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
WINDOW = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Manager")

# Ejecutar el menú principal
def run_game():
    game = main_menu()
    if game:
        while game.running:
            game.advance_week()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False

            # Actualizar lógica del juego
            game.update_logic()

            # Renderizar gráficos
            WINDOW.fill(settings.BLACK)  # Usar color definido en settings

            pygame.display.flip()
            game.clock.tick(settings.FPS)  # Usar FPS definido en settings

        pygame.quit()

if __name__ == "__main__":
    run_game()
