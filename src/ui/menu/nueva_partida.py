# src/ui/menu/nueva_partida.py

import pygame
import settings
from src.ui.menu.seleccionar_liga import menu_seleccion_equipo, menu_equipo_aleatorio, menu_modo_carrera  # Importar las nuevas funciones
from src.ui.menu.usuario import menu_informacion_usuario  # Importar la función de ingreso de datos del usuario
from src.ui.ui_helpers import crear_boton, dibujar_botones, ajustar_texto  # Importar desde ui_helpers

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir colores
BLANCO = settings.BLANCO
NEGRO = settings.NEGRO
ROJO = settings.ROJO

# Definir fuentes
FUENTE_BOTON = pygame.font.Font(None, 50)
FUENTE_COMENTARIO = pygame.font.Font(None, 30)

# Cargar la imagen de fondo del menú
FONDO_MENU = pygame.image.load(settings.RUTA_RECURSOS + 'menu_background.png')

# Mostrar el menú del modo de juego
def menu_modo_juego(pantalla):
    modos = [
        ("Modo Entrenador", "Como entrenador, gestionarás el equipo, entrenamientos y tácticas."),
        ("Modo Director Deportivo", "Como director deportivo, manejarás fichajes y contrataciones."),
        ("Modo Presidente", "Como presidente, tomarás decisiones clave para el club.")
    ]
    botones_modo = [
        crear_boton(modo[0], (settings.ANCHO // 6, settings.ALTO // 2 - 100 + i * 100), FUENTE_BOTON) for i, modo in enumerate(modos)
    ]

    botones_opcion = []
    comentarios_opcion = [
        "Selecciona el equipo con el que quieres jugar.",
        "El equipo será asignado aleatoriamente.",
        "Recibe ofertas y elige tu carrera."
    ]

    modo_seleccionado = None
    corriendo = True
    
    while corriendo:
        pantalla.blit(FONDO_MENU, (0, 0))
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, (superficie_texto, rect) in enumerate(botones_modo):
                    if rect.collidepoint(evento.pos):
                        modo_seleccionado = modos[i]
                        botones_opcion = [
                            crear_boton("Elegir Equipo", (settings.ANCHO * 5 // 6, settings.ALTO // 2 - 100), FUENTE_BOTON),
                            crear_boton("Modo Aleatorio", (settings.ANCHO * 5 // 6, settings.ALTO // 2), FUENTE_BOTON),
                            crear_boton("Modo Carrera", (settings.ANCHO * 5 // 6, settings.ALTO // 2 + 100), FUENTE_BOTON)
                        ]

            if botones_opcion:
                for i, (superficie_texto, rect) in enumerate(botones_opcion):
                    if evento.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(evento.pos):
                        if i == 0:
                            equipo_seleccionado, puede_ser_despedido = menu_seleccion_equipo(pantalla)
                            info_usuario, respuestas = menu_informacion_usuario(pantalla)
                            corriendo = False
                        elif i == 1:
                            equipo_seleccionado, puede_ser_despedido = menu_equipo_aleatorio(pantalla)
                            info_usuario, respuestas = menu_informacion_usuario(pantalla)
                            corriendo = False
                        elif i == 2:
                            equipo_seleccionado = menu_modo_carrera(pantalla)
                            info_usuario, respuestas = menu_informacion_usuario(pantalla)
                            corriendo = False

        dibujar_botones(pantalla, botones_modo)
        
        if modo_seleccionado:
            descripcion = modo_seleccionado[1]
            texto_ajustado = ajustar_texto(descripcion, FUENTE_BOTON, 500)  # Limitar a 500px de ancho
            for idx, linea in enumerate(texto_ajustado):
                superficie_desc = FUENTE_BOTON.render(linea, True, BLANCO)
                rect_desc = superficie_desc.get_rect(center=(settings.ANCHO // 2, settings.ALTO // 2 + idx * 40))
                pantalla.blit(superficie_desc, rect_desc)
            
            dibujar_botones(pantalla, botones_opcion)
            for j, (superficie_texto, rect) in enumerate(botones_opcion):
                superficie_comentario = FUENTE_COMENTARIO.render(comentarios_opcion[j], True, BLANCO)
                rect_comentario = superficie_comentario.get_rect(center=(rect.centerx, rect.centery + 40))
                pantalla.blit(superficie_comentario, rect_comentario)

        # Botón de Volver
        boton_volver = crear_boton("VOLVER", (settings.ANCHO // 2, settings.ALTO - 50), FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_volver])
        if boton_volver[1].collidepoint(pygame.mouse.get_pos()) and evento.type == pygame.MOUSEBUTTONDOWN:
            corriendo = False
        
        pygame.display.flip()
    
    return modo_seleccionado
