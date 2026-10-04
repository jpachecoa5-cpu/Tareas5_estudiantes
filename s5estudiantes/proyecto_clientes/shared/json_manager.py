import json
import os


class GestorJSON:
    """Lee y guarda una lista de diccionarios en un archivo JSON."""

    def __init__(self, ruta):
        # Guarda la ruta y prepara su carpeta cuando se indicó una.
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def leer(self):
        # Devuelve siempre una lista. Un archivo inexistente, inválido o con
        # contenido JSON de otro tipo se interpreta como una lista vacía.
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            # Capturamos errores concretos, nunca un "except:" pelado
            return []

    def guardar(self, datos):
        # Serializa la lista con indentación y conserva caracteres Unicode.
        try:
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (TypeError, OSError):
            # TypeError aparece si intentas guardar un set: JSON no lo conoce
            return False