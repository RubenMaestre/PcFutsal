import pygame
import settings
from ui.menu.inicio import menu_principal
from ui.game.menu_principal_gestion import menu_principal_gestion
from ui.menu.usuario import menu_informacion_usuario

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
VENTANA = pygame.display.set_mode((settings.ANCHO, settings.ALTO))
pygame.display.set_caption("PcFutsal")

# Ejecutar el menú principal
def ejecutar_juego():
    juego = menu_principal()
    if juego:
        # Mostrar el menú de información del usuario después del menú principal
        info_usuario, respuestas = menu_informacion_usuario(VENTANA)
        
        # Luego, mostrar el menú de gestión del usuario
        menu_principal_gestion(VENTANA)
        
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
