import pygame
import settings
from proyecto_pcfutbol.manager.src.core.finanzas import Finance

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

# Dibujar reporte financiero
def draw_financial_report(screen, finance):
    y_offset = 100
    report = finance.get_financial_report()
    for key, value in report.items():
        report_text = f"{key}: {value}"
        report_surface = FONT.render(report_text, True, WHITE)
        screen.blit(report_surface, (50, y_offset))
        y_offset += 40

# Gestión financiera
def finance_management(finance):
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Manager - Gestión Financiera")
    
    buttons = [
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
                            running = False

        draw_financial_report(screen, finance)
        draw_buttons(screen, buttons)
        
        pygame.display.flip()

    pygame.quit()

# Si ejecutas este archivo directamente, muestra la gestión financiera.
if __name__ == "__main__":
    finance = Finance(1000000)
    finance_management(finance)
