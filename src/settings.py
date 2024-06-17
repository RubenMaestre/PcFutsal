# settings.py
import pygame

# Dimensiones de la ventana
WIDTH = 1920
HEIGHT = 1080

# Frames per second (FPS)
FPS = 60

# Paleta de colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Definición de las fuentes
pygame.init()  # Inicializar Pygame antes de definir fuentes
FONT = pygame.font.Font(None, 74)
BUTTON_FONT = pygame.font.Font(None, 50)
COMMENT_FONT = pygame.font.Font(None, 30)

# Configuraciones de sonido
SOUND_VOLUME = 0.5

# Rutas de archivos
ASSETS_PATH = 'assets/'
