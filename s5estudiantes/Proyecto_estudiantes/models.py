# TUPLA de campos para crear/actualizar estudiantes, compartida entre Vista
# y Controlador para evitar repetir nombres de campos.
CAMPOS_ESTUDIANTE = (
    "nombre",
    "apellido",
    "email",
    "carnet",
)

class Estudiante:
    """MODELO: representa un estudiante y administra sus notas y materias."""

    def __init__(self, id_estudiante, nombre, apellido, email, carnet, notas=None, materias=None):
        self.id = id_estudiante
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.carnet = carnet

        # DICCIONARIO DE LISTAS: cada materia apunta a sus notas.
        # {"Matemática": [18, 19], "Inglés": [17]}
        self.notas = notas if notas else {}

        # CONJUNTO: materias inscritas, sin elementos repetidos.
        self.materias = set(materias) if materias else set()

    def obtener_nombre_completo(self):
        # Centraliza la forma de presentar el nombre y el apellido.
        return f"{self.nombre} {self.apellido}"

    def inscribir_materia(self, materia):
        # add() incorpora una materia solo si aún no está en el conjunto.
        self.materias.add(materia)

    def agregar_nota(self, materia, nota):
        # Registrar una nota también inscribe al estudiante en la materia.
        self.inscribir_materia(materia)

        # setdefault crea la lista vacía la primera vez que aparece la materia.
        self.notas.setdefault(materia, []).append(nota)

    def obtener_promedio(self):
        # Junta las notas de todas las materias para calcular el promedio global.
        todas = []

        for lista_notas in self.notas.values():
            todas.extend(lista_notas)

        if not todas:
            return 0

        return round(sum(todas) / len(todas), 2)

    def materias_en_comun(self, otro_estudiante):
        # La intersección devuelve las materias que comparten ambos estudiantes.
        return self.materias & otro_estudiante.materias

    def a_diccionario(self):
        # Convierte el objeto a tipos compatibles con JSON.
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carnet": self.carnet,
            "notas": self.notas,

            # JSON no serializa conjuntos; se guardan como lista ordenada.
            "materias": sorted(self.materias),
        }

    @classmethod
    def desde_diccionario(cls, datos):
        # Reconstruye el objeto y convierte la lista de materias en conjunto.
        return cls(
            datos["id"],
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["carnet"],
            notas=datos.get("notas", {}),
            materias=set(datos.get("materias", [])),
        )

    def __str__(self):
        # Devuelve una representación legible para mensajes de consola.
        return f"[{self.carnet}] {self.obtener_nombre_completo()} - Promedio: {self.obtener_promedio()}"