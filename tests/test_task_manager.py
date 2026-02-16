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