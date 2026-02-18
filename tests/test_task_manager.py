from datetime import date, timedelta
import unittest
from src.logic.task_manager import TaskManager
from src.model.declarative_base import Base, engine
from src.model.modelo import Prioridad, EstadoTarea, Usuario, Materia, Tarea


# ══════════════════════════════════════════════════════════════════
# HELPERS COMPARTIDOS
# ══════════════════════════════════════════════════════════════════

def crear_usuario_helper(tm: TaskManager, nombre="Juan Lopez", correo="juan@mail.com") -> Usuario:
    return tm.crear_usuario(nombre, correo)


def seleccionar_usuario_helper(tm: TaskManager, usuario: Usuario) -> Usuario:
    return tm.seleccionar_usuario(usuario.idUsuario)


def crear_materia_helper(tm: TaskManager, nombre="Matemáticas", color="#FF5733") -> Materia:
    return tm.crear_materia(nombre, color)


def crear_tarea_helper(tm: TaskManager, materia_id: int, titulo="Estudiar capítulo uno") -> Tarea:
    return tm.crear_tarea(
        titulo=titulo,
        descripcion="Descripción de prueba",
        prioridad=Prioridad.Media,
        fecha_entrega=date.today(),
        materia_id=materia_id
    )


# ══════════════════════════════════════════════════════════════════
# HU-001: CREAR USUARIO
# ══════════════════════════════════════════════════════════════════

