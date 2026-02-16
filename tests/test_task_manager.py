from datetime import date
import unittest
from src.logic.task_manager import TaskManager
from src.model.declarative_base import Base, engine
from src.model.modelo import Usuario # Importamos para aserciones

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
