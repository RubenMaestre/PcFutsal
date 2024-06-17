# src/core/ver_estadisticas.py

def mostrar_clasificacion(clasificacion):
    """Función para mostrar la clasificación."""
    clasificacion_ordenada = sorted(clasificacion.items(), key=lambda x: x[1], reverse=True)
    print("Clasificación:")
    for posicion, (nombre_equipo, puntos) in enumerate(clasificacion_ordenada, start=1):
        print(f"{posicion}. {nombre_equipo} - {puntos} puntos")

# Función principal para probar la clasificación (puedes eliminar esto más adelante si no es necesario)
def main():
    from src.core.cargar_equipos import cargar_equipos, asignar_equipos_a_ligas
    from src.core.competicion import Competicion

    equipos = cargar_equipos('data/equipos.csv')
    ligas = asignar_equipos_a_ligas(equipos)
    primera_division = ligas['Primera División']

    competicion = Competicion(primera_division)

    for numero_jornada in range(len(competicion.calendario)):
        competicion.jugar_jornada(numero_jornada)
    
    competicion.mostrar_clasificacion()

if __name__ == "__main__":
    main()
