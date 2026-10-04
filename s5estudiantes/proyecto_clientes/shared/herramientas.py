import os

# DICCIONARIO: nombre del color -> secuencia ANSI que colorea la consola.
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "BLANCO": "\033[97m",
    "RESET": "\033[0m",
}

# TUPLA: respuestas afirmativas reconocidas por confirmar().
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")


def limpiar_pantalla():
    # El comando depende del sistema operativo en el que se ejecuta Python.
    os.system("clear" if os.name == "posix" else "cls")


def imprimir_color(texto, color):
    # Si el color no existe, se utiliza blanco como opción predeterminada.
    codigo = COLORES.get(color, COLORES["BLANCO"])   # .get evita el error si el color no existe
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto):
    # Limpia la consola y muestra un encabezado consistente para cada pantalla.
    limpiar_pantalla()
    imprimir_color("=" * 60, "AZUL")
    print(f"  {texto}".center(60))
    imprimir_color("=" * 60, "AZUL")
    print()


def imprimir_exito(mensaje):
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"✗ {mensaje}", "ROJO")


def imprimir_info(mensaje):
    imprimir_color(f"ℹ {mensaje}", "CYAN")


def confirmar(pregunta):
    # Normaliza la respuesta antes de comprobarla contra la tupla afirmativa.
    respuesta = input(f"{pregunta} (si/no): ").strip().lower()
    return respuesta in RESPUESTAS_SI


def es_email_valido(texto):
    # Validación básica para este ejercicio: un @, usuario no vacío y un punto
    # dentro del dominio, que no puede terminar en punto.
    texto = texto.strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")