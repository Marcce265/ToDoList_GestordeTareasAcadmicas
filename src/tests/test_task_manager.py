import unittest
from src.logica.task_manager import TaskManager
from src.modelo.declarative_base import Base, engine


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        Base.metadata.create_all(engine)
        self.tm = TaskManager()

    def tearDown(self):
        Base.metadata.drop_all(engine)

    def test_hu001_rojo_sin_perfiles(self):
        perfil = self.tm.seleccionar_perfil(1)
        self.assertIsNone(perfil)
