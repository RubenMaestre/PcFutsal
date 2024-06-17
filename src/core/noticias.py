# src/core/noticias.py

class Noticia:
    def __init__(self, titular, contenido, fecha):
        self.titular = titular
        self.contenido = contenido
        self.fecha = fecha  # Fecha de la noticia

    def mostrar_noticia(self):
        """Mostrar la noticia"""
        print(f"{self.fecha} - {self.titular}")
        print(self.contenido)
