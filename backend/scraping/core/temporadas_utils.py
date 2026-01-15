from datetime import date
from nucleo.models import Temporada


def get_or_create_temporada(nombre: str) -> Temporada:
    """
    Recupera o crea una temporada en la base de datos a partir del nombre '2025-2026'.
    
    Si no existe, la crea con fecha_inicio = 1 de julio del primer año y fecha_fin = 30 de junio del siguiente.
    Esto sigue el formato estándar de temporadas deportivas en España (julio a junio).
    
    El formato del nombre puede ser '2025-2026' (con guión) o '2025/2026' (con barra).
    Internamente se normaliza a '2025/2026' para consistencia en la BD.
    """
    # Convertir formato 2025-2026 → 2025/2026 (formato base de datos).
    # Esto permite aceptar ambos formatos sin importar cómo venga el nombre.
    nombre_db = nombre.replace("-", "/")

    # Extraer año inicial del nombre de la temporada.
    # Si falla el parsing, usar el año actual como fallback.
    try:
        anio_inicio = int(nombre.split("-")[0])
    except ValueError:
        anio_inicio = date.today().year

    # Fechas estándar de temporada deportiva en España:
    # Inicio: 1 de julio del año inicial
    # Fin: 30 de junio del año siguiente
    fecha_inicio = date(anio_inicio, 7, 1)
    fecha_fin = date(anio_inicio + 1, 6, 30)

    temporada, creada = Temporada.objects.get_or_create(
        nombre=nombre_db,
        defaults={
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        },
    )

    if creada:
        print(f"[temporadas_utils] Nueva temporada creada: {temporada.nombre} ({fecha_inicio} → {fecha_fin})")
    else:
        print(f"[temporadas_utils] Temporada ya existente: {temporada.nombre}")

    return temporada
