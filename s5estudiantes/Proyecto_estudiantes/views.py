# Este módulo es el CONTROLADOR: valida los datos y coordina el modelo con
# el archivo JSON. La interacción por consola se deja para main.py.
from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# Gestor compartido por las operaciones de este módulo.
gestor = GestorJSON("data/estudiantes.json")


# TUPLAS de configuración: centralizan los campos obligatorios y buscables.
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")


# AYUDAS INTERNAS 

def carnets_registrados(excepto_id=None):
    """CONJUNTO con los carnets ya utilizados."""
    # Se comparan en minúsculas para evitar duplicados por diferencia de
    # mayúsculas. Al editar, se excluye al estudiante actual.
    return {
        registro["carnet"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    """Obtiene el siguiente ID disponible."""
    # Usa el id mayor más uno; si no existen registros, empieza en 1.
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1

# CREATE
def crear_estudiante(datos):
    """Crea un estudiante y lo guarda en el archivo JSON."""
    try:
        # Normalizo las entradas y creo un valor para cada campo definido
        # en CAMPOS_ESTUDIANTE, eliminando espacios externos.
        valores = {
            campo: str(datos.get(campo, "")).strip()
            for campo in CAMPOS_ESTUDIANTE
        }

        # Rechazo el registro si falta algún dato obligatorio.
        faltantes = [
            campo
            for campo in CAMPOS_OBLIGATORIOS
            if not valores[campo]
        ]

        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # Valido el correo antes de revisar duplicados o guardar.
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"

        # El conjunto de carnets permite detectar duplicados rápidamente.
        if valores["carnet"].lower() in carnets_registrados():
            return False, "Ese carnet ya está registrado"

        # Los nombres de las claves de valores coinciden con el constructor.
        estudiante = Estudiante(siguiente_id(), **valores)

        # Convierte el modelo a diccionario y lo agrega a la lista JSON.
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())

        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, (
            f"Estudiante {estudiante.obtener_nombre_completo()} "
            f"creado con id {estudiante.id}"
        )

    except Exception as error:
        return False, f"Error inesperado: {error}"
    
# READ
def obtener_todos():
    """Devuelve una LISTA de objetos Estudiante."""
    # Convierte cada diccionario guardado en una instancia del modelo.
    return [
        Estudiante.desde_diccionario(registro)
        for registro in gestor.leer()
    ]


def obtener_por_id(id_estudiante):
    """Busca un estudiante por su ID."""
    # Búsqueda lineal; devuelve None cuando el id no existe.
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante

    return None

# SEARCH

def buscar_estudiantes(termino):
    """Busca estudiantes por nombre, apellido, email o carnet."""
    # Normaliza el término para que la búsqueda ignore mayúsculas y espacios.
    termino = termino.strip().lower()

    if not termino:
        return []

    # Revisa todos los campos buscables y agrega cada estudiante una sola vez.
    encontrados = []

    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(
                    Estudiante.desde_diccionario(registro)
                )
                break

    return encontrados

# UPDATE

def actualizar_estudiante(id_estudiante, cambios):
    """Actualiza los campos indicados de un estudiante."""
    try:
        # La diferencia de conjuntos detecta claves inválidas y evita cambiar
        # el id, ya que no forma parte de CAMPOS_ESTUDIANTE.
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)

        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        if not cambios:
            return False, "No se indicó ningún cambio"

        # Solo se valida el correo si aparece entre los cambios solicitados.
        if "email" in cambios:
            cambios["email"] = cambios["email"].strip()

            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"

        # El carnet debe seguir siendo único, excluyendo al propio estudiante.
        if "carnet" in cambios:
            cambios["carnet"] = cambios["carnet"].strip()

            if cambios["carnet"].lower() in carnets_registrados(
                excepto_id=id_estudiante
            ):
                return False, "Ese carnet ya lo usa otro estudiante"

        registros = gestor.leer()

        posicion = None

        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                posicion = indice
                break

        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        # Actualiza únicamente las claves recibidas y conserva las restantes.
        registros[posicion].update(cambios)

        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, (
            f"Estudiante {id_estudiante} actualizado "
            f"({len(cambios)} campo/s)"
        )

    except Exception as error:
        return False, f"Error inesperado: {error}"
    
# DELETE

def eliminar_estudiante(id_estudiante):
    """Elimina un estudiante por su ID."""
    registros = gestor.leer()

    # Construye una lista nueva sin el estudiante indicado, sin modificar la
    # colección mientras se recorre.
    quedan = [
        registro
        for registro in registros
        if registro["id"] != id_estudiante
    ]

    # Si las listas tienen el mismo tamaño, no se encontró
    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"

    # Guardamos la nueva lista
    if not gestor.guardar(quedan):
        return False, "No se pudo escribir el archivo"

    return True, f"Estudiante {id_estudiante} eliminado"


# FUNCIONES ESPECIALES

