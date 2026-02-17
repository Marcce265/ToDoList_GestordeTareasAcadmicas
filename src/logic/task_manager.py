from datetime import date
from typing import Optional
from sqlalchemy.orm import sessionmaker
from src.model.declarative_base import engine
from src.model.modelo import Usuario, Materia, Tarea, Prioridad, EstadoTarea

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

    def crear_tarea(
        self,
        titulo: str,
        descripcion: str,
        prioridad: Prioridad,
        fecha_entrega: date,
        materia_id: int
    ) -> Tarea:
        """
        HU-004: Crea una tarea asociada a una materia.
        """
        # Validaciones (Fail Fast)
        if not titulo or not titulo.strip():
            raise ValueError("El título de la tarea no puede estar vacío")
        
        if not isinstance(prioridad, Prioridad):
            raise ValueError("La prioridad debe ser Baja, Media o Alta")
        
        session = Session()
        try:
            materia = session.query(Materia).filter_by(idMateria=materia_id).first()
            if not materia:
                raise ValueError("La materia no existe")
            
            tarea = Tarea(
                titulo=titulo.strip(),
                descripcion=descripcion,
                materia_id=materia_id,
                prioridad=prioridad,
                fechaEntrega=fecha_entrega,
                estado=EstadoTarea.Pendiente # <--- Excelente añadido por defecto
                # progreso=0.0,              # <-- Descomenta solo si existe en modelo.py
                # fecha_creacion=date.today() # <-- Descomenta solo si existe en modelo.py
            )
            
            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            return tarea
        finally:
            session.close()

    def _cambiar_estado_tarea(self, tarea_id: int, nuevo_estado: EstadoTarea) -> Tarea:
        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()

            if not tarea:
                raise ValueError("La tarea no existe")

            if tarea.estado == nuevo_estado:
                if nuevo_estado == EstadoTarea.Completada:
                    raise ValueError("La tarea ya está completada")
                else:
                    raise ValueError("La tarea ya está pendiente")

            tarea.estado = nuevo_estado

            session.commit()
            session.refresh(tarea)

            return tarea

        finally:
            session.close()


    def marcar_tarea(self, tarea_id: int) -> Tarea:
        return self._cambiar_estado_tarea(tarea_id, EstadoTarea.Completada)


    def desmarcar_tarea(self, tarea_id: int) -> Tarea:
        return self._cambiar_estado_tarea(tarea_id, EstadoTarea.Pendiente)
    
    def editar_usuario(
        self,
        id_usuario: int,
        nuevo_nombre: Optional[str] = None,
        nuevo_correo: Optional[str] = None
    ) -> Usuario:
        """
        HU-006: Edita un usuario existente.

        Args:
            id_usuario: ID del usuario a editar
            nuevo_nombre: Nuevo nombre (opcional)
            nuevo_correo: Nuevo correo (opcional)

        Returns:
            Usuario actualizado

        Raises:
            ValueError: Si nombre vacío o correo duplicado
        """
        session = Session()
        try:
            usuario = session.query(Usuario).filter_by(
                idUsuario=id_usuario
            ).first()

            if nuevo_nombre is not None:
                if not nuevo_nombre.strip():
                    raise ValueError(
                        "El nombre no puede estar vacío"
                    )
                usuario.nombre = nuevo_nombre.strip()

            if nuevo_correo is not None:
                existente = session.query(Usuario).filter(
                    Usuario.correo == nuevo_correo.strip(),
                    Usuario.idUsuario != id_usuario
                ).first()
                if existente:
                    raise ValueError(
                        f"El correo {nuevo_correo} "
                        "ya está registrado"
                    )
                usuario.correo = nuevo_correo.strip()

            session.commit()
            session.refresh(usuario)
            return usuario
        finally:
            session.close()

    def eliminar_usuario(self, id_usuario: int):
        """
        Elimina un usuario del sistema por su ID. (Versión Final Completa)
        """
        # Validación de tipo (Escenario 3)
        if not isinstance(id_usuario, int):
            raise TypeError("El ID del usuario debe ser un número entero.")

        session = Session() 
        try:
            # Búsqueda del usuario (Escenario 1)
            usuario_a_eliminar = session.query(Usuario).filter_by(idUsuario=id_usuario).first()

            if not usuario_a_eliminar:
                raise ValueError(f"El usuario con ID {id_usuario} no existe.")
            
            # Eliminación física (Escenario 2)
            session.delete(usuario_a_eliminar)
            session.commit()
                
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def editar_materia(
        self,
        id_materia: int,
        nuevo_nombre: Optional[str] = None,
        nuevo_color: Optional[str] = None
    ) -> Materia:
        """
        HU-008: Edita una materia existente.
        """

        # ✅ Refactor 1: Validación de tipo
        if not isinstance(id_materia, int):
            raise TypeError("El ID de la materia debe ser un número entero.")

        session = Session()
        try:
            materia = session.query(Materia).filter_by(
                idMateria=id_materia
            ).first()

            # ✅ Validación materia inexistente
            if not materia:
                raise ValueError("La materia no existe")

            # ✅ Refactor 2: Validación limpia reutilizable
            if nuevo_nombre is not None:
                nombre_limpio = nuevo_nombre.strip()
                if not nombre_limpio:
                    raise ValueError("El nombre no puede estar vacío")
                materia.nombre = nombre_limpio

            if nuevo_color is not None:
                color_limpio = nuevo_color.strip()
                if not color_limpio:
                    raise ValueError("El color no puede estar vacío")
                materia.color = color_limpio

            session.commit()
            session.refresh(materia)
            return materia

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()
            
    def editar_tarea(
        self,
        id_tarea: int,
        nuevo_titulo: Optional[str] = None,
        nueva_descripcion: Optional[str] = None,
        nueva_prioridad: Optional[Prioridad] = None
    ) -> Tarea:
        """
        HU-009: Edita una tarea existente.

        Args:
            id_tarea: ID de la tarea a editar
            nuevo_titulo: Nuevo título (opcional)
            nueva_descripcion: Nueva descripción (opcional)
            nueva_prioridad: Nueva prioridad (opcional)

        Returns:
            Tarea actualizada

        Raises:
            ValueError: Si título vacío o prioridad inválida
        """
        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(
                idTarea=id_tarea
            ).first()

            if nuevo_titulo is not None:
                if not nuevo_titulo.strip():
                    raise ValueError(
                        "El título no puede estar vacío"
                    )
                tarea.titulo = nuevo_titulo.strip()

            if nueva_descripcion is not None:
                tarea.descripcion = nueva_descripcion.strip()

            if nueva_prioridad is not None:
                if not isinstance(nueva_prioridad, Prioridad):
                    raise ValueError(
                        "La prioridad debe ser Baja, Media o Alta"
                    )
                tarea.prioridad = nueva_prioridad

            session.commit()
            session.refresh(tarea)
            return tarea
        finally:
            session.close()