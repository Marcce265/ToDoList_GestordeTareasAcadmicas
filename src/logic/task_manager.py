"""
task_manager.py
===============
Módulo de lógica de negocio para el proyecto TaskMaster Student.

Este módulo contiene la clase TaskManager, que centraliza todas las
operaciones del sistema: gestión de usuarios, materias y tareas académicas.
Implementa las Historias de Usuario HU-001 a HU-011.

Dependencias:
    - SQLAlchemy ORM (sesiones y consultas a SQLite)
    - src.model.declarative_base (engine)
    - src.model.modelo (Usuario, Materia, Tarea, Prioridad, EstadoTarea)

Uso típico:
    from src.logic.task_manager import TaskManager

    tm = TaskManager()
    usuario = tm.crear_usuario("Ana Torres", "ana@mail.com")
    tm.seleccionar_usuario(usuario.idUsuario)
    materia = tm.crear_materia("Cálculo I", "#3B82F6")
    tarea   = tm.crear_tarea("Parcial 1", "", Prioridad.Alta,
                              date(2026, 3, 15), materia.idMateria)
"""

import re
from datetime import date
from typing import Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.model.declarative_base import engine
from src.model.modelo import Usuario, Materia, Tarea, Prioridad, EstadoTarea

# Fábrica de sesiones ligada al engine configurado en declarative_base
Session = sessionmaker(bind=engine)


