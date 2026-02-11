from src.modelo.declarative_base import Session
from src.modelo.modelo import EstadoTarea, Perfil, Materia, Tarea, Prioridad


class TaskManager:
    """
    Servicio de lógica de negocio para la gestión académica.

    Maneja operaciones CRUD sobre:
    - Perfiles
    - Materias
    - Tareas

    Esta clase actúa como capa intermedia entre la presentación
    (main.py) y la capa de persistencia (modelo).
    """

    def crear_perfil(self, nombre: str) -> Perfil:
        """
        Crea un nuevo perfil de usuario en la base de datos.

        Args:
            nombre (str): Nombre del perfil.

        Returns:
            Perfil: Objeto Perfil creado y persistido.

        Raises:
            ValueError: Si el nombre está vacío o contiene solo espacios.
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

        Args:
            id_perfil (int): Identificador del perfil.

        Returns:
            Perfil | None: Perfil encontrado o None si no existe.

        Raises:
            ValueError: Si el ID es inválido (<= 0).
        """
        if id_perfil <= 0:
            raise ValueError("ID de perfil inválido")

        session = Session()
        perfil = session.query(Perfil).filter_by(idPerfil=id_perfil).first()
        session.close()
        return perfil

    def seleccionar_perfil_por_nombre(self, nombre: str) -> Perfil | None:
        """
        Obtiene un perfil existente por su nombre.

        Args:
            nombre (str): Nombre del perfil.

        Returns:
            Perfil | None: Perfil encontrado o None si no existe.
        """
        session = Session()
        perfil = session.query(Perfil).filter_by(nombre=nombre).first()
        session.close()
        return perfil

    def crear_materia(self, perfil_id: int, nombre: str, color: str = "Azul") -> Materia:
        """
        Crea una nueva materia asociada a un perfil existente.

        Args:
            perfil_id (int): ID del perfil propietario.
            nombre (str): Nombre de la materia.
            color (str, optional): Color identificador. Default es "Azul".

        Returns:
            Materia: Materia creada y persistida.

        Raises:
            ValueError: Si el nombre es inválido o el perfil no existe.
        """

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
        """
        Lista todas las materias asociadas a un perfil.

        Args:
            perfil_id (int): ID del perfil.

        Returns:
            list[Materia]: Lista de materias con sus tareas cargadas.

        Raises:
            ValueError: Si el ID es inválido o el perfil no existe.
        """
        if perfil_id <= 0:
            raise ValueError("ID de perfil inválido")

        session = Session()

        try:
            perfil = session.query(Perfil).filter_by(
                idPerfil=perfil_id).first()

            if not perfil:
                raise ValueError("Perfil no existe")

            # Forzar carga completa
            materias = []
            for m in perfil.materias:
                _ = list(m.tareas)  # fuerza carga de tareas
                materias.append(m)

            return materias

        finally:
            session.close()

    def crear_tarea(self, titulo, descripcion, materia_id, prioridad, fecha):
        """
        Crea una tarea asociada a una materia existente.

        Args:
            titulo (str): Título de la tarea.
            descripcion (str): Descripción detallada.
            materia_id (int): ID de la materia asociada.
            prioridad (Prioridad): Nivel de prioridad de la tarea.
            fecha (date): Fecha de entrega.

        Returns:
            Tarea: Tarea creada y almacenada en la base de datos.

        Raises:
            ValueError: Si el título es inválido o la materia no existe.
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

        Args:
            session: Sesión activa de SQLAlchemy.
            tarea_id (int): ID de la tarea.

        Returns:
            Tarea: Tarea encontrada.

        Raises:
            ValueError: Si el ID es inválido o la tarea no existe.
        """

        if tarea_id <= 0:
            raise ValueError("ID de tarea inválido")

        tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()

        if not tarea:
            raise ValueError("Tarea no existe")

        return tarea

    def marcar_tarea_completada(self, tarea_id: int) -> Tarea:
        """
        Marca una tarea como completada.

        Args:
            tarea_id (int): ID de la tarea.

        Returns:
            Tarea: Tarea actualizada.

        Raises:
            ValueError: Si la tarea no existe o ya está completada.
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
        Cambia el estado de una tarea de Completada a Pendiente.

        Args:
            tarea_id (int): ID de la tarea.

        Returns:
            Tarea: Tarea actualizada.

        Raises:
            ValueError: Si la tarea no existe.
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
        Lista todas las tareas asociadas a una materia.

        Args:
            materia_id (int): ID de la materia.

        Returns:
            list[Tarea]: Lista de tareas asociadas.

        Raises:
            ValueError: Si el ID es inválido o la materia no existe.
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

        Solo se actualizan los campos proporcionados.

        Args:
            tarea_id (int): ID de la tarea.
            nuevo_titulo (str, optional): Nuevo título.
            nueva_descripcion (str, optional): Nueva descripción.

        Returns:
            Tarea: Tarea actualizada.

        Raises:
            ValueError: Si la tarea no existe o los datos son inválidos.
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
        """
        Actualiza el título de una tarea si se proporciona un valor válido.

        Args:
            tarea (Tarea): Objeto tarea a modificar.
            nuevo_titulo (str | None): Nuevo título.

        Raises:
            ValueError: Si el nuevo título es vacío.
        """
        if nuevo_titulo is None:
            return

        if not nuevo_titulo.strip():
            raise ValueError("El título no puede estar vacío")

        tarea.titulo = nuevo_titulo.strip()

    def _actualizar_descripcion(self, tarea, nueva_descripcion):
        """
        Actualiza la descripción de una tarea si se proporciona un valor válido.

        Args:
            tarea (Tarea): Objeto tarea a modificar.
            nueva_descripcion (str | None): Nueva descripción.

        Raises:
            ValueError: Si la descripción es vacía.
        """
        if nueva_descripcion is None:
            return

        if not nueva_descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")

        tarea.descripcion = nueva_descripcion.strip()

    def editar_materia(
        self,
        id_materia: int,
        nuevo_nombre: str = None,
        nuevo_color: str = None
    ) -> Materia:
        """
        Edita una materia existente.

        Solo se modifican los campos proporcionados.

        Args:
            id_materia (int): ID de la materia.
            nuevo_nombre (str, optional): Nuevo nombre.
            nuevo_color (str, optional): Nuevo color.

        Returns:
            Materia: Materia actualizada.

        Raises:
            ValueError: Si la materia no existe o el nombre es inválido.
        """
        session = Session()
        try:
            # Buscar materia
            materia = self._obtener_materia(session, id_materia)

            # Actualizar nombre si se proporciona
            if nuevo_nombre is not None:
                self._validar_nombre_materia(nuevo_nombre)
                materia.nombre = nuevo_nombre.strip()

        # Actualizar color si se proporciona
            if nuevo_color is not None:
                materia.color = nuevo_color

            session.commit()
            session.refresh(materia)
            return materia

        finally:
            session.close()

    def _obtener_materia(self, session, id_materia: int) -> Materia:
        """
        Obtiene una materia por ID validando su existencia.

        Args:
            session: Sesión activa de SQLAlchemy.
            id_materia (int): ID de la materia.

        Returns:
            Materia: Materia encontrada.

        Raises:
            ValueError: Si el ID es inválido o la materia no existe.
        """
        if id_materia <= 0:
            raise ValueError("ID de materia inválido")

        materia = session.query(Materia).filter_by(
            idMateria=id_materia).first()

        if not materia:
            raise ValueError("Materia no existe")

        return materia

    def _validar_nombre_materia(self, nombre: str):
        """
        Valida que el nombre de una materia no esté vacío.

        Args:
            nombre (str): Nombre a validar.

        Raises:
            ValueError: Si el nombre es vacío o solo contiene espacios.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la materia es obligatorio")
