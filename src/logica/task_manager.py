from src.modelo.declarative_base import Session
from src.modelo.modelo import EstadoTarea, Perfil, Materia, Tarea, Prioridad


class TaskManager:
    """
    Clase que contiene la lógica de negocio para la gestión de perfiles,
    materias y tareas.
    """

    def crear_perfil(self, nombre: str) -> Perfil:
        """
        Crea un nuevo perfil de usuario.

        :param nombre: Nombre del perfil
        :return: Perfil creado
        :raises ValueError: si el nombre es vacío
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del perfil no puede estar vacío")

        session = Session()
        perfil = Perfil(nombre=nombre.strip())
        session.add(perfil)
        session.commit()
        session.refresh(perfil)
        session.close()
        return perfil

    def seleccionar_perfil(self, id_perfil: int) -> Perfil | None:
        """
        Obtiene un perfil existente por su ID.

        :param id_perfil: ID del perfil
        :return: Perfil encontrado o None
        :raises ValueError: si el ID es inválido
        """
        if id_perfil <= 0:
            raise ValueError("ID de perfil inválido")

        session = Session()
        perfil = session.query(Perfil).filter_by(idPerfil=id_perfil).first()
        session.close()
        return perfil

    def seleccionar_perfil_por_nombre(self, nombre: str) -> Perfil | None:
        session = Session()
        perfil = session.query(Perfil).filter_by(nombre=nombre).first()
        session.close()
        return perfil

    def crear_materia(self, perfil_id: int, nombre: str, color: str = "Azul") -> Materia:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la materia es obligatorio")

        session = Session()

        perfil = session.query(Perfil).filter_by(idPerfil=perfil_id).first()
        if not perfil:
            session.close()
            raise ValueError("Perfil no existe")

        materia = Materia(
            nombre=nombre.strip(),
            color=color,
            perfil=perfil
        )

        session.add(materia)
        session.commit()
        session.refresh(materia)
        session.close()

        return materia

    def listar_materias_por_perfil(self, perfil_id: int):
        if perfil_id <= 0:
            raise ValueError("ID de perfil inválido")

        session = Session()

        perfil = session.query(Perfil).filter_by(idPerfil=perfil_id).first()
        if not perfil:
            session.close()
            raise ValueError("Perfil no existe")

        materias = perfil.materias
        session.close()

        return materias

    def crear_tarea(self, titulo, descripcion, materia_id, prioridad, fecha):
        """
        Crea una tarea asociada a una materia existente.
        """

        # 1️⃣ Validación de negocio
        if not titulo or not titulo.strip():
            raise ValueError("El título de la tarea es obligatorio")

        session = Session()
        try:
            # 2️⃣ Validar existencia de materia
            materia = session.query(Materia).filter_by(
                idMateria=materia_id).first()
            if not materia:
                raise ValueError("Materia no existe")

            # 3️⃣ Crear tarea
            tarea = Tarea(
                titulo=titulo.strip(),
                descripcion=descripcion,
                materia_id=materia_id,
                prioridad=prioridad,
                fechaEntrega=fecha,
                estado=EstadoTarea.Pendiente
            )

            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            return tarea

        finally:
            session.close()

    def _obtener_tarea(self, session, tarea_id: int) -> Tarea:
        """
        Obtiene una tarea por ID validando su existencia.
        """

        if tarea_id <= 0:
            raise ValueError("ID de tarea inválido")

        tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()

        if not tarea:
            raise ValueError("Tarea no existe")

        return tarea

    def marcar_tarea_completada(self, tarea_id: int) -> Tarea:
        """
        Marca una tarea existente como completada.
        """

        session = Session()
        try:
            tarea = self._obtener_tarea(session, tarea_id)

            if tarea.estado == EstadoTarea.Completada:
                raise ValueError("La tarea ya está completada")

            tarea.estado = EstadoTarea.Completada

            session.commit()
            session.refresh(tarea)
            return tarea

        finally:
            session.close()

    def desmarcar_tarea(self, tarea_id: int):
        """
        Devuelve una tarea completada al estado Pendiente.
        """

        session = Session()
        try:
            tarea = self._obtener_tarea(session, tarea_id)

            tarea.estado = EstadoTarea.Pendiente

            session.commit()
            session.refresh(tarea)
            return tarea

        finally:
            session.close()

    def listar_tareas_por_materia(self, materia_id: int):
        """
        Devuelve todas las tareas asociadas a una materia.
        """

        if materia_id <= 0:
            raise ValueError("ID de materia inválido")

        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=materia_id).first()

            if not materia:
                raise ValueError("Materia no existe")

            # Forzamos la carga de las tareas DENTRO de la sesión
            tareas = list(materia.tareas)

            return tareas

        finally:
            session.close()

    def editar_tarea(self, tarea_id: int, nuevo_titulo=None, nueva_descripcion=None):
        """
        Edita una tarea existente.
        Solo se modifican los campos proporcionados.
        """

        session = Session()
        try:
            tarea = self._obtener_tarea(session, tarea_id)

            self._actualizar_titulo(tarea, nuevo_titulo)
            self._actualizar_descripcion(tarea, nueva_descripcion)

            session.commit()
            session.refresh(tarea)
            return tarea

        finally:
            session.close()

    def _actualizar_titulo(self, tarea, nuevo_titulo):
        if nuevo_titulo is None:
            return

        if not nuevo_titulo.strip():
            raise ValueError("El título no puede estar vacío")

        tarea.titulo = nuevo_titulo.strip()

    def _actualizar_descripcion(self, tarea, nueva_descripcion):
        if nueva_descripcion is None:
            tarea.descripcion = "Descripcion cambiada"
            return

        if not nueva_descripcion.strip():
            return

        tarea.descripcion = nueva_descripcion.strip()

    def editar_materia(self, id_materia: int, nuevo_nombre: str, nuevo_color: str):
        session = Session()
        try:
            materia = session.query(Materia).filter_by(
            idMateria=id_materia
            ).first()

            if not materia:
                raise ValueError("Materia no existe")

            materia.nombre = nuevo_nombre
            materia.color = nuevo_color

            session.commit()
            session.refresh(materia)
            return materia

        finally:
            session.close()

    def editar_materia(self, id_materia: int, nuevo_nombre: str, nuevo_color: str):
        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=id_materia
            ).first()

            if not materia:
                raise ValueError("Materia no existe")

            #  VALIDACIÓN  (HU-006 Escenario 2)
            if not nuevo_nombre or not nuevo_nombre.strip():
                raise ValueError("El nombre de la materia es obligatorio")

            materia.nombre = nuevo_nombre.strip()
            materia.color = nuevo_color

            session.commit()
            session.refresh(materia)
            return materia

        finally:
            session.close()

    


           
