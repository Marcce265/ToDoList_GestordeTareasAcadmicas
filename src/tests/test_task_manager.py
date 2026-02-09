from datetime import date
import unittest
from src.logica.task_manager import TaskManager
from src.modelo.declarative_base import Base, Session, engine
from src.modelo.modelo import Materia, Prioridad


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
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

    def test_hu003_crear_tarea_valida(self):
        session = Session()

        materia = Materia(nombre="Matemática", color="Azul", perfil_id=1)
        session.add(materia)
        session.commit()
        session.refresh(materia)
        session.close()

        tarea = self.tm.crear_tarea(
            titulo="Estudiar para el examen",
            descripcion="Capítulos 1 al 3",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Alta,
            fecha=date(2026, 2, 20)
        )

        self.assertEqual(tarea.titulo, "Estudiar para el examen")

    def test_hu003_crear_tarea_titulo_vacio(self):
        with self.assertRaises(ValueError):
            self.tm.crear_tarea(
                titulo="",
                descripcion="Algo",
                materia_id=1,
                prioridad=Prioridad.Media,
                fecha=None
            )

    def test_hu003_crear_tarea_materia_inexistente(self):
        with self.assertRaises(ValueError):
            self.tm.crear_tarea(
                titulo="Hacer tarea",
                descripcion="",
                materia_id=999,
                prioridad=Prioridad.Baja,
                fecha=None
            )

    def test_hu004_marcar_tarea_completada(self):
        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Matemática")

        tarea = self.tm.crear_tarea(
            titulo="Estudiar",
            descripcion="Parcial",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Media,
            fecha=None
        )

        tarea_actualizada = self.tm.marcar_tarea_completada(tarea.idTarea)

        self.assertEqual(tarea_actualizada.estado.name, "Completada")
