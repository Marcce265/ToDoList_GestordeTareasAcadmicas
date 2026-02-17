from datetime import date
import unittest
from src.logic.task_manager import TaskManager
from src.model.declarative_base import Base, engine
from src.model.modelo import Usuario  # Importamos para aserciones


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        """Prepara la base de datos para cada prueba."""
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()

    def test_hu001_rojo_crear_usuario_nombre_vacio(self):
        """
        HU-001 - Caso rojo
        No se debe permitir crear usuario con nombre vacío
        """
        with self.assertRaises(ValueError) as context:
            self.tm.crear_usuario("", "test@mail.com")
        self.assertIn("nombre", str(context.exception).lower())

    def test_hu001_rojo_crear_usuario_correo_vacio(self):
        """
        HU-001 - Caso rojo
        No se debe permitir crear usuario con correo vacío
        """
        with self.assertRaises(ValueError) as context:
            self.tm.crear_usuario("Test User", "")
        self.assertIn("correo", str(context.exception).lower())

    def test_hu001_rojo_crear_usuario_correo_duplicado(self):
        """
        HU-001 - Caso rojo
        No se debe permitir crear usuario con correo ya registrado
        """
        self.tm.crear_usuario("Juan", "test@mail.com")

        with self.assertRaises(ValueError) as context:
            self.tm.crear_usuario("Pedro", "test@mail.com")
        self.assertIn("correo", str(context.exception).lower())

    def test_hu001_verde_crear_usuario_caso_feliz(self):
        """
        HU-001 - Caso verde
        Crear usuario con datos válidos
        """
        usuario = self.tm.crear_usuario("Juan Pérez", "juan@mail.com")

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nombre, "Juan Pérez")
        self.assertEqual(usuario.correo, "juan@mail.com")
        self.assertIsNotNone(usuario.fecha_creacion)

    def test_hu002_rojo_seleccionar_usuario_id_cero(self):
        """
        HU-002 - Caso rojo
        No se debe permitir ID cero
        """
        with self.assertRaises(ValueError) as context:
            self.tm.seleccionar_usuario(0)
        self.assertIn("id", str(context.exception).lower())

    def test_hu002_rojo_seleccionar_usuario_id_negativo(self):
        """
        HU-002 - Caso rojo
        No se debe permitir ID negativo
        """
        with self.assertRaises(ValueError) as context:
            self.tm.seleccionar_usuario(-5)
        self.assertIn("id", str(context.exception).lower())

    def test_hu002_rojo_seleccionar_usuario_inexistente(self):
        """
        HU-002 - Caso rojo
        Debe retornar None si el usuario no existe
        """
        usuario = self.tm.seleccionar_usuario(999)
        self.assertIsNone(usuario)

    def test_hu002_verde_seleccionar_usuario_caso_feliz(self):
        """
        HU-002 - Caso verde
        Seleccionar usuario existente por ID
        """
        usuario_creado = self.tm.crear_usuario("Juan", "juan@mail.com")
        usuario = self.tm.seleccionar_usuario(usuario_creado.idUsuario)

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nombre, "Juan")
        self.assertEqual(usuario.correo, "juan@mail.com")

    def test_hu003_rojo_crear_materia_usuario_inexistente(self):
        """
        HU-003 - Caso rojo
        No se debe permitir crear materia sin usuario válido
        """
        with self.assertRaises(ValueError) as context:
            self.tm.crear_materia(999, "Matemáticas", "Azul")

        self.assertIn("usuario", str(context.exception).lower())

    def test_hu003_rojo_crear_materia_nombre_vacio(self):
        """
        HU-003 - Caso rojo
        No se debe permitir crear materia con nombre vacío
        """
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")

        with self.assertRaises(ValueError) as context:
            self.tm.crear_materia(usuario.idUsuario, "", "Azul")

        self.assertIn("nombre", str(context.exception).lower())

    def test_hu003_rojo_crear_materia_color_vacio(self):
        """
        HU-003 - Caso rojo
        No se debe permitir crear materia con color vacío
        """
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")

        with self.assertRaises(ValueError) as context:
            self.tm.crear_materia(usuario.idUsuario, "Matemáticas", "")

        self.assertIn("color", str(context.exception).lower())

    def test_hu003_rojo_crear_materia_caso_feliz(self):
        """
        HU-003 - Caso rojo
        Crear una materia válida asociada a un usuario
        """
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")

        materia = self.tm.crear_materia(
            usuario.idUsuario,
            "Matemáticas",
            "Azul"
        )

        self.assertIsNotNone(materia)
        self.assertEqual(materia.nombre, "Matemáticas")
        self.assertEqual(materia.color, "Azul")
        self.assertEqual(materia.usuario_id, usuario.idUsuario)

    def test_hu004_rojo_crear_tarea_titulo_vacio(self):
        """
        HU-004 - Escenario 1 (Rojo)
        No se debe permitir crear una tarea con título vacío
        """
        # 1. Preparación (Setup)
        from src.model.modelo import Materia, Prioridad
        from src.model.declarative_base import session
        
        # Creamos un usuario usando el método que ya existe
        usuario = self.tm.crear_usuario("Ana", "ana@mail.com")
        
        # Creamos una materia directamente en la base de datos para la prueba
        materia = Materia(nombre="Física", color="Rojo", usuario_id=usuario.idUsuario)
        session.add(materia)
        session.commit()
        session.refresh(materia)
        materia_id = materia.idMateria

        # 2. Acción y Aserción
        with self.assertRaises(ValueError) as context:
            # Intentamos crear la tarea con título vacío
            self.tm.crear_tarea(
                titulo="", 
                descripcion="Resolver ejercicios de cinemática",
                prioridad=Prioridad.Media,
                fecha_entrega=date.today(),
                materia_id=materia_id
            )
        
        # Verificamos que el error mencione el problema con el título
        self.assertIn("título", str(context.exception).lower())

    def test_hu004_rojo_crear_tarea_materia_inexistente(self):
        """
        HU-004 - Escenario 2 (Rojo)
        No se debe permitir crear una tarea si la materia_id no existe.
        """
        from src.model.modelo import Prioridad
        from datetime import date
        
        with self.assertRaises(ValueError) as context:
            # Intentamos crear tarea con materia_id = 9999 (que no existe)
            self.tm.crear_tarea(
                titulo="Aprobar el curso", 
                descripcion="Terminar el proyecto de software",
                prioridad=Prioridad.Alta,
                fecha_entrega=date.today(),
                materia_id=9999
            )
        
        # El mensaje de error debe mencionar que la materia no existe
        self.assertIn("materia", str(context.exception).lower())

    def test_hu004_rojo_crear_tarea_prioridad_invalida(self):
        """
        HU-004 - Escenario 3 (Rojo)
        No se debe permitir crear una tarea con una prioridad fuera del Enum permitido.
        """
        from src.model.modelo import Materia
        from src.model.declarative_base import session
        from datetime import date

        # 1. Preparación: Creamos un usuario y una materia reales para que no falle por eso
        usuario = self.tm.crear_usuario("Carlos", "carlos@mail.com")
        materia = Materia(nombre="Química", color="Azul", usuario_id=usuario.idUsuario)
        session.add(materia)
        session.commit()
        session.refresh(materia)
        materia_id = materia.idMateria

        # 2. Acción y Aserción
        with self.assertRaises(ValueError) as context:
            self.tm.crear_tarea(
                titulo="Hacer informe de laboratorio", 
                descripcion="Mezclar reactivos",
                prioridad="Súper Urgente",  # <--- TRAMPA: Esto es un string, no el Enum Prioridad
                fecha_entrega=date.today(),
                materia_id=materia_id
            )
        
        # 3. Verificamos que el error mencione el problema con la prioridad
        self.assertIn("prioridad", str(context.exception).lower())

    def test_hu004_verde_crear_tarea_caso_feliz(self):
        """
        HU-004 - Caso verde (Azul/Refactor)
        Crear tarea con datos válidos
        """
        from src.model.modelo import Materia, Prioridad, EstadoTarea
        from src.model.declarative_base import session
        from datetime import date

        # 1. Preparación
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")
        
        # Creamos la materia directo en BD para no depender de métodos externos
        materia = Materia(nombre="Matemáticas", color="Rojo", usuario_id=usuario.idUsuario)
        session.add(materia)
        session.commit()
        session.refresh(materia)

        # 2. Acción
        tarea = self.tm.crear_tarea(
            titulo="Estudiar capítulo 1",
            descripcion="Repasar ejercicios",
            prioridad=Prioridad.Alta,
            fecha_entrega=date.today(),
            materia_id=materia.idMateria
        )
        
        # 3. Aserciones
        self.assertIsNotNone(tarea, "La tarea debe ser creada")
        self.assertEqual(tarea.titulo, "Estudiar capítulo 1")
        self.assertEqual(tarea.estado, EstadoTarea.Pendiente, "El estado por defecto debe ser Pendiente")
        self.assertEqual(tarea.prioridad, Prioridad.Alta)
        # self.assertEqual(tarea.progreso, 0.0) # Descomenta si usas el campo progreso

    def test_hu005_rojo_marcar_tarea_inexistente(self):
        """
        HU-005 - Escenario 1 (Rojo)
        No se debe permitir marcar como completada una tarea que no existe.
        """

        # Intentamos marcar una tarea con ID inexistente
        with self.assertRaises(ValueError) as context:
            self.tm.marcar_tarea(9999)  # ID que no existe

        # Verificamos que el mensaje mencione que la tarea no existe
        self.assertIn("tarea", str(context.exception).lower())

    def test_hu005_rojo_desmarcar_tarea_inexistente(self):
        """
        HU-005 - Escenario 2 (Rojo)
        No se debe permitir desmarcar una tarea que no existe.
        """

        with self.assertRaises(ValueError) as context:
            self.tm.desmarcar_tarea(9999)  # ID inexistente

        self.assertIn("tarea", str(context.exception).lower())

    def test_hu005_rojo_marcar_tarea_ya_completada(self):
        """
        HU-005 - Escenario 3 (Rojo)
        No se debe permitir marcar como completada una tarea que ya está completada.
        """

        from src.model.modelo import Materia, Prioridad, EstadoTarea
        from src.model.declarative_base import session
        from datetime import date

        # 1. Preparación: crear usuario y materia reales
        usuario = self.tm.crear_usuario("Lucía", "lucia@mail.com")

        materia = Materia(nombre="Historia", color="Verde", usuario_id=usuario.idUsuario)
        session.add(materia)
        session.commit()
        session.refresh(materia)

        # 2. Crear tarea válida
        tarea = self.tm.crear_tarea(
            titulo="Leer capítulo 5",
            descripcion="Resumen del libro",
            prioridad=Prioridad.Media,
            fecha_entrega=date.today(),
            materia_id=materia.idMateria
        )

        # 3. Marcarla como completada
        self.tm.marcar_tarea(tarea.idTarea)

        # 4. Intentar marcarla otra vez (debe fallar)
        with self.assertRaises(ValueError) as context:
            self.tm.marcar_tarea(tarea.idTarea)

        self.assertIn("completada", str(context.exception).lower())

    def test_hu006_rojo_editar_usuario_nombre_vacio(self):
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")
        with self.assertRaises(ValueError) as context:
            self.tm.editar_usuario(
                usuario.idUsuario, nuevo_nombre=""
            )
        self.assertIn("nombre", str(context.exception).lower())

    def test_hu006_rojo_editar_usuario_nombre_solo_espacios(self):
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")
        with self.assertRaises(ValueError) as context:
            self.tm.editar_usuario(
                usuario.idUsuario, nuevo_nombre="   "
            )
        self.assertIn("nombre", str(context.exception).lower())

    def test_hu006_rojo_editar_usuario_correo_duplicado(self):
        self.tm.crear_usuario("Juan", "juan@mail.com")
        usuario2 = self.tm.crear_usuario("Pedro", "pedro@mail.com")
        with self.assertRaises(ValueError) as context:
            self.tm.editar_usuario(
                usuario2.idUsuario,
                nuevo_correo="juan@mail.com"
            )
        self.assertIn("correo", str(context.exception).lower())
    
    def test_hu006_verde_editar_usuario_caso_feliz(self):
        usuario = self.tm.crear_usuario("Juan", "juan@mail.com")
        editado = self.tm.editar_usuario(
            usuario.idUsuario,
            nuevo_nombre="Juan Carlos",
            nuevo_correo="juancarlos@mail.com"
        )
        self.assertEqual(editado.nombre, "Juan Carlos")
        self.assertEqual(editado.correo, "juancarlos@mail.com")

    def test_hu007_escenario1_rojo_eliminar_usuario_inexistente(self):
        """
        HU-007 - Escenario 1: Intentar eliminar un usuario que no existe.
        Debe lanzar un ValueError.
        """
        # Intentamos eliminar un ID fantasma
        with self.assertRaises(ValueError) as context:
            self.tm.eliminar_usuario(999) 
        
        # Verificamos que el error nos avise que no existe
        self.assertIn("no existe", str(context.exception).lower())

    def test_hu007_escenario2_rojo_eliminar_usuario_existente(self):
        """
        HU-007 - Escenario 2: Eliminar un usuario que sí existe.
        El usuario debe desaparecer de la base de datos.
        """
        # 1. Preparación: Creamos un usuario válido con nombre y CORREO
        usuario_nuevo = self.tm.crear_usuario("Usuario a Eliminar", "eliminar@prueba.com")
        id_real = usuario_nuevo.idUsuario
        
        # 2. Acción: Lo eliminamos
        self.tm.eliminar_usuario(id_real)
        
        # 3. Aserción: Lo buscamos de nuevo. Debería darnos None.
        usuario_buscado = self.tm.seleccionar_usuario(id_real)
        self.assertIsNone(usuario_buscado, "El usuario aún existe en la BD, no fue eliminado")
        
    def test_hu007_escenario3_rojo_eliminar_usuario_id_invalido(self):
        """
        HU-007 - Escenario 3: Intentar eliminar un usuario enviando un ID 
        que no es un número (por ejemplo, un texto).
        Debe lanzar un TypeError o ValueError.
        """
        # Enviamos un texto en lugar de un ID numérico
        with self.assertRaises(TypeError) as context:
            self.tm.eliminar_usuario("ID_FALSO_ABC")
        
        # Verificamos que el error nos hable sobre el tipo de dato
        self.assertIn("debe ser un número", str(context.exception).lower())