def agregar_nota(id_estudiante, materia, nota):
    """Agrega una nota a un estudiante."""

    # Verifica el rango antes de consultar o modificar al estudiante.
    if nota < 0 or nota > 20:
        return False, "La nota debe estar entre 0 y 20"

    estudiante = obtener_por_id(id_estudiante)

    if estudiante is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    materia = materia.strip()

    if not materia:
        return False, "La materia no puede estar vacía"

    # El modelo agrega la nota a su lista y registra la materia en su conjunto.
    estudiante.agregar_nota(materia, nota)

    registros = gestor.leer()

    for registro in registros:
        if registro["id"] == id_estudiante:
            registro.update(estudiante.a_diccionario())
            break

    if not gestor.guardar(registros):
        return False, "No se pudo guardar la nota"

    return True, "Nota agregada correctamente"

def materias_ofertadas():
    """Devuelve un CONJUNTO con todas las materias inscritas."""

    # update() combina los conjuntos de materias sin repetir ninguna.
    materias = set()

    for estudiante in obtener_todos():
        materias.update(estudiante.materias)

    return materias

def estudiantes_en_comun(id_a, id_b):
    """Devuelve las materias que comparten dos estudiantes."""

    estudiante_a = obtener_por_id(id_a)
    estudiante_b = obtener_por_id(id_b)

    if estudiante_a is None:
        return set()

    if estudiante_b is None:
        return set()

    # INTERSECCIÓN de conjuntos
    return estudiante_a.materias & estudiante_b.materias


# ------------------------------------------------------------------
# PRUEBAS DEL CONTROLADOR
# Ejecuta este bloque con: python views.py
# El archivo temporal evita cambiar data/estudiantes.json.
# ------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import tempfile

    gestor_original = gestor
    ruta_temporal = None
    contador_pruebas = [0]

    def comprobar(condicion, descripcion):
        """Comprueba un resultado esperado y muestra el caso validado."""
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
            "carnet": "EST001",
        }
        luis = {
            "nombre": "Luis", "apellido": "Mora", "email": "luis@unemi.edu.ec",
            "carnet": "EST002",
        }

        comprobar(crear_estudiante(ana)[0], "crear primer estudiante")
        comprobar(crear_estudiante(luis)[0], "crear segundo estudiante")
        comprobar(not crear_estudiante({**ana, "carnet": "EST003", "email": "correo-invalido"})[0], "rechazar email inválido")
        comprobar(not crear_estudiante({**ana, "email": "ana2@gmail.com"})[0], "rechazar carnet duplicado")
        comprobar(not crear_estudiante({"nombre": "Eva"})[0], "rechazar campos obligatorios faltantes")
        comprobar(len(obtener_todos()) == 2, "leer todos los estudiantes")
        comprobar(obtener_por_id(1).nombre == "Ana", "buscar estudiante por id")
        comprobar(obtener_por_id(99) is None, "devolver None para id inexistente")
        comprobar(len(buscar_estudiantes("ANA")) == 1, "buscar sin distinguir mayúsculas")
        comprobar(buscar_estudiantes("  ") == [], "no buscar un término vacío")
        comprobar(actualizar_estudiante(1, {"apellido": "Pérez López"})[0], "actualizar un campo")
        comprobar(obtener_por_id(1).apellido == "Pérez López", "leer el valor actualizado")
        comprobar(not actualizar_estudiante(1, {"edad": "20"})[0], "rechazar un campo desconocido")
        comprobar(not actualizar_estudiante(1, {})[0], "rechazar cambios vacíos")
        comprobar(not actualizar_estudiante(1, {"carnet": "EST002"})[0], "rechazar carnet usado por otro estudiante")
        comprobar(not agregar_nota(1, "Matemática", 21)[0], "rechazar nota fuera del rango")
        comprobar(not agregar_nota(99, "Matemática", 18)[0], "rechazar nota para id inexistente")
        comprobar(not agregar_nota(1, "  ", 18)[0], "rechazar materia vacía")
        comprobar(agregar_nota(1, "Matemática", 18)[0], "agregar primera nota")
        comprobar(agregar_nota(1, "Matemática", 20)[0], "agregar otra nota a la materia")
        comprobar(agregar_nota(2, "Matemática", 16)[0], "inscribir segundo estudiante en materia")
        comprobar(agregar_nota(2, "Inglés", 14)[0], "inscribir estudiante en otra materia")
        comprobar(obtener_por_id(1).obtener_promedio() == 19, "calcular promedio")
        comprobar(estudiantes_en_comun(1, 2) == {"Matemática"}, "obtener materias en común")
        comprobar(materias_ofertadas() == {"Matemática", "Inglés"}, "obtener materias ofertadas sin repetir")
        comprobar(estudiantes_en_comun(1, 99) == set(), "devolver conjunto vacío para id inexistente")
        comprobar(eliminar_estudiante(2)[0], "eliminar estudiante existente")
        comprobar(not eliminar_estudiante(2)[0], "rechazar eliminación repetida")
        comprobar(len(obtener_todos()) == 1, "confirmar lista después de eliminar")
        print(f"\nPruebas completadas: {contador_pruebas[0]}")
    finally:
        gestor = gestor_original
        if ruta_temporal and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
