from datetime import date
from typing import Optional
from sqlalchemy.orm import sessionmaker
from src.model.declarative_base import engine
from src.model.modelo import Usuario, Materia, Tarea, Prioridad

Session = sessionmaker(bind=engine)


class TaskManager:

    def crear_usuario(self, nombre: str, correo: str) -> Usuario:
        """
        HU-001: Crea un nuevo usuario.

        Args:
            nombre: Nombre del usuario (obligatorio)
            correo: Correo del usuario (obligatorio y único)

        Returns:
            Usuario creado y persistido

        Raises:
            ValueError: Si nombre o correo están vacíos, o correo duplicado
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")

        if not correo or not correo.strip():
            raise ValueError("El correo no puede estar vacío")

        session = Session()
        try:
            # Validar correo único
            usuario_existente = session.query(Usuario).filter_by(
                correo=correo.strip()
            ).first()

            if usuario_existente:
                raise ValueError(f"El correo {correo} ya está registrado")

            usuario = Usuario(
                nombre=nombre.strip(),
                correo=correo.strip(),
                fecha_creacion=date.today()
            )

            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            return usuario
        finally:
            session.close()

    def seleccionar_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """
        HU-002: Selecciona un usuario por ID.

        Args:
            id_usuario: ID del usuario a buscar

        Returns:
            Usuario encontrado o None si no existe

        Raises:
            ValueError: Si el ID es inválido (≤ 0)
        """
        if id_usuario <= 0:
            raise ValueError("El ID del usuario debe ser mayor a 0")

        # 2. ABRIR CONEXIÓN
        # Creamos una 'session' para poder hablar con la base de datos.
        session = Session()
        try:
            # 3. CONSULTA (QUERY)
            # Le decimos a la base de datos:
            # - query(Usuario): "Busca en la tabla de Usuarios..."
            # - filter_by(...): "...donde la columna idUsuario sea igual al id que me pasaron..."
            # - first(): "...y dame el primer resultado (o None si no encuentra nada)."
            usuario = session.query(Usuario).filter_by(
                idUsuario=id_usuario
            ).first()

            # 4. RETORNO
            # Devolvemos el objeto usuario encontrado (o None) a quien llamó la función.
            return usuario

        finally:
            # 5. CIERRE (CLEANUP)
            # Este bloque 'finally' se ejecuta SIEMPRE, haya error o no.
            # Cerramos la sesión para liberar memoria y no dejar conexiones colgadas.
            session.close()

    def crear_materia(self, usuario_id: int, nombre: str, color: str) -> Materia:
        """
        HU-003: Crea una materia asociada a un usuario.

        Args:
            usuario_id (int): ID del usuario propietario de la materia.
            nombre (str): Nombre de la materia.
            color (str): Color identificador de la materia.

        Returns:
            Materia: Objeto Materia creado y persistido en la base de datos.

        Raises:
            ValueError: Si el usuario no existe o si el nombre/color son inválidos.
        """

        session = Session()
        try:
            usuario = session.query(Usuario).filter_by(
                idUsuario=usuario_id
            ).first()

            if not usuario:
                raise ValueError("El usuario no existe")

            if not nombre or not nombre.strip():
                raise ValueError(
                    "El nombre de la materia no puede estar vacío")
            if not color or not color.strip():
                raise ValueError("El color de la materia no puede estar vacío")

            materia = Materia(
                nombre=nombre.strip(),
                color=color.strip(),
                usuario_id=usuario_id
            )

            session.add(materia)
            session.commit()
            session.refresh(materia)
            return materia

        finally:
            session.close()

    def crear_tarea(self, titulo: str, descripcion: str, prioridad: Prioridad, fecha_entrega: date, materia_id: int) -> Tarea:
        """
        HU-004: Crea una nueva tarea asociada a una materia.
        """
        # Validación Escenario 1: Título vacío
        if not titulo or not titulo.strip():
            raise ValueError("El título de la tarea no puede estar vacío")
            
        # =========================================================
         # ESCENARIO 3 (VERDE) <---
        # =========================================================
        if not isinstance(prioridad, Prioridad):
            raise ValueError("La prioridad asignada no es válida. Use Prioridad.Baja, Prioridad.Media o Prioridad.Alta.")
            
        session = Session()
        try:
            # Validación Escenario 2: Verificar que la materia exista
            materia_existente = session.query(Materia).filter_by(idMateria=materia_id).first()
            if not materia_existente:
                raise ValueError(f"La materia con ID {materia_id} no existe. No se puede crear la tarea.")

            # Si pasa todas las validaciones, creamos la tarea
            tarea = Tarea(
                titulo=titulo.strip(),
                descripcion=descripcion.strip() if descripcion else "",
                prioridad=prioridad,
                fechaEntrega=fecha_entrega,
                materia_id=materia_id
            )
            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            return tarea
        finally:
            session.close()
