# main.py es la VISTA: solicita entradas y muestra resultados al usuario.
# La lógica de validación y persistencia se delega al módulo views.py.
from models import CAMPOS_CLIENTE
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    crear_cliente, obtener_todos, obtener_por_id, buscar_clientes,
    actualizar_cliente, eliminar_cliente, estadisticas
)


def pausa():
    # Mantiene la pantalla actual visible hasta que el usuario continúe.
    input("\nPresione Enter para continuar...")


def mostrar_tabla(clientes):
    # Formatea la lista de objetos Cliente en columnas para facilitar su lectura.
    print(f"{'ID':<5}{'NOMBRE':<25}{'EMAIL':<28}{'CIUDAD':<15}{'TELÉFONO':<12}")
    print("-" * 85)
    for cliente in clientes:
        print(f"{cliente.id:<5}{cliente.obtener_nombre_completo():<25}"
              f"{cliente.email:<28}{cliente.ciudad:<15}{cliente.telefono:<12}")
    print("-" * 85)
    imprimir_info(f"Total: {len(clientes)} cliente(s)")


# ---------- C · CREAR ----------
def opcion_crear():
    imprimir_titulo("CREAR NUEVO CLIENTE")
    # Recorre la tupla compartida de campos para no duplicar nombres aquí.
    # Si cambia el modelo, el formulario usa automáticamente la misma definición.
    datos = {}
    for campo in CAMPOS_CLIENTE:
        datos[campo] = input(f"{campo.capitalize()}: ")

    # El controlador devuelve una tupla (exito, mensaje).
    exito, mensaje = crear_cliente(datos)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ---------- R · LEER TODOS ----------
def opcion_ver_todos():
    imprimir_titulo("LISTA DE CLIENTES")
    # Solicita al controlador la lista de objetos Cliente.
    clientes = obtener_todos()
    if not clientes:
        imprimir_info("Todavía no hay clientes. Use la opción 1 para crear el primero.")
    else:
        mostrar_tabla(clientes)
    pausa()


# ---------- S · BUSCAR ----------
def opcion_buscar():
    imprimir_titulo("BUSCAR CLIENTE")
    termino = input("Nombre, email, teléfono o ciudad: ")
    # El controlador normaliza el término y realiza la búsqueda.
    encontrados = buscar_clientes(termino)

    if not encontrados:
        imprimir_info(f"Ningún cliente coincide con '{termino}'.")
    else:
        mostrar_tabla(encontrados)
    pausa()


# ---------- R · LEER UNO ----------
def opcion_ver_por_id():
    imprimir_titulo("VER CLIENTE POR ID")
    # Convierte la entrada a entero y maneja texto que no represente un id.
    try:
        id_cliente = int(input("Id del cliente: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    cliente = obtener_por_id(id_cliente)
    if not cliente:
        imprimir_error(f"No existe un cliente con id {id_cliente}")
    else:
        # Recorre el diccionario del modelo para mostrar todos sus campos.
        for clave, valor in cliente.a_diccionario().items():
            print(f"  {clave.capitalize():<12}: {valor}")
    pausa()


# ---------- U · ACTUALIZAR ----------
def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR CLIENTE")
    try:
        id_cliente = int(input("Id del cliente: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    cliente = obtener_por_id(id_cliente)
    if not cliente:
        imprimir_error(f"No existe un cliente con id {id_cliente}")
        return pausa()

    imprimir_info(f"Editando a {cliente.obtener_nombre_completo()}")
    print("Deje en blanco el campo que no quiera cambiar.\n")

    # Solo se incluyen los campos no vacíos; los demás quedan sin cambios.
    cambios = {}
    for campo in CAMPOS_CLIENTE:
        actual = getattr(cliente, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    exito, mensaje = actualizar_cliente(id_cliente, cambios)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ---------- D · ELIMINAR ----------
def opcion_eliminar():
    imprimir_titulo("ELIMINAR CLIENTE")
    try:
        id_cliente = int(input("Id del cliente: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    cliente = obtener_por_id(id_cliente)
    if not cliente:
        imprimir_error(f"No existe un cliente con id {id_cliente}")
        return pausa()

    imprimir_info(f"Se eliminará: {cliente}")
    # La eliminación requiere confirmación explícita antes de modificar datos.
    if confirmar("¿Confirma la eliminación?"):
        exito, mensaje = eliminar_cliente(id_cliente)
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ---------- EXTRA · ESTADÍSTICAS ----------
def opcion_estadisticas():
    imprimir_titulo("ESTADÍSTICAS")
    # El controlador arma las colecciones; aquí solo se presentan.
    datos = estadisticas()
    print(f"  Clientes registrados : {datos['total']}")
    print(f"  Ciudades distintas   : {len(datos['ciudades'])} -> {', '.join(datos['ciudades'])}")
    print(f"  Dominios de email    : {', '.join(datos['dominios'])}")
    print(f"  Sin teléfono         : {len(datos['sin_telefono'])}")
    pausa()


def salir():
    imprimir_info("¡Hasta luego! 👋")
    # El valor de retorno le indica a main() que termine el ciclo del menú.
    return "salir"


# DICCIONARIO de opciones: cada tecla se asocia con el texto y su función.
# Así el ciclo principal evita una larga cadena de if/elif.
OPCIONES = {
    "1": ("Crear cliente", opcion_crear),
    "2": ("Ver todos", opcion_ver_todos),
    "3": ("Buscar", opcion_buscar),
    "4": ("Ver por id", opcion_ver_por_id),
    "5": ("Actualizar", opcion_actualizar),
    "6": ("Eliminar", opcion_eliminar),
    "7": ("Estadísticas", opcion_estadisticas),
    "0": ("Salir", salir),
}


def mostrar_menu():
    # Muestra las opciones configuradas en el diccionario OPCIONES.
    imprimir_titulo("SISTEMA DE GESTIÓN DE CLIENTES")
    for tecla, (texto, _funcion) in OPCIONES.items():
        print(f"  {tecla}. {texto}")
    print()


def main():
    # Repite el menú hasta que una opción indique que se debe salir.
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()

        # Consultar una clave del diccionario permite validar la opción elegida.
        if tecla not in OPCIONES:
            imprimir_error("Opción no válida")
            pausa()
            continue

        # Desempaqueta el texto y la función asociada a la tecla.
        _texto, funcion = OPCIONES[tecla]
        if funcion() == "salir":
            break


if __name__ == "__main__":
    # Este bloque se ejecuta al iniciar main.py, pero no al importarlo.
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")