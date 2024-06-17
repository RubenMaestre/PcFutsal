import pygame
import settings
import csv
import random
from ui.ui_helpers import crear_boton, dibujar_botones

# Funciones para cargar datos desde CSV
def cargar_competiciones(file_path):
    competiciones = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                competiciones.append(row)
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
    return competiciones

def cargar_equipos(file_path):
    equipos = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                equipos.append(row)
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
    return equipos

# Función para mostrar el menú de selección de equipo
def menu_seleccion_equipo(pantalla):
    competiciones = cargar_competiciones('data/competiciones.csv')
    equipos = cargar_equipos('data/equipos.csv')

    botones_competiciones = []
    botones_equipos = []
    pais_seleccionado = "España"
    competicion_seleccionada = None
    equipo_seleccionado = None
    puede_ser_despedido = False  # Inicialmente no puede ser despedido

    # Crear botón único para España
    boton_espana = crear_boton("España", (settings.ANCHO // 4, 150), settings.FUENTE_BOTON)

    corriendo = True
    while corriendo:
        pantalla.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if competicion_seleccionada is None:
                    if boton_espana[1].collidepoint(evento.pos):
                        botones_competiciones = [
                            (crear_boton(competicion['nombre_competicion'], (settings.ANCHO // 2, 150 + j * 60), settings.FUENTE_BOTON), competicion)
                            for j, competicion in enumerate(competiciones)
                            if competicion['nombre_pais'] == pais_seleccionado
                        ]
                else:
                    for i, (superficie_boton, competicion) in enumerate(botones_competiciones):
                        if superficie_boton[1].collidepoint(evento.pos):
                            competicion_seleccionada = competicion
                            botones_equipos = [
                                (crear_boton(equipo['nombre_equipo'], (3 * settings.ANCHO // 4, 150 + k * 60), settings.FUENTE_BOTON), equipo)
                                for k, equipo in enumerate(equipos)
                                if equipo['liga'] == competicion_seleccionada['nombre_competicion']
                            ]
                            equipo_seleccionado = None
                for i, (superficie_boton, equipo) in enumerate(botones_equipos):
                    if superficie_boton[1].collidepoint(evento.pos):
                        equipo_seleccionado = equipo
                # Check para despido
                if casilla_despido.collidepoint(evento.pos):
                    puede_ser_despedido = not puede_ser_despedido

        if competicion_seleccionada is None:
            dibujar_botones(pantalla, [boton_espana])
        else:
            dibujar_botones(pantalla, [superficie_boton for superficie_boton, _ in botones_competiciones])
            dibujar_botones(pantalla, [superficie_boton for superficie_boton, _ in botones_equipos])

        # Mostrar información de selección
        if pais_seleccionado:
            texto_seleccionado = f"País seleccionado: {pais_seleccionado}"
            superficie_texto = settings.FUENTE_BOTON.render(texto_seleccionado, True, settings.BLANCO)
            rect_texto = superficie_texto.get_rect(center=(settings.ANCHO // 2, settings.ALTO - 150))
            pantalla.blit(superficie_texto, rect_texto)

        if competicion_seleccionada:
            texto_seleccionado = f"Competición seleccionada: {competicion_seleccionada['nombre_competicion']}"
            superficie_texto = settings.FUENTE_BOTON.render(texto_seleccionado, True, settings.BLANCO)
            rect_texto = superficie_texto.get_rect(center=(settings.ANCHO // 2, settings.ALTO - 100))
            pantalla.blit(superficie_texto, rect_texto)

        if equipo_seleccionado:
            texto_seleccionado = f"Equipo seleccionado: {equipo_seleccionado['nombre_equipo']}"
            superficie_texto = settings.FUENTE_BOTON.render(texto_seleccionado, True, settings.BLANCO)
            rect_texto = superficie_texto.get_rect(center=(settings.ANCHO // 2, settings.ALTO - 50))
            pantalla.blit(superficie_texto, rect_texto)

        # Check para despido
        casilla_despido = pygame.Rect(settings.ANCHO // 2 - 100, settings.ALTO - 200, 20, 20)
        pygame.draw.rect(pantalla, settings.BLANCO, casilla_despido, 2)
        if puede_ser_despedido:
            pygame.draw.rect(pantalla, settings.BLANCO, casilla_despido)
        texto_despido = settings.FUENTE_BOTON.render("Selecciona aquí si puedes ser despedido del club", True, settings.BLANCO)
        pantalla.blit(texto_despido, (settings.ANCHO // 2 - 70, settings.ALTO - 205))

        # Botón de "Volver"
        boton_volver = crear_boton("VOLVER", (settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_volver])
        if boton_volver[1].collidepoint(pygame.mouse.get_pos()) and evento.type == pygame.MOUSEBUTTONDOWN:
            corriendo = False

        # Botón de "Siguiente"
        if equipo_seleccionado:
            boton_siguiente = crear_boton("SIGUIENTE", (3 * settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
            dibujar_botones(pantalla, [boton_siguiente])
            if boton_siguiente[1].collidepoint(evento.pos) and evento.type == pygame.MOUSEBUTTONDOWN:
                print(f"Equipo seleccionado: {equipo_seleccionado['nombre_equipo']}")
                corriendo = False

        pygame.display.flip()

    return equipo_seleccionado, puede_ser_despedido

# Función para mostrar el menú de selección aleatoria de equipo
def menu_equipo_aleatorio(pantalla):
    equipos = cargar_equipos('data/equipos.csv')
    equipo_seleccionado = random.choice(equipos)
    puede_ser_despedido = False

    corriendo = True
    while corriendo:
        pantalla.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # Check para despido
                if casilla_despido.collidepoint(evento.pos):
                    puede_ser_despedido = not puede_ser_despedido
                # Botón de "Volver a Barajar"
                if boton_barajar[1].collidepoint(evento.pos):
                    equipo_seleccionado = random.choice(equipos)
                # Botón de "Volver"
                if boton_volver[1].collidepoint(evento.pos):
                    corriendo = False
                # Botón de "Siguiente"
                if boton_siguiente[1].collidepoint(evento.pos):
                    print(f"Equipo seleccionado: {equipo_seleccionado['nombre_equipo']}")
                    corriendo = False

        texto_seleccionado = f"Equipo seleccionado: {equipo_seleccionado['nombre_equipo']}"
        superficie_texto = settings.FUENTE_BOTON.render(texto_seleccionado, True, settings.BLANCO)
        rect_texto = superficie_texto.get_rect(center=(settings.ANCHO // 2, settings.ALTO // 2))
        pantalla.blit(superficie_texto, rect_texto)

        # Check para despido
        casilla_despido = pygame.Rect(settings.ANCHO // 2 - 100, settings.ALTO - 200, 20, 20)
        pygame.draw.rect(pantalla, settings.BLANCO, casilla_despido, 2)
        if puede_ser_despedido:
            pygame.draw.rect(pantalla, settings.BLANCO, casilla_despido)
        texto_despido = settings.FUENTE_BOTON.render("Selecciona aquí si puedes ser despedido del club", True, settings.BLANCO)
        pantalla.blit(texto_despido, (settings.ANCHO // 2 - 70, settings.ALTO - 205))

        # Botón de "Volver a Barajar"
        boton_barajar = crear_boton("Volver a Barajar", (settings.ANCHO // 2, settings.ALTO // 2 + 100), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_barajar])

        # Botón de "Volver"
        boton_volver = crear_boton("VOLVER", (settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_volver])

        # Botón de "Siguiente"
        boton_siguiente = crear_boton("SIGUIENTE", (3 * settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_siguiente])

        pygame.display.flip()

    return equipo_seleccionado, puede_ser_despedido

# Función para mostrar el menú del modo carrera
def menu_modo_carrera(pantalla):
    equipos = cargar_equipos('data/equipos.csv')
    equipos_seleccionados = random.sample(equipos, 3)  # Seleccionar 3 equipos aleatorios
    equipo_seleccionado = None

    corriendo = True
    while corriendo:
        pantalla.blit(pygame.image.load('assets/menu_background.png'), (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, (superficie_boton, equipo) in enumerate(botones_equipos):
                    if superficie_boton[1].collidepoint(evento.pos):
                        equipo_seleccionado = equipo
                # Botón de "Volver"
                if boton_volver[1].collidepoint(evento.pos):
                    corriendo = False
                # Botón de "Siguiente"
                if equipo_seleccionado and boton_siguiente[1].collidepoint(evento.pos):
                    print(f"Equipo seleccionado en modo carrera: {equipo_seleccionado['nombre_equipo']}")
                    corriendo = False

        botones_equipos = [(crear_boton(equipo['nombre_equipo'], (settings.ANCHO // 2, 150 + i * 100), settings.FUENTE_BOTON), equipo) for i, equipo in enumerate(equipos_seleccionados)]
        dibujar_botones(pantalla, [superficie_boton for superficie_boton, _ in botones_equipos])

        # Mostrar equipo seleccionado
        if equipo_seleccionado:
            texto_seleccionado = f"Equipo seleccionado: {equipo_seleccionado['nombre_equipo']}"
            superficie_texto = settings.FUENTE_BOTON.render(texto_seleccionado, True, settings.BLANCO)
            rect_texto = superficie_texto.get_rect(center=(settings.ANCHO // 2, settings.ALTO - 50))
            pantalla.blit(superficie_texto, rect_texto)

        # Botón de "Volver"
        boton_volver = crear_boton("VOLVER", (settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_volver])

        # Botón de "Siguiente"
        boton_siguiente = crear_boton("SIGUIENTE", (3 * settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_siguiente])

        pygame.display.flip()

    return equipo_seleccionado
