# src/main.py

import pygame
import settings
from ui.menu.inicio import menu_principal

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
VENTANA = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
pygame.display.set_caption("PcFutsal")

# Ejecutar el menú principal
def ejecutar_juego():
    juego = menu_principal()
    if juego:
        while juego.corriendo:
            juego.avanzar_semana()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    juego.corriendo = False

            # Actualizar lógica del juego
            juego.actualizar_logica()

            # Renderizar gráficos
            VENTANA.fill(settings.NEGRO)  # Usar color definido en settings

            pygame.display.flip()
            juego.reloj.tick(settings.FPS)  # Usar FPS definido en settings

        pygame.quit()

if __name__ == "__main__":
    ejecutar_juego()
