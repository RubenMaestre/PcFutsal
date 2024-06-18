import pygame
import settings
import csv
from src.ui.ui_helpers import crear_boton, dibujar_botones, ajustar_texto  # Importar funciones auxiliares
from src.ui.game.menu_principal_gestion import menu_principal_gestion  # Importar la función del menú principal de gestión

# Inicializar Pygame (esto se debe hacer en main.py realmente)
pygame.init()

# Definir fuentes
FUENTE = pygame.font.Font(None, 40)
FUENTE_BOTON = pygame.font.Font(None, 30)
FUENTE_COMENTARIO = pygame.font.Font(None, 25)

# Preguntas y opciones
preguntas = [
    ("¿Qué tipo de táctica te gusta?", ["1-2-1", "2-2", "3-1", "2-1-1", "juego de 4"]),
    ("¿Qué tipo de fútbol te gusta?", ["Ofensivo", "Defensivo", "Control", "Posesión", "Defensa adelantada", "Salir a la contra", "Equilibrado"]),
    ("¿Qué tipo de personalidad tienes?", ["Impulsivo", "Tranquilo", "Equilibrado", "Analítico", "Pensador", "Creativo"]),
    ("¿Qué tipo de jugador prefieres?", ["Fichar a los mejores", "Formar jugadores de la base", "Apostar por jóvenes", "Apostar por talentos desconocidos", "Formador", "Exigente"]),
    ("¿Qué emoción te define más?", ["Ganador", "Trabajador", "Constante", "Impulsivo", "Creativo", "Desarrollar carrera", "Especialista en situaciones de crisis"])
]

# Función para cargar los países desde el CSV
def cargar_paises(ruta_archivo):
    paises = []
    with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.DictReader(archivo)
        for fila in lector_csv:
            paises.append(fila['nombre_pais'])
    return paises

# Función para mostrar el menú de ingreso de datos del usuario y preguntas
def menu_informacion_usuario(pantalla):
    paises = cargar_paises('data/paises.csv')
    info_usuario = {"nombre": "", "apellido": "", "edad": "", "nacionalidad": ""}
    respuestas = {}

    cajas_entrada = {
        "nombre": pygame.Rect(settings.ANCHO // 2 - 100, 150, 200, 40),
        "apellido": pygame.Rect(settings.ANCHO // 2 - 100, 200, 200, 40),
        "edad": pygame.Rect(settings.ANCHO // 2 - 100, 250, 200, 40)
    }
    caja_activa = None
    color_inactivo = pygame.Color('lightskyblue3')
    color_activo = pygame.Color('dodgerblue2')
    color = color_inactivo

    boton_nacionalidad = crear_boton("Seleccionar nacionalidad", (settings.ANCHO // 2, 300), FUENTE_BOTON)
    nacionalidad_seleccionada = None

    corriendo = True
    while corriendo:
        pantalla.blit(pygame.image.load(settings.RUTA_RECURSOS + 'menu_background.png'), (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for clave, caja in cajas_entrada.items():
                    if caja.collidepoint(evento.pos):
                        caja_activa = clave
                        color = color_activo
                    else:
                        color = color_inactivo
                if boton_nacionalidad[1].collidepoint(evento.pos):
                    nacionalidad_seleccionada = paises

                # Botón de "Volver"
                if boton_volver[1].collidepoint(evento.pos):
                    corriendo = False
                # Botón de "Siguiente"
                if boton_siguiente[1].collidepoint(evento.pos):
                    print("Información del usuario:", info_usuario)
                    print("Respuestas:", respuestas)
                    equipo_seleccionado = "Elche"  # Aquí debería ser el equipo seleccionado en tu lógica
                    puede_ser_despedido = True  # Aquí deberías obtener si puede ser despedido de tu lógica
                    modo_juego = "Modo Entrenador"  # Aquí deberías obtener el modo de juego seleccionado
                    menu_principal_gestion(pantalla, equipo_seleccionado, puede_ser_despedido, modo_juego)
                    return info_usuario, respuestas  # Termina el bucle y devuelve los datos del usuario

            elif evento.type == pygame.KEYDOWN:
                if caja_activa is not None:
                    if evento.key == pygame.K_RETURN:
                        caja_activa = None
                        color = color_inactivo
                    elif evento.key == pygame.K_BACKSPACE:
                        info_usuario[caja_activa] = info_usuario[caja_activa][:-1]
                    else:
                        info_usuario[caja_activa] += evento.unicode

        for clave, caja in cajas_entrada.items():
            superficie_texto = FUENTE.render(info_usuario[clave], True, color)
            ancho = max(200, superficie_texto.get_width() + 10)
            caja.w = ancho
            pantalla.blit(superficie_texto, (caja.x + 5, caja.y + 5))
            pygame.draw.rect(pantalla, color, caja, 2)

        # Dibujar etiquetas para los campos de entrada
        etiquetas = ["Nombre", "Apellido", "Edad", "Nacionalidad"]
        y_offset = 150
        for i, etiqueta in enumerate(etiquetas):
            superficie_etiqueta = FUENTE.render(etiqueta, True, settings.BLANCO)
            pantalla.blit(superficie_etiqueta, (settings.ANCHO // 2 - 300, y_offset))
            y_offset += 50

        # Dibujar el botón de nacionalidad
        dibujar_botones(pantalla, [boton_nacionalidad])
        if nacionalidad_seleccionada:
            for i, pais in enumerate(paises):
                boton_pais = crear_boton(pais, (settings.ANCHO // 2, 350 + i * 40), FUENTE_BOTON)
                dibujar_botones(pantalla, [boton_pais])
                if boton_pais[1].collidepoint(pygame.mouse.get_pos()) and evento.type == pygame.MOUSEBUTTONDOWN:
                    info_usuario["nacionalidad"] = pais
                    nacionalidad_seleccionada = False
                    break

        # Dibujar texto de preguntas y opciones
        y_offset = 400 + len(paises) * 40 if nacionalidad_seleccionada else 350
        for i, (pregunta, opciones) in enumerate(preguntas):
            superficie_pregunta = FUENTE.render(pregunta, True, settings.BLANCO)
            pantalla.blit(superficie_pregunta, (50, y_offset))
            y_offset += 40
            for j, opcion in enumerate(opciones):
                boton_opcion = crear_boton(opcion, (settings.ANCHO // 4 * (j % 4 + 1), y_offset), FUENTE_BOTON)
                dibujar_botones(pantalla, [boton_opcion])
                if boton_opcion[1].collidepoint(pygame.mouse.get_pos()) and evento.type == pygame.MOUSEBUTTONDOWN:
                    respuestas[pregunta] = opcion
            y_offset += 40

        # Botón de "Volver"
        boton_volver = crear_boton("VOLVER", (settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_volver])

        # Botón de "Siguiente"
        boton_siguiente = crear_boton("SIGUIENTE", (3 * settings.ANCHO // 4, settings.ALTO - 50), settings.FUENTE_COMENTARIO)
        dibujar_botones(pantalla, [boton_siguiente])

        pygame.display.flip()

    return info_usuario, respuestas