class TestHU001CrearUsuario(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_limite_cinco_usuarios(self):
        """No se deben crear más de 5 usuarios."""
        for i in range(5):
            self.tm.crear_usuario(f"Usuario{i}Nombre", f"user{i}@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Sexto Usuario", "sexto@mail.com")
        self.assertIn("límite", str(ctx.exception).lower())

    def test_rojo_nombre_vacio(self):
        """Nombre vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("", "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_solo_espacios(self):
        """Nombre con solo espacios debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("   ", "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_muy_corto(self):
        """Nombre con menos de 3 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Ab", "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_muy_largo(self):
        """Nombre con más de 50 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("A" * 51, "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_con_numeros(self):
        """Nombre con números debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan123", "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_con_caracteres_especiales(self):
        """Nombre con caracteres especiales debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan@#$", "test@mail.com")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_correo_vacio(self):
        """Correo vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_sin_arroba(self):
        """Correo sin @ debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "correosinmail.com")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_sin_dominio(self):
        """Correo con @ al final debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "correo@")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_duplicado(self):
        """Correo duplicado debe lanzar ValueError."""
        self.tm.crear_usuario("Juan Lopez", "test@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Pedro Garcia", "test@mail.com")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_duplicado_mayusculas(self):
        """Correo duplicado con mayúsculas distintas debe detectarse."""
        self.tm.crear_usuario("Juan Lopez", "test@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Pedro Garcia", "TEST@MAIL.COM")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_muy_largo(self):
        """Correo con más de 100 caracteres debe lanzar ValueError."""
        correo_largo = "a" * 90 + "@mail.com"
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", correo_largo)
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_termina_en_punto(self):
        """Correo que termina en punto debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "correo@mail.")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_multiples_arroba(self):
        """Correo con más de un @ debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "correo@@mail.com")
        self.assertIn("correo", str(ctx.exception).lower())

    def test_rojo_correo_con_espacios(self):
        """Correo con espacios internos debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_usuario("Juan Lopez", "co rreo@mail.com")
        self.assertIn("correo", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_crear_usuario_valido(self):
        """Crear usuario con datos válidos debe retornar el usuario creado."""
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nombre, "Juan Lopez")
        self.assertEqual(usuario.correo, "juan@mail.com")
        self.assertEqual(usuario.fecha_creacion, date.today())


# ══════════════════════════════════════════════════════════════════
# HU-002: SELECCIONAR USUARIO
# ══════════════════════════════════════════════════════════════════

class TestHU002SeleccionarUsuario(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_id_cero(self):
        """ID = 0 debe lanzar ValueError."""
        self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.seleccionar_usuario(0)
        self.assertIn("id", str(ctx.exception).lower())

    def test_rojo_id_negativo(self):
        """ID negativo debe lanzar ValueError."""
        self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.seleccionar_usuario(-5)
        self.assertIn("id", str(ctx.exception).lower())

    def test_rojo_id_inexistente_retorna_none(self):
        """ID que no existe debe retornar None."""
        self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        resultado = self.tm.seleccionar_usuario(999)
        self.assertIsNone(resultado)

    def test_rojo_sin_usuarios_en_bd(self):
        """Seleccionar cuando no hay usuarios debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.seleccionar_usuario(1)
        self.assertIn("no hay usuarios", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_seleccionar_usuario_existente(self):
        """Seleccionar usuario existente asigna usuario_activo."""
        creado = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        seleccionado = self.tm.seleccionar_usuario(creado.idUsuario)
        self.assertIsNotNone(seleccionado)
        self.assertEqual(seleccionado.nombre, "Juan Lopez")
        self.assertIsNotNone(self.tm.usuario_activo)
        self.assertEqual(self.tm.usuario_activo.idUsuario, creado.idUsuario)


# ══════════════════════════════════════════════════════════════════
# HU-003: CREAR MATERIA
# ══════════════════════════════════════════════════════════════════

class TestHU003CrearMateria(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Crear materia sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Matemáticas", "#FF5733")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_nombre_vacio(self):
        """Nombre vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("", "#FF5733")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_solo_espacios(self):
        """Nombre con solo espacios debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("   ", "#FF5733")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_muy_corto(self):
        """Nombre con menos de 3 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Ab", "#FF5733")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_duplicado_mismo_usuario(self):
        """Nombre duplicado para el mismo usuario debe lanzar ValueError."""
        self.tm.crear_materia("Matemáticas", "#FF5733")
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Matemáticas", "#00FF00")
        self.assertIn("materia", str(ctx.exception).lower())

    def test_rojo_color_sin_numeral(self):
        """Color sin # debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Matemáticas", "FF5733")
        self.assertIn("color", str(ctx.exception).lower())

    def test_rojo_color_formato_invalido(self):
        """Color con caracteres no HEX debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Matemáticas", "#ZZZZZZ")
        self.assertIn("color", str(ctx.exception).lower())

    def test_rojo_color_muy_corto(self):
        """Color con menos de 7 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_materia("Matemáticas", "#FFF")
        self.assertIn("color", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_crear_materia_valida(self):
        """Crear materia válida debe retornar la materia creada."""
        materia = self.tm.crear_materia("Matemáticas", "#FF5733")
        self.assertIsNotNone(materia)
        self.assertEqual(materia.nombre, "Matemáticas")
        self.assertEqual(materia.color, "#FF5733")

    def test_verde_nombre_duplicado_entre_usuarios_es_permitido(self):
        """El mismo nombre de materia puede existir para distintos usuarios."""
        usuario2 = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.crear_materia("Matemáticas", "#FF5733")

        self.tm.seleccionar_usuario(usuario2.idUsuario)
        materia2 = self.tm.crear_materia("Matemáticas", "#00FF00")
        self.assertIsNotNone(materia2)


# ══════════════════════════════════════════════════════════════════
# HU-004: CREAR TAREA
# ══════════════════════════════════════════════════════════════════

class TestHU004CrearTarea(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Crear tarea sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            crear_tarea_helper(self.tm, self.materia.idMateria)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_materia_inexistente(self):
        """Materia con ID inexistente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            crear_tarea_helper(self.tm, 9999)
        self.assertIn("materia", str(ctx.exception).lower())

    def test_hu004_rojo_materia_de_otro_usuario(self):
        """Tarea en materia de otro usuario debe lanzar ValueError."""
        # 1. Crear un segundo usuario y su materia
        usuario2 = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(usuario2.idUsuario)
        materia2 = self.tm.crear_materia("Física", "#0000FF")

        # 2. Restaurar al usuario original usando el nuevo método
        # (Asumiendo que "juan@mail.com" es el usuario creado en el setUp)
        usuario_original = self.tm.buscar_usuario_por_correo("juan@mail.com")
        self.tm.seleccionar_usuario(usuario_original.idUsuario)

        # 3. Acción y Aserción
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="Tarea Intruza",
                descripcion="...",
                materia_id=materia2.idMateria, # Esta materia NO es del usuario actual
                prioridad=Prioridad.Media,
                fecha_entrega=date.today()
            )
        
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_titulo_vacio(self):
        """Título vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="", descripcion="Desc",
                prioridad=Prioridad.Media,
                fecha_entrega=date.today(),
                materia_id=self.materia.idMateria
            )
        self.assertIn("título", str(ctx.exception).lower())

    def test_rojo_titulo_muy_corto(self):
        """Título con menos de 3 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="Ab", descripcion="Desc",
                prioridad=Prioridad.Media,
                fecha_entrega=date.today(),
                materia_id=self.materia.idMateria
            )
        self.assertIn("título", str(ctx.exception).lower())

    def test_rojo_descripcion_muy_larga(self):
        """Descripción con más de 500 caracteres debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="Título válido",
                descripcion="X" * 501,
                prioridad=Prioridad.Media,
                fecha_entrega=date.today(),
                materia_id=self.materia.idMateria
            )
        self.assertIn("descripción", str(ctx.exception).lower())

    def test_rojo_fecha_en_el_pasado(self):
        """Fecha en el pasado debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="Título válido",
                descripcion="Desc",
                prioridad=Prioridad.Media,
                fecha_entrega=date.today() - timedelta(days=1),
                materia_id=self.materia.idMateria
            )
        self.assertIn("fecha", str(ctx.exception).lower())

    def test_rojo_prioridad_invalida(self):
        """Prioridad que no es del enum debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.crear_tarea(
                titulo="Título válido",
                descripcion="Desc",
                prioridad="SuperUrgente",
                fecha_entrega=date.today(),
                materia_id=self.materia.idMateria
            )
        self.assertIn("prioridad", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_crear_tarea_valida(self):
        """Crear tarea válida debe tener estado Pendiente por defecto."""
        tarea = crear_tarea_helper(self.tm, self.materia.idMateria)
        self.assertIsNotNone(tarea)
        self.assertEqual(tarea.estado, EstadoTarea.Pendiente)
        self.assertEqual(tarea.prioridad, Prioridad.Media)


# ══════════════════════════════════════════════════════════════════
# HU-005: MARCAR / DESMARCAR TAREA
# ══════════════════════════════════════════════════════════════════

class TestHU005MarcarDesmarcar(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")
        self.tarea = crear_tarea_helper(self.tm, self.materia.idMateria)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_marcar_sin_usuario_activo(self):
        """Marcar tarea sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.marcar_tarea(self.tarea.idTarea)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_marcar_tarea_inexistente(self):
        """Marcar tarea con ID inexistente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.marcar_tarea(9999)
        self.assertIn("tarea", str(ctx.exception).lower())

    def test_rojo_marcar_tarea_otro_usuario(self):
        """Marcar tarea de otro usuario debe lanzar ValueError."""
        usuario2 = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(usuario2.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.marcar_tarea(self.tarea.idTarea)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_marcar_tarea_ya_completada(self):
        """Marcar tarea ya completada debe lanzar ValueError."""
        self.tm.marcar_tarea(self.tarea.idTarea)
        with self.assertRaises(ValueError) as ctx:
            self.tm.marcar_tarea(self.tarea.idTarea)
        self.assertIn("completada", str(ctx.exception).lower())

    def test_rojo_desmarcar_tarea_ya_pendiente(self):
        """Desmarcar tarea ya pendiente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.desmarcar_tarea(self.tarea.idTarea)
        self.assertIn("pendiente", str(ctx.exception).lower())

    # ── CASOS VERDES ──────────────────────────────────────────────

    def test_verde_marcar_tarea_pendiente(self):
        """Marcar tarea pendiente debe cambiar estado a Completada."""
        tarea = self.tm.marcar_tarea(self.tarea.idTarea)
        self.assertEqual(tarea.estado, EstadoTarea.Completada)

    def test_verde_desmarcar_tarea_completada(self):
        """Desmarcar tarea completada debe cambiar estado a Pendiente."""
        self.tm.marcar_tarea(self.tarea.idTarea)
        tarea = self.tm.desmarcar_tarea(self.tarea.idTarea)
        self.assertEqual(tarea.estado, EstadoTarea.Pendiente)


