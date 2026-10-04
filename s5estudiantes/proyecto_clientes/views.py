# Este módulo funciona como CONTROLADOR: valida y coordina el CRUD de clientes.
# No solicita datos ni imprime resultados; esas tareas pertenecen a main.py.
from models import Cliente, CAMPOS_CLIENTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

# Gestor compartido por las funciones del módulo. Mantiene la persistencia JSON.
gestor = GestorJSON("data/clientes.json")

# TUPLAS de configuración: son constantes y centralizan los nombres de campos.
# Solo estos campos se exigen al crear un cliente.
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email")
# Estos campos se revisan al buscar; dirección no forma parte de la búsqueda.
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "telefono", "ciudad")


# ===================== AYUDAS INTERNAS =====================

def emails_registrados(excepto_id=None):
    """CONJUNTO con los emails ya usados. Sirve para detectar duplicados al instante."""
    # Se normaliza a minúsculas para que Ana@ejemplo.com y ana@ejemplo.com
    # cuenten como el mismo correo. Al actualizar, se excluye al dueño actual.
    return {
        registro["email"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    # Los ids nuevos se calculan a partir del mayor id existente, no del total
    # de registros. Si no hay clientes todavía, el primer id es 1.
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_cliente(datos):
    """datos: diccionario con las claves de CAMPOS_CLIENTE. Devuelve (exito, mensaje)."""
    try:
        # Normalizo los campos en el orden definido por la tupla. str() permite
        # recibir valores no textuales y strip() elimina espacios exteriores.
        valores = {campo: str(datos.get(campo, "")).strip() for campo in CAMPOS_CLIENTE}

        # Rechazo la creación si falta algún campo obligatorio.
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if not valores[campo]]
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # El formato se valida antes de consultar duplicados o guardar.
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"

        # El conjunto permite detectar duplicados sin distinguir mayúsculas.
        if valores["email"].lower() in emails_registrados():
            return False, "Ese email ya está registrado"

        # **valores pasa cada campo como argumento nombrado al constructor.
        cliente = Cliente(siguiente_id(), **valores)

        # Se agrega al final de los registros actuales y se guarda el JSON.
        registros = gestor.leer()
        registros.append(cliente.a_diccionario())
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, f"Cliente {cliente.obtener_nombre_completo()} creado con id {cliente.id}"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== R · READ =====================

def obtener_todos():
    """LISTA de objetos Cliente."""
    # Convierte cada diccionario persistido en un objeto del modelo.
    return [Cliente.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_cliente):
    # Búsqueda lineal: si no hay coincidencia, se devuelve None.
    for cliente in obtener_todos():
        if cliente.id == id_cliente:
            return cliente
    return None


# ===================== S · SEARCH =====================

def buscar_clientes(termino):
    """Búsqueda lineal: revisa registro por registro los campos de CAMPOS_BUSCABLES."""
    # La búsqueda no distingue mayúsculas y espacios al principio/final.
    termino = termino.strip().lower()
    if not termino:
        return []

    # Revisa los campos buscables de cada registro y lo añade una sola vez.
    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:                 # recorro la TUPLA de campos
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(Cliente.desde_diccionario(registro))
                break                                   # ya coincidió: paso al siguiente cliente
    return encontrados


# ===================== U · UPDATE =====================

def actualizar_cliente(id_cliente, cambios):
    """cambios: diccionario solo con los campos que se quieren modificar."""
    try:
        # La diferencia de conjuntos detecta claves desconocidas y evita que
        # se altere el id, que no pertenece a CAMPOS_CLIENTE.
        desconocidos = set(cambios) - set(CAMPOS_CLIENTE)
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        if not cambios:
            return False, "No se indicó ningún cambio"

        # Solo se valida el correo cuando forma parte de los cambios.
        if "email" in cambios:
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in emails_registrados(excepto_id=id_cliente):
                return False, "Ese email ya lo usa otro cliente"

        # Busca la posición para modificar el diccionario dentro de la lista.
        registros = gestor.leer()
        posicion = None
        for indice, registro in enumerate(registros):   # enumerate me da índice y valor
            if registro["id"] == id_cliente:
                posicion = indice
                break

        if posicion is None:
            return False, f"No existe un cliente con id {id_cliente}"

        # update() reemplaza los campos indicados y conserva los demás.
        registros[posicion].update(cambios)
        gestor.guardar(registros)
        return True, f"Cliente {id_cliente} actualizado ({len(cambios)} campo/s)"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================

def eliminar_cliente(id_cliente):
    # Se crea una lista nueva sin el cliente elegido; no se elimina mientras
    # se recorre la lista original.
    registros = gestor.leer()
    # Construyo una LISTA NUEVA sin ese registro: nunca borro mientras recorro
    quedan = [registro for registro in registros if registro["id"] != id_cliente]

    if len(quedan) == len(registros):
        return False, f"No existe un cliente con id {id_cliente}"

    gestor.guardar(quedan)
    return True, f"Cliente {id_cliente} eliminado"


# ===================== EXTRA: estadísticas con conjuntos =====================

def estadisticas():
    """Devuelve un DICCIONARIO de resumen. Práctica pura de colecciones."""
    # Cada colección responde a una necesidad distinta: ciudades/dominios
    # únicos con conjuntos y nombres sin teléfono con una lista.
    registros = gestor.leer()
    ciudades = {r.get("ciudad", "").title() for r in registros if r.get("ciudad")}
    dominios = {r["email"].split("@")[1].lower() for r in registros if "@" in r["email"]}
    sin_telefono = [r["nombre"] for r in registros if not r.get("telefono")]

    return {
        "total": len(registros),
        "ciudades": sorted(ciudades),
        "dominios": sorted(dominios),
        "sin_telefono": sin_telefono,
    }


# ------------------------------------------------------------------
# PRUEBA DEL CONTROLADOR
# Este bloque se ejecuta únicamente con: python views.py
# Usa un archivo temporal, de modo que no modifica data/clientes.json.
# ------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import tempfile

    gestor_original = gestor
    ruta_temporal = None
    contador_pruebas = [0]

    def comprobar(condicion, descripcion):
        """Asegura un resultado esperado y muestra qué caso se está probando."""
        contador_pruebas[0] += 1
        if not condicion:
            raise AssertionError(f"Falló la prueba: {descripcion}")
        print(f"[OK] {descripcion}")

    try:
        archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        ruta_temporal = archivo_temporal.name
        archivo_temporal.close()
        gestor = GestorJSON(ruta_temporal)
        gestor.guardar([])

        ana = {
            "nombre": "Ana", "apellido": "Pérez", "email": "ana@gmail.com",
            "telefono": "0991234567", "ciudad": "Milagro", "direccion": "Av. Principal",
        }
        luis = {
            "nombre": "Luis", "apellido": "Mora", "email": "luis@unemi.edu.ec",
            "telefono": "", "ciudad": "Guayaquil", "direccion": "",
        }

        comprobar(crear_cliente(ana)[0], "crear primer cliente")
        comprobar(crear_cliente(luis)[0], "crear segundo cliente")
        comprobar(not crear_cliente(ana)[0], "rechazar email duplicado")
        comprobar(not crear_cliente({"nombre": "Eva"})[0], "rechazar campos obligatorios faltantes")
        comprobar(len(obtener_todos()) == 2, "leer todos los clientes")
        comprobar(obtener_por_id(1).nombre == "Ana", "buscar cliente por id")
        comprobar(obtener_por_id(99) is None, "devolver None para id inexistente")
        comprobar(len(buscar_clientes("MILAGRO")) == 1, "buscar sin distinguir mayúsculas")
        comprobar(buscar_clientes("   ") == [], "no buscar un término vacío")
        comprobar(actualizar_cliente(1, {"ciudad": "Quito"})[0], "actualizar un campo")
        comprobar(obtener_por_id(1).ciudad == "Quito", "leer el valor actualizado")
        comprobar(not actualizar_cliente(99, {"ciudad": "Quito"})[0], "rechazar actualización de id inexistente")
        comprobacion_estadisticas = estadisticas()
        comprobar(comprobacion_estadisticas["total"] == 2, "contar clientes en estadísticas")
        comprobar(comprobacion_estadisticas["ciudades"] == ["Guayaquil", "Quito"], "listar ciudades únicas ordenadas")
        comprobar(comprobacion_estadisticas["sin_telefono"] == ["Luis"], "identificar clientes sin teléfono")
        comprobar(eliminar_cliente(2)[0], "eliminar cliente existente")
        comprobar(not eliminar_cliente(2)[0], "rechazar eliminación repetida")
        comprobar(len(obtener_todos()) == 1, "confirmar lista después de eliminar")
        print(f"\nPruebas completadas: {contador_pruebas[0]}")
    finally:
        gestor = gestor_original
        if ruta_temporal and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)