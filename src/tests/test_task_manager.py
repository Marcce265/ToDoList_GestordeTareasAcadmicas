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

    def test_hu001_verde_crear_perfil(self):
        perfil = self.tm.crear_perfil("Ernesto")
        self.assertIsNotNone(perfil)
    
    def test_hu001_seleccionar_perfil_id_invalido(self):
        with self.assertRaises(ValueError):
            self.tm.seleccionar_perfil(0)


    