# ══════════════════════════════════════════════════════════════════
# HU-006: EDITAR USUARIO
# ══════════════════════════════════════════════════════════════════

class TestHU006EditarUsuario(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        self.usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(self.usuario.idUsuario)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Editar sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_usuario(self.usuario.idUsuario, nuevo_nombre="Nuevo Nombre")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_editar_otro_usuario(self):
        """Editar un usuario distinto al activo debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_usuario(otro.idUsuario, nuevo_nombre="Otro Nombre")
        self.assertIn("propio", str(ctx.exception).lower())

    def test_rojo_nombre_vacio(self):
        """Nombre vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_usuario(self.usuario.idUsuario, nuevo_nombre="")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_solo_espacios(self):
        """Nombre con solo espacios debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_usuario(self.usuario.idUsuario, nuevo_nombre="   ")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_correo_duplicado(self):
        """Correo ya registrado en otro usuario debe lanzar ValueError."""
        self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_usuario(self.usuario.idUsuario, nuevo_correo="pedro@mail.com")
        self.assertIn("correo", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_editar_usuario_correctamente(self):
        """Editar usuario válido debe actualizar los datos."""
        editado = self.tm.editar_usuario(
            self.usuario.idUsuario,
            nuevo_nombre="Juan Carlos Lopez",
            nuevo_correo="juancarlos@mail.com"
        )
        self.assertEqual(editado.nombre, "Juan Carlos Lopez")
        self.assertEqual(editado.correo, "juancarlos@mail.com")

    def test_verde_usuario_activo_se_actualiza_tras_edicion(self):
        """usuario_activo debe reflejar los nuevos datos tras editar."""
        self.tm.editar_usuario(
            self.usuario.idUsuario,
            nuevo_nombre="Juan Carlos Lopez"
        )
        self.assertEqual(self.tm.usuario_activo.nombre, "Juan Carlos Lopez")


# ══════════════════════════════════════════════════════════════════
# HU-007: ELIMINAR USUARIO
# ══════════════════════════════════════════════════════════════════

class TestHU007EliminarUsuario(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        self.usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(self.usuario.idUsuario)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Eliminar sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_usuario(self.usuario.idUsuario)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_eliminar_otro_usuario(self):
        """Eliminar un usuario distinto al activo debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_usuario(otro.idUsuario)
        self.assertIn("propio", str(ctx.exception).lower())

    def test_rojo_eliminar_usuario_con_materias(self):
        """Eliminar usuario con materias asociadas debe lanzar ValueError."""
        self.tm.crear_materia("Matemáticas", "#FF5733")
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_usuario(self.usuario.idUsuario)
        self.assertIn("materias", str(ctx.exception).lower())

    def test_rojo_eliminar_dos_veces(self):
        """Eliminar usuario ya eliminado debe lanzar ValueError."""
        self.tm.eliminar_usuario(self.usuario.idUsuario)

        # Crear otro usuario para poder operar
        nuevo = self.tm.crear_usuario("Ana Torres", "ana@mail.com")
        self.tm.seleccionar_usuario(nuevo.idUsuario)

        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_usuario(self.usuario.idUsuario)
        self.assertIn("propio", str(ctx.exception).lower())

    def test_rojo_id_tipo_invalido(self):
        """ID de tipo string debe lanzar TypeError."""
        with self.assertRaises(TypeError) as ctx:
            self.tm.eliminar_usuario("ID_FALSO")
        self.assertIn("número", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_eliminar_usuario_sin_dependencias(self):
        """Eliminar usuario sin materias debe retornar True."""
        resultado = self.tm.eliminar_usuario(self.usuario.idUsuario)
        self.assertTrue(resultado)

    def test_verde_usuario_activo_limpiado_tras_eliminar(self):
        """usuario_activo debe ser None después de eliminar."""
        self.tm.eliminar_usuario(self.usuario.idUsuario)
        self.assertIsNone(self.tm.usuario_activo)


# ══════════════════════════════════════════════════════════════════
# HU-008: EDITAR MATERIA
# ══════════════════════════════════════════════════════════════════

class TestHU008EditarMateria(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Editar sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(self.materia.idMateria, nuevo_nombre="Nuevo Nombre")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_materia_otro_usuario(self):
        """Editar materia de otro usuario debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(otro.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(self.materia.idMateria, nuevo_nombre="Hack")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_nombre_vacio(self):
        """Nombre vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(self.materia.idMateria, nuevo_nombre="")
        self.assertIn("nombre", str(ctx.exception).lower())

    def test_rojo_nombre_duplicado(self):
        """Nombre duplicado para el mismo usuario debe lanzar ValueError."""
        self.tm.crear_materia("Física", "#0000FF")
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(self.materia.idMateria, nuevo_nombre="Física")
        self.assertIn("materia", str(ctx.exception).lower())

    def test_rojo_color_invalido(self):
        """Color con formato inválido debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(self.materia.idMateria, nuevo_color="AZUL")
        self.assertIn("color", str(ctx.exception).lower())

    def test_rojo_materia_inexistente(self):
        """Editar materia inexistente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_materia(9999, nuevo_nombre="Cualquiera")
        self.assertIn("materia", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_editar_materia_correctamente(self):
        """Editar materia válida debe actualizar los datos."""
        editada = self.tm.editar_materia(
            self.materia.idMateria,
            nuevo_nombre="Álgebra Lineal",
            nuevo_color="#123456"
        )
        self.assertEqual(editada.nombre, "Álgebra Lineal")
        self.assertEqual(editada.color, "#123456")


# ══════════════════════════════════════════════════════════════════
# HU-009: EDITAR TAREA
# ══════════════════════════════════════════════════════════════════

class TestHU009EditarTarea(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        self.usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(self.usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")
        self.tarea = crear_tarea_helper(self.tm, self.materia.idMateria)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Editar sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nuevo_titulo="Nuevo Título")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_tarea_otro_usuario(self):
        """Editar tarea de otro usuario debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(otro.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nuevo_titulo="Hack Título")
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_titulo_vacio(self):
        """Título vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nuevo_titulo="")
        self.assertIn("título", str(ctx.exception).lower())

    def test_rojo_titulo_solo_espacios(self):
        """Título con solo espacios debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nuevo_titulo="   ")
        self.assertIn("título", str(ctx.exception).lower())

    def test_rojo_fecha_en_el_pasado(self):
        """Fecha en el pasado debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(
                self.tarea.idTarea,
                nueva_fecha_entrega=date.today() - timedelta(days=1)
            )
        self.assertIn("fecha", str(ctx.exception).lower())

    def test_rojo_prioridad_invalida(self):
        """Prioridad inválida debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nueva_prioridad="SuperUrgente")
        self.assertIn("prioridad", str(ctx.exception).lower())

    def test_rojo_cambiar_a_materia_otro_usuario(self):
        """Mover tarea a materia de otro usuario debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(otro.idUsuario)
        materia_otro = self.tm.crear_materia("Física", "#0000FF")

        # Restaurar usuario original
        self.tm.seleccionar_usuario(self.usuario.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.editar_tarea(self.tarea.idTarea, nueva_materia_id=materia_otro.idMateria)
        self.assertIn("usuario", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_editar_tarea_correctamente(self):
        """Editar tarea válida debe actualizar los datos."""
        editada = self.tm.editar_tarea(
            self.tarea.idTarea,
            nuevo_titulo="Título actualizado",
            nueva_descripcion="Descripción actualizada",
            nueva_prioridad=Prioridad.Alta
        )
        self.assertEqual(editada.titulo, "Título actualizado")
        self.assertEqual(editada.descripcion, "Descripción actualizada")
        self.assertEqual(editada.prioridad, Prioridad.Alta)

    def test_verde_estado_no_cambia_al_editar(self):
        """El estado de la tarea no debe cambiar al editar otros campos."""
        self.tm.marcar_tarea(self.tarea.idTarea)
        editada = self.tm.editar_tarea(self.tarea.idTarea, nuevo_titulo="Nuevo Título")
        self.assertEqual(editada.estado, EstadoTarea.Completada)


# ══════════════════════════════════════════════════════════════════
# HU-010: ELIMINAR MATERIA
# ══════════════════════════════════════════════════════════════════

class TestHU010EliminarMateria(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Eliminar materia sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_materia(self.materia.idMateria)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_materia_otro_usuario(self):
        """Eliminar materia de otro usuario debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(otro.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_materia(self.materia.idMateria)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_eliminar_dos_veces(self):
        """Eliminar materia ya eliminada debe lanzar ValueError."""
        self.tm.eliminar_materia(self.materia.idMateria)
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_materia(self.materia.idMateria)
        self.assertIn("materia", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_eliminar_materia_con_cascade(self):
        """Eliminar materia debe eliminar sus tareas en cascada."""
        tarea = crear_tarea_helper(self.tm, self.materia.idMateria)
        id_tarea = tarea.idTarea

        self.tm.eliminar_materia(self.materia.idMateria)

        materia_buscada = self.tm.seleccionar_materia(self.materia.idMateria)
        tarea_buscada = self.tm.seleccionar_tarea(id_tarea)

        self.assertIsNone(materia_buscada, "La materia debería haberse eliminado")
        self.assertIsNone(tarea_buscada, "La tarea debería haberse eliminado en cascada")


# ══════════════════════════════════════════════════════════════════
# HU-011: ELIMINAR TAREA
# ══════════════════════════════════════════════════════════════════

class TestHU011EliminarTarea(unittest.TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.tm = TaskManager()
        usuario = self.tm.crear_usuario("Juan Lopez", "juan@mail.com")
        self.tm.seleccionar_usuario(usuario.idUsuario)
        self.materia = self.tm.crear_materia("Matemáticas", "#FF5733")
        self.tarea = crear_tarea_helper(self.tm, self.materia.idMateria)

    # ── CASOS ROJOS ───────────────────────────────────────────────

    def test_rojo_sin_usuario_activo(self):
        """Eliminar tarea sin usuario activo debe lanzar ValueError."""
        self.tm.usuario_activo = None
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_tarea(self.tarea.idTarea)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_tarea_otro_usuario(self):
        """Eliminar tarea de otro usuario debe lanzar ValueError."""
        otro = self.tm.crear_usuario("Pedro Garcia", "pedro@mail.com")
        self.tm.seleccionar_usuario(otro.idUsuario)
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_tarea(self.tarea.idTarea)
        self.assertIn("usuario", str(ctx.exception).lower())

    def test_rojo_eliminar_dos_veces(self):
        """Eliminar tarea ya eliminada debe lanzar ValueError."""
        self.tm.eliminar_tarea(self.tarea.idTarea)
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_tarea(self.tarea.idTarea)
        self.assertIn("tarea", str(ctx.exception).lower())

    def test_rojo_id_tipo_invalido(self):
        """ID de tipo string debe lanzar TypeError."""
        with self.assertRaises(TypeError) as ctx:
            self.tm.eliminar_tarea("ID_INVALIDO")
        self.assertIn("número", str(ctx.exception).lower())

    def test_rojo_tarea_inexistente(self):
        """ID inexistente debe lanzar ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tm.eliminar_tarea(9999)
        self.assertIn("tarea", str(ctx.exception).lower())

    # ── CASO VERDE ────────────────────────────────────────────────

    def test_verde_eliminar_tarea_correctamente(self):
        """Eliminar tarea válida debe retornar True y no existir en BD."""
        id_tarea = self.tarea.idTarea
        resultado = self.tm.eliminar_tarea(id_tarea)
        self.assertTrue(resultado)
        self.assertIsNone(self.tm.seleccionar_tarea(id_tarea))


if __name__ == "__main__":
    unittest.main()