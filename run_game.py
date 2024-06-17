import sys
import os

# Añadir el directorio `src` al sys.path para permitir importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import run_game

if __name__ == "__main__":
    run_game()
