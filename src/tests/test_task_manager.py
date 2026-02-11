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

    def test_hu004_desmarcar_tarea(self):
        """
        HU004 - Escenario alterno:
        Verifica que una tarea completada pueda volver a estado Pendiente.
        """

        # Arrange: crear perfil, materia y tarea
        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Física")

        tarea = self.tm.crear_tarea(
            titulo="Resolver ejercicios",
            descripcion="Guía 2",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Baja,
            fecha=None
        )

        # Marcar primero como completada
        self.tm.marcar_tarea_completada(tarea.idTarea)

        # Act: desmarcar la tarea (método aún no existe → ROJO)
        tarea_actualizada = self.tm.desmarcar_tarea(tarea.idTarea)

        # Assert: la tarea vuelve a Pendiente
        self.assertEqual(tarea_actualizada.estado.name, "Pendiente")
    
    def test_hu004_marcar_tarea_ya_completada(self):
        """
        HU004 - Escenario rojo:
        Verifica que no se pueda marcar como completada
        una tarea que ya está en estado Completada.
        """

        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Química")

        tarea = self.tm.crear_tarea(
            titulo="Leer apuntes",
            descripcion="Unidad 1",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Media,
            fecha=None
        )

        # Marcar una vez (esto es válido)
        self.tm.marcar_tarea_completada(tarea.idTarea)

        # Intentar marcar otra vez (debería fallar → ROJO)
        with self.assertRaises(ValueError):
            self.tm.marcar_tarea_completada(tarea.idTarea)

    def test_hu005_rojo_editar_titulo(self):
        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Historia")

        tarea = self.tm.crear_tarea(
            titulo="Titulo viejo",
            descripcion="Desc",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Media,
            fecha=None
        )

        tarea_editada = self.tm.editar_tarea(
            tarea_id=tarea.idTarea,
            nuevo_titulo="Titulo nuevo"
        )

        self.assertEqual(tarea_editada.titulo, "Titulo nuevo")

    def test_hu005_rojo_editar_descripcion(self):
        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Lengua")

        tarea = self.tm.crear_tarea(
            titulo="Leer",
            descripcion="Vieja",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Baja,
            fecha=None
        )

        tarea_editada = self.tm.editar_tarea(
            tarea_id=tarea.idTarea,
            nueva_descripcion="Nueva"
        )

        self.assertEqual(tarea_editada.descripcion, "Nueva")

    def test_hu005_rojo_mantener_campos_no_editados(self):

        perfil = self.tm.crear_perfil("Usuario Test")
        materia = self.tm.crear_materia(perfil.idPerfil, "Arte")

        tarea = self.tm.crear_tarea(
            titulo="Titulo original",
            descripcion="Descripcion original",
            materia_id=materia.idMateria,
            prioridad=Prioridad.Alta,
            fecha=None
        )

        # Editamos SOLO el título
        tarea_editada = self.tm.editar_tarea(
            tarea_id=tarea.idTarea,
            nuevo_titulo="Titulo nuevo"
        )

        # La descripción NO debería cambiar,
        self.assertEqual(tarea_editada.descripcion, "Descripcion original")

    def test_HU006_editar_materia_datos_validos(self):
        tm = TaskManager()

        # GIVEN: perfil y materia existente
        perfil = tm.crear_perfil("Kevin")
        materia = tm.crear_materia(
        perfil_id=perfil.idPerfil,
        nombre="Matemáticas",
        color="Azul"
    )

        # WHEN: se edita nombre y color
        materia_editada = tm.editar_materia(
        id_materia=materia.idMateria,
        nuevo_nombre="Álgebra",
        nuevo_color="Rojo"
    )

        # THEN: los cambios se reflejan
        self.assertEqual(materia_editada.nombre, "Álgebra")
        self.assertEqual(materia_editada.color, "Rojo")

    def test_HU006_editar_materia_nombre_vacio(self):
        tm = TaskManager()

        # GIVEN: un perfil y una materia existente
        perfil = tm.crear_perfil("Kevin")
        materia = tm.crear_materia(
            perfil_id=perfil.idPerfil,
            nombre="Matemáticas",
            color="Azul"
     )

        # WHEN / THEN: intentar editar con nombre vacío debe fallar
        with self.assertRaises(ValueError):
            tm.editar_materia(
                id_materia=materia.idMateria,
                nuevo_nombre="   ",
                nuevo_color="Rojo"
        )
    
    def test_hu006_editar_materia_nombre_solo_espacios(self):
        """
        HU006 - Escenario 3 ROJO:
        No se debe permitir editar con nombre que solo contenga espacios.
        """
        tm = TaskManager()
    
        # GIVEN: perfil y materia existente
        perfil = tm.crear_perfil("Kevin")
        materia = tm.crear_materia(
            perfil_id=perfil.idPerfil,
            nombre="Historia",
            color="Verde"
        )

        # WHEN/THEN: intentar editar con espacios debe fallar
        with self.assertRaises(ValueError):
            tm.editar_materia(
                id_materia=materia.idMateria,
                nuevo_nombre="   ",
                nuevo_color="Amarillo"
        )


