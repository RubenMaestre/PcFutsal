# run_game.py

import sys
import os

# Añadir el directorio `src` al sys.path para permitir importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import ejecutar_juego  # Importa la función correcta

if __name__ == "__main__":
    ejecutar_juego()  # Llama a la función correcta
