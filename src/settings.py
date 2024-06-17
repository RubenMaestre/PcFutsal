# settings.py
import pygame

# Dimensiones de la ventana
ANCHO = 1920
ALTO = 1080

# Frames per second (FPS)
FPS = 60

# Paleta de colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# Definición de las fuentes
pygame.init()  # Inicializar Pygame antes de definir fuentes
FUENTE = pygame.font.Font(None, 74)
FUENTE_BOTON = pygame.font.Font(None, 50)
FUENTE_COMENTARIO = pygame.font.Font(None, 30)

# Configuraciones de sonido
VOLUMEN_SONIDO = 0.5

# Rutas de archivos
RUTA_RECURSOS = 'assets/'
