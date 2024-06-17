import pygame
import settings

# Crear botones
def create_button(text, pos, font, color=settings.WHITE):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=pos)
    return text_surface, rect

# Dibujar botones
def draw_buttons(screen, buttons):
    for text_surface, rect in buttons:
        pygame.draw.rect(screen, settings.RED, rect.inflate(20, 20))
        screen.blit(text_surface, rect)

# Función para dividir el texto en múltiples líneas
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width, word_height = font.size(word + ' ')
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(' '.join(current_line))

    return lines
