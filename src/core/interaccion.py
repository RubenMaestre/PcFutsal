# src/core/interaccion.py

from src.core.entrenador import Entrenador
from src.core.director_deportivo import DirectorDeportivo
from src.core.presidente import Presidente

def interactuar_entrenador_director(entrenador: Entrenador, director: DirectorDeportivo):
    if director.tipos_entrenador_preferidos[0] in entrenador.tipos_jugador_preferidos:
        print(f"{director.nombre} y {entrenador.nombre} trabajan bien juntos.")
    else:
        print(f"{director.nombre} y {entrenador.nombre} tienen conflictos.")

