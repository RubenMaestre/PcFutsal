from datetime import date
from nucleo.models import Temporada


def get_or_create_temporada(nombre: str) -> Temporada:
    """
    Recupera o crea una temporada en la base de datos a partir del nombre '2025-2026'.
    Si no existe, la crea con fecha_inicio = 1 de julio del primer año y fecha_fin = 30 de junio del siguiente.
    """
    # Convertir formato 2025-2026 → 2025/2026 (formato base de datos)
    nombre_db = nombre.replace("-", "/")

    # Extraer año inicial
    try:
        anio_inicio = int(nombre.split("-")[0])
    except ValueError:
        anio_inicio = date.today().year

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
