import os


# DICCIONARIO: nombre del color -> código ANSI que colorea la consola.
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "BLANCO": "\033[97m",
    "RESET": "\033[0m",
}


# TUPLA: respuestas que confirmar() interpreta como afirmativas.
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")


def limpiar_pantalla():
    # El comando utilizado depende del sistema operativo.
    os.system("clear" if os.name == "posix" else "cls")
    
def imprimir_color(texto, color):
    # Si el nombre del color no existe, usa blanco como valor predeterminado.
    codigo = COLORES.get(color, COLORES["BLANCO"])
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto):
    # Limpia la consola y muestra un encabezado uniforme.
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
    # Normaliza la respuesta antes de compararla con las opciones afirmativas.
    respuesta = input(f"{pregunta} (si/no): ").strip().lower()
    return respuesta in RESPUESTAS_SI


def es_email_valido(texto):
    # Validación básica: un usuario, un solo @ y un dominio con punto.
    texto = texto.strip()

    if texto.count("@") != 1:
        return False

    usuario, dominio = texto.split("@")

    return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")