class TaskManager:
    """
    Controlador principal de la lógica de negocio de TaskMaster Student.

    Gestiona las operaciones CRUD sobre usuarios, materias y tareas,
    aplicando validaciones de negocio antes de interactuar con la base
    de datos. Mantiene en memoria el usuario actualmente seleccionado.

    Atributos:
        usuario_activo (Optional[Usuario]):
            Usuario que tiene la sesión activa. Es None si no se ha
            seleccionado ningún usuario. La mayoría de operaciones sobre
            materias y tareas requieren que este atributo esté definido.

    Ejemplo de flujo básico:
        tm = TaskManager()
        u = tm.crear_usuario("Juan Lopez", "juan@mail.com")
        tm.seleccionar_usuario(u.idUsuario)
        m = tm.crear_materia("Matemáticas", "#FF5733")
        t = tm.crear_tarea("Tarea 1", "", Prioridad.Media,
                            date.today(), m.idMateria)
        tm.marcar_tarea(t.idTarea)
    """

    def __init__(self):
        """Inicializa el TaskManager sin usuario activo."""
        self.usuario_activo: Optional[Usuario] = None

    # ──────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ──────────────────────────────────────────────────────────────

    def _validar_usuario_activo(self):
        """
        Verifica que haya un usuario activo seleccionado.

        Raises:
            ValueError: Si usuario_activo es None.
        """
        if self.usuario_activo is None:
            raise ValueError("Debe seleccionar un usuario primero")

    @staticmethod
    def _validar_nombre_usuario(nombre: str) -> str:
        """
        Valida y normaliza el nombre de un usuario.

        Aplica las siguientes reglas:
            - No puede estar vacío ni contener solo espacios.
            - Mínimo 3 caracteres, máximo 50.
            - Solo letras (incluyendo acentos y ñ) y espacios.
            - No se permiten números ni caracteres especiales.

        Args:
            nombre (str): Nombre a validar.

        Returns:
            str: Nombre con espacios extremos eliminados (strip).

        Raises:
            ValueError: Si el nombre no cumple alguna de las reglas.
        """
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")
        if len(nombre) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        if len(nombre) > 50:
            raise ValueError("El nombre es muy largo (máximo 50 caracteres)")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValueError(
                "El nombre solo puede contener letras y espacios, "
                "sin números ni caracteres especiales"
            )
        return nombre

    @staticmethod
    def _validar_correo(correo: str) -> str:
        """
        Valida y normaliza un correo electrónico.

        Aplica las siguientes reglas:
            - No puede estar vacío.
            - Máximo 100 caracteres.
            - No puede contener espacios.
            - Debe tener exactamente un símbolo @.
            - No puede iniciar con @ ni terminar en punto.
            - Debe cumplir el patrón: usuario@dominio.tld

        Args:
            correo (str): Correo a validar.

        Returns:
            str: Correo en minúsculas y sin espacios extremos.

        Raises:
            ValueError: Si el correo no cumple alguna de las reglas.
        """
        correo = correo.strip().lower()
        if not correo:
            raise ValueError("El correo no puede estar vacío")
        if len(correo) > 100:
            raise ValueError("El correo es muy largo (máximo 100 caracteres)")
        if ' ' in correo:
            raise ValueError("El correo no puede contener espacios")
        if correo.count('@') != 1:
            raise ValueError("El correo debe contener exactamente un @")
        if correo.startswith('@'):
            raise ValueError("El correo no puede iniciar con @")
        if correo.endswith('.'):
            raise ValueError("El correo no puede terminar en punto")
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValueError("El correo tiene un formato inválido")
        return correo

    @staticmethod
    def _validar_nombre_materia(nombre: str) -> str:
        """
        Valida y normaliza el nombre de una materia.

        Reglas:
            - No puede estar vacío ni contener solo espacios.
            - Mínimo 3 caracteres, máximo 50.

        Args:
            nombre (str): Nombre de la materia a validar.

        Returns:
            str: Nombre con espacios extremos eliminados.

        Raises:
            ValueError: Si el nombre no cumple alguna de las reglas.
        """
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la materia no puede estar vacío")
        if len(nombre) < 3:
            raise ValueError(
                "El nombre de la materia debe tener al menos 3 caracteres")
        if len(nombre) > 50:
            raise ValueError(
                "El nombre de la materia es muy largo (máximo 50 caracteres)")
        return nombre

    @staticmethod
    def _validar_color_hex(color: str):
        """
        Valida que un color esté en formato HEX (#RRGGBB).

        Args:
            color (str): Cadena de color a validar.

        Raises:
            ValueError: Si el color no tiene el formato #RRGGBB exacto
                        (1 numeral + 6 dígitos hexadecimales).
        """
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("El color debe ser formato HEX (#RRGGBB)")

    @staticmethod
    def _validar_titulo_tarea(titulo: str) -> str:
        """
        Valida y normaliza el título de una tarea.

        Reglas:
            - No puede estar vacío ni contener solo espacios.
            - Mínimo 3 caracteres, máximo 100.

        Args:
            titulo (str): Título de la tarea a validar.

        Returns:
            str: Título con espacios extremos eliminados.

        Raises:
            ValueError: Si el título no cumple alguna de las reglas.
        """
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El título de la tarea no puede estar vacío")
        if len(titulo) < 3:
            raise ValueError(
                "El título de la tarea debe tener al menos 3 caracteres")
        if len(titulo) > 100:
            raise ValueError(
                "El título de la tarea es muy largo (máximo 100 caracteres)")
        return titulo

    # ──────────────────────────────────────────────────────────────
    # HU-001: Crear Usuario
    # ──────────────────────────────────────────────────────────────

    def crear_usuario(self, nombre: str, correo: str) -> Usuario:
        """
        HU-001: Crea y persiste un nuevo usuario en el sistema.

        Valida los datos de entrada, verifica que no se supere el límite
        de 5 usuarios y que el correo no esté duplicado, y guarda el
        usuario en la base de datos.

        Args:
            nombre (str): Nombre completo del usuario.
            correo (str): Correo electrónico único del usuario.

        Returns:
            Usuario: Objeto Usuario recién creado y desvinculado de la sesión.

        Raises:
            ValueError: Si:
                - El nombre es inválido (vacío, muy corto/largo, con números).
                - El correo es inválido (formato incorrecto, vacío, muy largo).
                - Ya existen 5 usuarios registrados.
                - El correo ya está registrado por otro usuario.
        """
        nombre = self._validar_nombre_usuario(nombre)
        correo = self._validar_correo(correo)

        session = Session()
        try:
            # Verificar límite máximo de usuarios
            count = session.query(Usuario).count()
            if count >= 5:
                raise ValueError("Límite de usuarios alcanzado (máximo 5)")

            # Verificar unicidad del correo
            existente = session.query(Usuario).filter_by(correo=correo).first()
            if existente:
                raise ValueError(f"El correo '{correo}' ya está registrado")

            usuario = Usuario(
                nombre=nombre,
                correo=correo,
                fecha_creacion=date.today()
            )
            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            session.expunge(usuario)
            return usuario

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "El correo ya está registrado (error de concurrencia)")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-002: Seleccionar Usuario
    # ──────────────────────────────────────────────────────────────

    def listar_usuarios(self) -> list:
        """
        HU-002 (auxiliar): Retorna todos los usuarios registrados en el sistema.

        Returns:
            list[Usuario]: Lista de objetos Usuario. Puede estar vacía si
                           no hay usuarios registrados.
        """
        session = Session()
        try:
            usuarios = session.query(Usuario).all()
            for u in usuarios:
                session.expunge(u)
            return usuarios
        finally:
            session.close()

    def seleccionar_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """
        HU-002: Selecciona un usuario por ID y lo establece como usuario activo.

        Si el ID existe, el usuario queda asignado a self.usuario_activo para
        que las operaciones posteriores (materias, tareas) puedan verificar
        la identidad del usuario en sesión.

        Args:
            id_usuario (int): ID del usuario a seleccionar.

        Returns:
            Optional[Usuario]: El usuario encontrado, o None si el ID no existe.

        Raises:
            ValueError: Si no hay usuarios registrados en el sistema,
                        o si id_usuario es <= 0.
        """
        session = Session()
        try:
            count = session.query(Usuario).count()
            if count == 0:
                raise ValueError("No hay usuarios registrados")

            if id_usuario <= 0:
                raise ValueError("El ID del usuario debe ser mayor a 0")

            usuario = session.query(Usuario).filter_by(
                idUsuario=id_usuario).first()
            if usuario:
                session.expunge(usuario)
                self.usuario_activo = usuario
            return usuario
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-003: Crear Materia
    # ──────────────────────────────────────────────────────────────

    def crear_materia(self, nombre: str, color: str) -> Materia:
        """
        HU-003: Crea y persiste una materia para el usuario activo.

        El nombre debe ser único dentro de las materias del mismo usuario.
        El color debe estar en formato HEX (#RRGGBB).

        Args:
            nombre (str): Nombre de la materia (mín. 3, máx. 50 caracteres).
            color  (str): Color identificador en formato #RRGGBB.

        Returns:
            Materia: Objeto Materia recién creada y desvinculado de la sesión.

        Raises:
            ValueError: Si:
                - No hay usuario activo.
                - El nombre es inválido (vacío, muy corto/largo).
                - El color no tiene formato HEX válido.
                - Ya existe una materia con el mismo nombre para este usuario.
        """
        self._validar_usuario_activo()
        nombre = self._validar_nombre_materia(nombre)
        self._validar_color_hex(color)

        session = Session()
        try:
            # Verificar que el nombre no esté duplicado para este usuario
            duplicado = session.query(Materia).filter_by(
                nombre=nombre,
                usuario_id=self.usuario_activo.idUsuario
            ).first()
            if duplicado:
                raise ValueError(
                    f"Ya existe una materia llamada '{nombre}' para este usuario")

            materia = Materia(
                nombre=nombre,
                color=color,
                usuario_id=self.usuario_activo.idUsuario
            )
            session.add(materia)
            session.commit()
            session.refresh(materia)
            session.expunge(materia)
            return materia

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "Ya existe una materia con ese nombre para este usuario")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-004: Crear Tarea
    # ──────────────────────────────────────────────────────────────

    def crear_tarea(
        self,
        titulo: str,
        descripcion: str,
        prioridad: Prioridad,
        fecha_entrega: date,
        materia_id: int
    ) -> Tarea:
        """
        HU-004: Crea y persiste una tarea asociada a una materia del usuario activo.

        La tarea se crea con estado inicial EstadoTarea.Pendiente.
        La materia debe existir y pertenecer al usuario activo.

        Args:
            titulo        (str):      Título de la tarea (mín. 3, máx. 100 caracteres).
            descripcion   (str):      Descripción opcional (máx. 500 caracteres).
            prioridad     (Prioridad): Nivel de prioridad (debe ser instancia de Prioridad).
            fecha_entrega (date):     Fecha límite (no puede ser anterior a hoy).
            materia_id    (int):      ID de la materia a la que pertenece la tarea.

        Returns:
            Tarea: Objeto Tarea recién creada, con estado Pendiente.

        Raises:
            ValueError: Si:
                - No hay usuario activo.
                - El título es inválido.
                - La descripción supera 500 caracteres.
                - La fecha de entrega es pasada o no es un objeto date.
                - La prioridad no es una instancia del enum Prioridad.
                - La materia no existe o pertenece a otro usuario.
        """
        self._validar_usuario_activo()
        titulo = self._validar_titulo_tarea(titulo)

        if descripcion and len(descripcion) > 500:
            raise ValueError(
                "La descripción es muy larga (máximo 500 caracteres)")

        if not isinstance(fecha_entrega, date):
            raise ValueError("La fecha de entrega es inválida")
        if fecha_entrega < date.today():
            raise ValueError("La fecha de entrega no puede ser en el pasado")

        if not isinstance(prioridad, Prioridad):
            raise ValueError(
                "La prioridad debe ser una instancia de Prioridad (Baja, Media o Alta)")

        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=materia_id).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError(
                    "No puede crear una tarea en una materia de otro usuario")

            tarea = Tarea(
                titulo=titulo,
                descripcion=descripcion,
                materia_id=materia_id,
                prioridad=prioridad,
                fechaEntrega=fecha_entrega,
                estado=EstadoTarea.Pendiente
            )
            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            session.expunge(tarea)
            return tarea

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def buscar_usuario_por_correo(self, correo):
        """
        Busca un usuario por su dirección de correo electrónico.

        Método auxiliar utilizado principalmente en los tests para recuperar
        un usuario específico sin depender del ID.

        Args:
            correo (str): Correo electrónico del usuario a buscar.

        Returns:
            Optional[Usuario]: El usuario encontrado, o None si no existe.
        """
        from src.model.declarative_base import Session
        from src.model.modelo import Usuario

        session = Session()
        usuario = session.query(Usuario).filter_by(correo=correo).first()
        session.close()
        return usuario

    # ──────────────────────────────────────────────────────────────
    # HU-005: Marcar / Desmarcar Tarea
    # ──────────────────────────────────────────────────────────────

    def _cambiar_estado_tarea(self, tarea_id: int, nuevo_estado: EstadoTarea) -> Tarea:
        """
        Método interno que cambia el estado de una tarea.

        Verifica que haya usuario activo, que la tarea exista, que pertenezca
        al usuario activo y que el nuevo estado sea diferente al actual.

        Args:
            tarea_id     (int):         ID de la tarea a modificar.
            nuevo_estado (EstadoTarea): Nuevo estado a asignar.

        Returns:
            Tarea: Tarea actualizada y desvinculada de la sesión.

        Raises:
            ValueError: Si no hay usuario activo, la tarea no existe,
                        pertenece a otro usuario, o ya tiene el estado indicado.
        """
        self._validar_usuario_activo()

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()
            if not tarea:
                raise ValueError("La tarea no existe")

            materia = session.query(Materia).filter_by(
                idMateria=tarea.materia_id).first()
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError(
                    "No puede modificar una tarea de otro usuario")

            if tarea.estado == nuevo_estado:
                if nuevo_estado == EstadoTarea.Completada:
                    raise ValueError("La tarea ya está completada")
                else:
                    raise ValueError("La tarea ya está pendiente")

            tarea.estado = nuevo_estado
            session.commit()
            session.refresh(tarea)
            session.expunge(tarea)
            return tarea

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def marcar_tarea(self, tarea_id: int) -> Tarea:
        """
        HU-005: Marca una tarea como Completada.

        Args:
            tarea_id (int): ID de la tarea a marcar.

        Returns:
            Tarea: Tarea con estado EstadoTarea.Completada.

        Raises:
            ValueError: Si la tarea ya estaba completada, no existe,
                        no hay usuario activo, o pertenece a otro usuario.
        """
        return self._cambiar_estado_tarea(tarea_id, EstadoTarea.Completada)

    def desmarcar_tarea(self, tarea_id: int) -> Tarea:
        """
        HU-005: Desmarca una tarea, volviendo su estado a Pendiente.

        Args:
            tarea_id (int): ID de la tarea a desmarcar.

        Returns:
            Tarea: Tarea con estado EstadoTarea.Pendiente.

        Raises:
            ValueError: Si la tarea ya estaba pendiente, no existe,
                        no hay usuario activo, o pertenece a otro usuario.
        """
        return self._cambiar_estado_tarea(tarea_id, EstadoTarea.Pendiente)

    # ──────────────────────────────────────────────────────────────
    # HU-006: Editar Usuario
    # ──────────────────────────────────────────────────────────────

    def editar_usuario(
        self,
        id_usuario: int,
        nuevo_nombre: Optional[str] = None,
        nuevo_correo: Optional[str] = None
    ) -> Usuario:
        """
        HU-006: Edita los datos del usuario activo.

        Un usuario solo puede editar su propio perfil. Se pueden modificar
        el nombre, el correo o ambos en una sola llamada.

        Args:
            id_usuario    (int):           ID del usuario a editar (debe ser el activo).
            nuevo_nombre  (Optional[str]): Nuevo nombre. Si es None, no se modifica.
            nuevo_correo  (Optional[str]): Nuevo correo. Si es None, no se modifica.

        Returns:
            Usuario: Objeto Usuario actualizado. También actualiza usuario_activo.

        Raises:
            ValueError: Si:
                - No hay usuario activo.
                - Se intenta editar un usuario distinto al activo.
                - El nuevo nombre es inválido.
                - El nuevo correo es inválido o ya está registrado.
        """
        self._validar_usuario_activo()

        if id_usuario != self.usuario_activo.idUsuario:
            raise ValueError("Solo puede editar su propio usuario")

        if nuevo_nombre is not None:
            nuevo_nombre = self._validar_nombre_usuario(nuevo_nombre)
        if nuevo_correo is not None:
            nuevo_correo = self._validar_correo(nuevo_correo)

        session = Session()
        try:
            usuario = session.query(Usuario).filter_by(
                idUsuario=id_usuario).first()
            if not usuario:
                raise ValueError("El usuario no existe")

            if nuevo_nombre is not None:
                usuario.nombre = nuevo_nombre

            if nuevo_correo is not None:
                # Verificar que el nuevo correo no esté registrado en otro usuario
                existente = session.query(Usuario).filter(
                    Usuario.correo == nuevo_correo,
                    Usuario.idUsuario != id_usuario
                ).first()
                if existente:
                    raise ValueError(
                        f"El correo '{nuevo_correo}' ya está registrado")
                usuario.correo = nuevo_correo

            session.commit()
            session.refresh(usuario)
            session.expunge(usuario)
            # Actualizar referencia en memoria
            self.usuario_activo = usuario
            return usuario

        except IntegrityError:
            session.rollback()
            raise ValueError("El correo ya está registrado")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-007: Eliminar Usuario
    # ──────────────────────────────────────────────────────────────

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """
        HU-007: Elimina el usuario activo del sistema.

        Solo se puede eliminar el propio usuario activo. Para poder eliminarlo,
        el usuario no debe tener materias asociadas (debe limpiarlas primero).
        Tras eliminar, self.usuario_activo queda en None.

        Args:
            id_usuario (int): ID del usuario a eliminar (debe ser el activo).

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            TypeError:  Si id_usuario no es un entero.
            ValueError: Si:
                - No hay usuario activo.
                - Se intenta eliminar un usuario distinto al activo.
                - El usuario tiene materias asociadas.
                - El usuario no existe en la base de datos.
        """
        if not isinstance(id_usuario, int):
            raise TypeError("El ID debe ser un número entero")

        self._validar_usuario_activo()

        if id_usuario != self.usuario_activo.idUsuario:
            raise ValueError("Solo puede eliminar su propio usuario")

        session = Session()
        try:
            usuario = session.query(Usuario).filter_by(
                idUsuario=id_usuario).first()
            if not usuario:
                raise ValueError(f"El usuario con ID {id_usuario} no existe")

            # Verificar que no tenga materias antes de eliminar
            if usuario.materias:
                raise ValueError(
                    "Debe eliminar primero todas las materias del usuario")

            session.delete(usuario)
            session.commit()
            self.usuario_activo = None  # Limpiar sesión activa
            return True

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-008: Editar Materia
    # ──────────────────────────────────────────────────────────────

    def editar_materia(
        self,
        id_materia: int,
        nuevo_nombre: Optional[str] = None,
        nuevo_color: Optional[str] = None
    ) -> Materia:
        """
        HU-008: Edita una materia del usuario activo.

        Se pueden modificar el nombre, el color o ambos. La materia debe
        pertenecer al usuario activo.

        Args:
            id_materia   (int):           ID de la materia a editar.
            nuevo_nombre (Optional[str]): Nuevo nombre. Si es None, no se modifica.
            nuevo_color  (Optional[str]): Nuevo color HEX. Si es None, no se modifica.

        Returns:
            Materia: Objeto Materia actualizado.

        Raises:
            ValueError: Si:
                - No hay usuario activo.
                - La materia no existe o pertenece a otro usuario.
                - El nuevo nombre es inválido o está duplicado para este usuario.
                - El nuevo color no tiene formato HEX válido.
        """
        self._validar_usuario_activo()

        if nuevo_nombre is not None:
            nuevo_nombre = self._validar_nombre_materia(nuevo_nombre)
        if nuevo_color is not None:
            self._validar_color_hex(nuevo_color)

        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=id_materia).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede editar una materia de otro usuario")

            if nuevo_nombre is not None:
                # Verificar que el nuevo nombre no esté duplicado para este usuario
                duplicado = session.query(Materia).filter(
                    Materia.nombre == nuevo_nombre,
                    Materia.usuario_id == self.usuario_activo.idUsuario,
                    Materia.idMateria != id_materia
                ).first()
                if duplicado:
                    raise ValueError(
                        f"Ya existe una materia llamada '{nuevo_nombre}' para este usuario")
                materia.nombre = nuevo_nombre

            if nuevo_color is not None:
                materia.color = nuevo_color

            session.commit()
            session.refresh(materia)
            session.expunge(materia)
            return materia

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-009: Editar Tarea
    # ──────────────────────────────────────────────────────────────

    def editar_tarea(
        self,
        id_tarea: int,
        nuevo_titulo: Optional[str] = None,
        nueva_descripcion: Optional[str] = None,
        nueva_prioridad: Optional[Prioridad] = None,
        nueva_fecha_entrega: Optional[date] = None,
        nueva_materia_id: Optional[int] = None
    ) -> Tarea:
        """
        HU-009: Edita una tarea del usuario activo.

        Permite modificar uno o varios campos de la tarea. La tarea debe
        pertenecer al usuario activo. Si se cambia la materia, la nueva
        materia también debe pertenecer al usuario activo.

        Args:
            id_tarea            (int):              ID de la tarea a editar.
            nuevo_titulo        (Optional[str]):    Nuevo título. None = sin cambio.
            nueva_descripcion   (Optional[str]):    Nueva descripción. None = sin cambio.
            nueva_prioridad     (Optional[Prioridad]): Nueva prioridad. None = sin cambio.
            nueva_fecha_entrega (Optional[date]):   Nueva fecha (no pasada). None = sin cambio.
            nueva_materia_id    (Optional[int]):    ID de nueva materia. None = sin cambio.

        Returns:
            Tarea: Objeto Tarea actualizado. El estado no se modifica.

        Raises:
            ValueError: Si:
                - No hay usuario activo.
                - La tarea no existe o pertenece a otro usuario.
                - El nuevo título es inválido.
                - La nueva descripción supera 500 caracteres.
                - La nueva fecha es pasada o inválida.
                - La nueva prioridad no es instancia de Prioridad.
                - La nueva materia no existe o pertenece a otro usuario.
        """
        self._validar_usuario_activo()

        if nuevo_titulo is not None:
            nuevo_titulo = self._validar_titulo_tarea(nuevo_titulo)

        if nueva_descripcion is not None and len(nueva_descripcion) > 500:
            raise ValueError(
                "La descripción es muy larga (máximo 500 caracteres)")

        if nueva_fecha_entrega is not None:
            if not isinstance(nueva_fecha_entrega, date):
                raise ValueError("La fecha de entrega es inválida")
            if nueva_fecha_entrega < date.today():
                raise ValueError(
                    "La fecha de entrega no puede ser en el pasado")

        if nueva_prioridad is not None and not isinstance(nueva_prioridad, Prioridad):
            raise ValueError(
                "La prioridad debe ser una instancia de Prioridad (Baja, Media o Alta)")

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=id_tarea).first()
            if not tarea:
                raise ValueError("La tarea no existe")

            materia_actual = session.query(Materia).filter_by(
                idMateria=tarea.materia_id).first()
            if materia_actual.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede editar una tarea de otro usuario")

            if nueva_materia_id is not None:
                nueva_materia = session.query(Materia).filter_by(
                    idMateria=nueva_materia_id).first()
                if not nueva_materia:
                    raise ValueError("La nueva materia no existe")
                if nueva_materia.usuario_id != self.usuario_activo.idUsuario:
                    raise ValueError(
                        "No puede mover una tarea a una materia de otro usuario")
                tarea.materia_id = nueva_materia_id

            if nuevo_titulo is not None:
                tarea.titulo = nuevo_titulo
            if nueva_descripcion is not None:
                tarea.descripcion = nueva_descripcion
            if nueva_prioridad is not None:
                tarea.prioridad = nueva_prioridad
            if nueva_fecha_entrega is not None:
                tarea.fechaEntrega = nueva_fecha_entrega

            session.commit()
            session.refresh(tarea)
            session.expunge(tarea)
            return tarea

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-010: Eliminar Materia
    # ──────────────────────────────────────────────────────────────

    def seleccionar_materia(self, materia_id: int) -> Optional[Materia]:
        """
        HU-010 (auxiliar): Retorna una materia por su ID.

        Método de consulta simple sin restricciones de usuario activo.
        Utilizado principalmente para verificar existencia tras eliminaciones.

        Args:
            materia_id (int): ID de la materia a buscar.

        Returns:
            Optional[Materia]: La materia encontrada, o None si no existe.
        """
        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=materia_id).first()
            if materia:
                session.expunge(materia)
            return materia
        finally:
            session.close()

    def eliminar_materia(self, materia_id: int) -> bool:
        """
        HU-010: Elimina una materia del usuario activo y sus tareas en cascada.

        La materia debe pertenecer al usuario activo. Al eliminarse,
        todas las tareas asociadas se eliminan automáticamente por el
        cascade configurado en el modelo.

        Args:
            materia_id (int): ID de la materia a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            ValueError: Si no hay usuario activo, la materia no existe
                        o pertenece a otro usuario.
        """
        self._validar_usuario_activo()

        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=materia_id).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError(
                    "No puede eliminar una materia de otro usuario")

            # cascade="all, delete-orphan" elimina las tareas automáticamente
            session.delete(materia)
            session.commit()
            return True

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-011: Eliminar Tarea
    # ──────────────────────────────────────────────────────────────

    def seleccionar_tarea(self, tarea_id: int) -> Optional[Tarea]:
        """
        HU-011 (auxiliar): Retorna una tarea por su ID.

        Método de consulta simple sin restricciones de usuario activo.
        Utilizado principalmente para verificar existencia tras eliminaciones.

        Args:
            tarea_id (int): ID de la tarea a buscar.

        Returns:
            Optional[Tarea]: La tarea encontrada, o None si no existe.
        """
        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()
            if tarea:
                session.expunge(tarea)
            return tarea
        finally:
            session.close()

    def eliminar_tarea(self, id_tarea: int) -> bool:
        """
        HU-011: Elimina una tarea del usuario activo.

        La tarea debe pertenecer a una materia del usuario activo.

        Args:
            id_tarea (int): ID de la tarea a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            TypeError:  Si id_tarea no es un entero.
            ValueError: Si:
                - No hay usuario activo.
                - La tarea no existe.
                - La tarea pertenece a otro usuario.
        """
        if not isinstance(id_tarea, int):
            raise TypeError("El ID de la tarea debe ser un número entero")

        self._validar_usuario_activo()

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=id_tarea).first()
            if not tarea:
                raise ValueError(f"La tarea con id {id_tarea} no existe")

            materia = session.query(Materia).filter_by(
                idMateria=tarea.materia_id).first()
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede eliminar una tarea de otro usuario")

            session.delete(tarea)
            session.commit()
            return True

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
