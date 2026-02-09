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

  # Verifica que se pueda crear una materia válida asociada a un perfil existente
    def test_hu002_escenario1_crear_materia_valida(self):
        
        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Matemáticas")

        self.assertIsNotNone(materia)
        self.assertEqual(materia.nombre, "Matemáticas")

    # Verifica que no se permita crear una materia con nombre vacío
    def test_hu002_escenario2_nombre_obligatorio(self):
        perfil = self.tm.crear_perfil("Usuario Test")

        with self.assertRaises(ValueError):
            self.tm.crear_materia(perfil.idPerfil, "")
            
    # Verifica que se puedan listar las materias asociadas a un perfil
    def test_hu002_listar_materias_por_perfil(self):
        
        perfil = self.tm.crear_perfil("Usuario Test")
        self.tm.crear_materia(perfil.idPerfil, "Matemáticas")
        self.tm.crear_materia(perfil.idPerfil, "Física")

        materias = self.tm.listar_materias_por_perfil(perfil.idPerfil)

        self.assertEqual(len(materias), 2)    

