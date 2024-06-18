# src/ui/game/menu_principal_gestion.py

import pygame
import settings
from src.core.juego import principal
from src.ui.ui_helpers import crear_boton, dibujar_botones

def menu_principal_gestion(pantalla, equipo_seleccionado, puede_ser_despedido, modo_juego):
    juego = principal(equipo_seleccionado, puede_ser_despedido, modo_juego)
    print("Nuevo juego iniciado.")
    print("Mostrando el menú de gestión...")

    botones = [
        crear_boton("RESULTADOS", (settings.ANCHO // 4, settings.ALTO // 4), settings.FUENTE_BOTON),
        crear_boton("CLASIFICACIÓN", (settings.ANCHO // 4, settings.ALTO // 4 + 60), settings.FUENTE_BOTON),
        crear_boton("CALENDARIO", (settings.ANCHO // 4, settings.ALTO // 4 + 120), settings.FUENTE_BOTON),
        crear_boton("FICHAR", (settings.ANCHO // 4, settings.ALTO // 2), settings.FUENTE_BOTON),
        crear_boton("PLANTILLA", (settings.ANCHO // 4, settings.ALTO // 2 + 60), settings.FUENTE_BOTON),
        crear_boton("EMPLEADOS", (settings.ANCHO // 4, settings.ALTO // 2 + 120), settings.FUENTE_BOTON),
        crear_boton("ALINEACIÓN", (3 * settings.ANCHO // 4, settings.ALTO // 4), settings.FUENTE_BOTON),
        crear_boton("TÁCTICAS", (3 * settings.ANCHO // 4, settings.ALTO // 4 + 60), settings.FUENTE_BOTON),
        crear_boton("VER RIVAL", (3 * settings.ANCHO // 4, settings.ALTO // 4 + 120), settings.FUENTE_BOTON),
        crear_boton("CAJA", (3 * settings.ANCHO // 4, settings.ALTO // 2), settings.FUENTE_BOTON),
        crear_boton("DECISIONES", (3 * settings.ANCHO // 4, settings.ALTO // 2 + 60), settings.FUENTE_BOTON),
        crear_boton("ESTADIO", (3 * settings.ANCHO // 4, settings.ALTO // 2 + 120), settings.FUENTE_BOTON),
        crear_boton("SALIR", (settings.ANCHO // 2, settings.ALTO - 50), settings.FUENTE_BOTON)
    ]

    corriendo = True
    while corriendo:
        pantalla.blit(pygame.image.load('assets/menu_background.png'), (0, 0))  # Fondo del menú

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, (superficie_texto, rect) in enumerate(botones):
                    if rect.collidepoint(evento.pos):
                        if i == 0:
                            mostrar_resultados(pantalla, juego)
                        elif i == 1:
                            mostrar_clasificacion(pantalla, juego)
                        elif i == 2:
                            mostrar_calendario(pantalla, juego)
                        elif i == 3:
                            mostrar_fichar(pantalla)
                        elif i == 4:
                            mostrar_plantilla(pantalla)
                        elif i == 5:
                            mostrar_empleados(pantalla)
                        elif i == 6:
                            mostrar_alineacion(pantalla)
                        elif i == 7:
                            mostrar_tacticas(pantalla)
                        elif i == 8:
                            mostrar_ver_rival(pantalla)
                        elif i == 9:
                            mostrar_caja(pantalla)
                        elif i == 10:
                            mostrar_decisiones(pantalla)
                        elif i == 11:
                            mostrar_estadio(pantalla)
                        elif i == 12:
                            corriendo = False

        dibujar_botones(pantalla, botones)
        pygame.display.flip()

    pygame.quit()

def mostrar_resultados(pantalla, juego):
    volver_boton = crear_boton("VOLVER", (settings.ANCHO // 2, settings.ALTO - 50), settings.FUENTE_BOTON)
    corriendo = True
    while corriendo:
        pantalla.fill(settings.NEGRO)
        y_offset = 50
        for nombre_liga, competicion in juego.ligas.items():
            texto_liga = settings.FUENTE_BOTON.render(f"{nombre_liga}", True, settings.BLANCO)
            pantalla.blit(texto_liga, (50, y_offset))
            y_offset += 40
            for i, partidos in enumerate(competicion.calendario):
                texto_jornada = settings.FUENTE_COMENTARIO.render(f"Jornada {i + 1}", True, settings.BLANCO)
                pantalla.blit(texto_jornada, (100, y_offset))
                y_offset += 30
                for partido in partidos:
                    texto_partido = settings.FUENTE_COMENTARIO.render(f"{partido[0].nombre} vs {partido[1].nombre}", True, settings.BLANCO)
                    pantalla.blit(texto_partido, (150, y_offset))
                    y_offset += 20
                y_offset += 10
            y_offset += 30

        dibujar_botones(pantalla, [volver_boton])
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if volver_boton[1].collidepoint(evento.pos):
                    corriendo = False

def mostrar_clasificacion(pantalla, juego):
    volver_boton = crear_boton("VOLVER", (settings.ANCHO // 2, settings.ALTO - 50), settings.FUENTE_BOTON)
    corriendo = True
    while corriendo:
        pantalla.fill(settings.NEGRO)  # Limpiar la pantalla
        clasificacion = juego.ligas['Primera División'].obtener_clasificacion()  # Obtener la clasificación de la liga

        # Dibujar la clasificación en la pantalla
        fuente = pygame.font.Font(None, 36)
        y_offset = 50
        for posicion, (nombre_equipo, puntos) in enumerate(clasificacion, start=1):
            texto = f"{posicion}. {nombre_equipo} - {puntos} puntos"
            superficie_texto = fuente.render(texto, True, settings.BLANCO)
            pantalla.blit(superficie_texto, (50, y_offset))
            y_offset += 40

        dibujar_botones(pantalla, [volver_boton])
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if volver_boton[1].collidepoint(evento.pos):
                    corriendo = False

def mostrar_calendario(pantalla, juego):
    volver_boton = crear_boton("VOLVER", (settings.ANCHO // 2, settings.ALTO - 50), settings.FUENTE_BOTON)
    corriendo = True
    while corriendo:
        pantalla.fill(settings.NEGRO)  # Limpiar la pantalla
        calendario = juego.ligas['Primera División'].calendario  # Obtener el calendario de la liga

        # Dibujar el calendario en la pantalla
        fuente = pygame.font.Font(None, 36)
        y_offset = 50
        for jornada, partidos in enumerate(calendario, start=1):
            texto_jornada = f"Jornada {jornada}"
            superficie_texto_jornada = fuente.render(texto_jornada, True, settings.BLANCO)
            pantalla.blit(superficie_texto_jornada, (50, y_offset))
            y_offset += 30
            for equipo1, equipo2 in partidos:
                texto_partido = f"{equipo1.nombre} vs {equipo2.nombre}"
                superficie_texto_partido = fuente.render(texto_partido, True, settings.BLANCO)
                pantalla.blit(superficie_texto_partido, (100, y_offset))
                y_offset += 30
            y_offset += 20

        dibujar_botones(pantalla, [volver_boton])
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if volver_boton[1].collidepoint(evento.pos):
                    corriendo = False

def mostrar_fichar(pantalla):
    pass  # Implementar la pantalla de fichar

def mostrar_plantilla(pantalla):
    pass  # Implementar la pantalla de plantilla

def mostrar_empleados(pantalla):
    pass  # Implementar la pantalla de empleados

def mostrar_alineacion(pantalla):
    pass  # Implementar la pantalla de alineación

def mostrar_tacticas(pantalla):
    pass  # Implementar la pantalla de tácticas

def mostrar_ver_rival(pantalla):
    pass  # Implementar la pantalla de ver rival

def mostrar_caja(pantalla):
    pass  # Implementar la pantalla de caja

def mostrar_decisiones(pantalla):
    pass  # Implementar la pantalla de decisiones

def mostrar_estadio(pantalla):
    pass  # Implementar la pantalla de estadio
