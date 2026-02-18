import re
from datetime import date
from typing import Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.model.declarative_base import engine
from src.model.modelo import Usuario, Materia, Tarea, Prioridad, EstadoTarea

Session = sessionmaker(bind=engine)


class TaskManager:

    def __init__(self):
        self.usuario_activo: Optional[Usuario] = None

    # ──────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ──────────────────────────────────────────────────────────────

    def _validar_usuario_activo(self):
        if self.usuario_activo is None:
            raise ValueError("Debe seleccionar un usuario primero")

    @staticmethod
    def _validar_nombre_usuario(nombre: str) -> str:
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
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la materia no puede estar vacío")
        if len(nombre) < 3:
            raise ValueError("El nombre de la materia debe tener al menos 3 caracteres")
        if len(nombre) > 50:
            raise ValueError("El nombre de la materia es muy largo (máximo 50 caracteres)")
        return nombre

    @staticmethod
    def _validar_color_hex(color: str):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("El color debe ser formato HEX (#RRGGBB)")

    @staticmethod
    def _validar_titulo_tarea(titulo: str) -> str:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El título de la tarea no puede estar vacío")
        if len(titulo) < 3:
            raise ValueError("El título de la tarea debe tener al menos 3 caracteres")
        if len(titulo) > 100:
            raise ValueError("El título de la tarea es muy largo (máximo 100 caracteres)")
        return titulo

    # ──────────────────────────────────────────────────────────────
    # HU-001: Crear Usuario
    # ──────────────────────────────────────────────────────────────

    def crear_usuario(self, nombre: str, correo: str) -> Usuario:
        """
        Crea un nuevo usuario con validaciones completas.

        Raises:
            ValueError: Si el límite de 5 usuarios se alcanzó, nombre/correo
                        inválidos, o correo duplicado.
        """
        nombre = self._validar_nombre_usuario(nombre)
        correo = self._validar_correo(correo)

        session = Session()
        try:
            count = session.query(Usuario).count()
            if count >= 5:
                raise ValueError("Límite de usuarios alcanzado (máximo 5)")

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
            raise ValueError("El correo ya está registrado (error de concurrencia)")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ──────────────────────────────────────────────────────────────
    # HU-002: Seleccionar Usuario
    # ──────────────────────────────────────────────────────────────

    def listar_usuarios(self) -> list:
        """Retorna todos los usuarios registrados."""
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
        Selecciona un usuario por ID y lo asigna como usuario activo.

        Raises:
            ValueError: Si no hay usuarios registrados o el ID es <= 0.
        Returns:
            Usuario encontrado, o None si el ID no existe.
        """
        session = Session()
        try:
            count = session.query(Usuario).count()
            if count == 0:
                raise ValueError("No hay usuarios registrados")

            if id_usuario <= 0:
                raise ValueError("El ID del usuario debe ser mayor a 0")

            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
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
        Crea una materia para el usuario activo.

        Raises:
            ValueError: Si no hay usuario activo, nombre/color inválidos,
                        o nombre duplicado para el mismo usuario.
        """
        self._validar_usuario_activo()
        nombre = self._validar_nombre_materia(nombre)
        self._validar_color_hex(color)

        session = Session()
        try:
            duplicado = session.query(Materia).filter_by(
                nombre=nombre,
                usuario_id=self.usuario_activo.idUsuario
            ).first()
            if duplicado:
                raise ValueError(f"Ya existe una materia llamada '{nombre}' para este usuario")

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
            raise ValueError("Ya existe una materia con ese nombre para este usuario")
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
        Crea una tarea asociada a una materia del usuario activo.

        Raises:
            ValueError: Si no hay usuario activo, materia inválida/ajena,
                        título/descripción/fecha/prioridad inválidos.
        """
        self._validar_usuario_activo()
        titulo = self._validar_titulo_tarea(titulo)

        if descripcion and len(descripcion) > 500:
            raise ValueError("La descripción es muy larga (máximo 500 caracteres)")

        if not isinstance(fecha_entrega, date):
            raise ValueError("La fecha de entrega es inválida")
        if fecha_entrega < date.today():
            raise ValueError("La fecha de entrega no puede ser en el pasado")

        if not isinstance(prioridad, Prioridad):
            raise ValueError("La prioridad debe ser una instancia de Prioridad (Baja, Media o Alta)")

        session = Session()
        try:
            materia = session.query(Materia).filter_by(idMateria=materia_id).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede crear una tarea en una materia de otro usuario")

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
        """Busca un usuario por su correo electrónico."""
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
        self._validar_usuario_activo()

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=tarea_id).first()
            if not tarea:
                raise ValueError("La tarea no existe")

            materia = session.query(Materia).filter_by(idMateria=tarea.materia_id).first()
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede modificar una tarea de otro usuario")

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
        return self._cambiar_estado_tarea(tarea_id, EstadoTarea.Completada)

    def desmarcar_tarea(self, tarea_id: int) -> Tarea:
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
        Edita el usuario activo. Solo puede editar su propio usuario.

        Raises:
            ValueError: Si no hay usuario activo, intenta editar otro usuario,
                        o nombre/correo inválidos o duplicados.
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
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario:
                raise ValueError("El usuario no existe")

            if nuevo_nombre is not None:
                usuario.nombre = nuevo_nombre

            if nuevo_correo is not None:
                existente = session.query(Usuario).filter(
                    Usuario.correo == nuevo_correo,
                    Usuario.idUsuario != id_usuario
                ).first()
                if existente:
                    raise ValueError(f"El correo '{nuevo_correo}' ya está registrado")
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
        Elimina el usuario activo. Solo puede eliminar su propio usuario.
        Limpia self.usuario_activo al finalizar.

        Raises:
            TypeError: Si el ID no es un entero.
            ValueError: Si no hay usuario activo, intenta eliminar otro usuario,
                        tiene materias asociadas, o el usuario no existe.
        """
        if not isinstance(id_usuario, int):
            raise TypeError("El ID debe ser un número entero")

        self._validar_usuario_activo()

        if id_usuario != self.usuario_activo.idUsuario:
            raise ValueError("Solo puede eliminar su propio usuario")

        session = Session()
        try:
            usuario = session.query(Usuario).filter_by(idUsuario=id_usuario).first()
            if not usuario:
                raise ValueError(f"El usuario con ID {id_usuario} no existe")

            if usuario.materias:
                raise ValueError("Debe eliminar primero todas las materias del usuario")

            session.delete(usuario)
            session.commit()
            self.usuario_activo = None
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
        Edita una materia del usuario activo.

        Raises:
            ValueError: Si no hay usuario activo, la materia no existe o
                        pertenece a otro usuario, nombre/color inválidos o duplicados.
        """
        self._validar_usuario_activo()

        if nuevo_nombre is not None:
            nuevo_nombre = self._validar_nombre_materia(nuevo_nombre)
        if nuevo_color is not None:
            self._validar_color_hex(nuevo_color)

        session = Session()
        try:
            materia = session.query(Materia).filter_by(idMateria=id_materia).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede editar una materia de otro usuario")

            if nuevo_nombre is not None:
                duplicado = session.query(Materia).filter(
                    Materia.nombre == nuevo_nombre,
                    Materia.usuario_id == self.usuario_activo.idUsuario,
                    Materia.idMateria != id_materia
                ).first()
                if duplicado:
                    raise ValueError(f"Ya existe una materia llamada '{nuevo_nombre}' para este usuario")
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
        Edita una tarea del usuario activo.

        Raises:
            ValueError: Si no hay usuario activo, la tarea no existe o es ajena,
                        validaciones de campos, o nueva materia es ajena.
        """
        self._validar_usuario_activo()

        if nuevo_titulo is not None:
            nuevo_titulo = self._validar_titulo_tarea(nuevo_titulo)

        if nueva_descripcion is not None and len(nueva_descripcion) > 500:
            raise ValueError("La descripción es muy larga (máximo 500 caracteres)")

        if nueva_fecha_entrega is not None:
            if not isinstance(nueva_fecha_entrega, date):
                raise ValueError("La fecha de entrega es inválida")
            if nueva_fecha_entrega < date.today():
                raise ValueError("La fecha de entrega no puede ser en el pasado")

        if nueva_prioridad is not None and not isinstance(nueva_prioridad, Prioridad):
            raise ValueError("La prioridad debe ser una instancia de Prioridad (Baja, Media o Alta)")

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=id_tarea).first()
            if not tarea:
                raise ValueError("La tarea no existe")

            materia_actual = session.query(Materia).filter_by(idMateria=tarea.materia_id).first()
            if materia_actual.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede editar una tarea de otro usuario")

            if nueva_materia_id is not None:
                nueva_materia = session.query(Materia).filter_by(idMateria=nueva_materia_id).first()
                if not nueva_materia:
                    raise ValueError("La nueva materia no existe")
                if nueva_materia.usuario_id != self.usuario_activo.idUsuario:
                    raise ValueError("No puede mover una tarea a una materia de otro usuario")
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
        """Retorna una materia por ID, o None si no existe."""
        session = Session()
        try:
            materia = session.query(Materia).filter_by(idMateria=materia_id).first()
            if materia:
                session.expunge(materia)
            return materia
        finally:
            session.close()

    def eliminar_materia(self, materia_id: int) -> bool:
        """
        Elimina una materia del usuario activo (y sus tareas en cascada).

        Raises:
            ValueError: Si no hay usuario activo, la materia no existe o es ajena.
        """
        self._validar_usuario_activo()

        session = Session()
        try:
            materia = session.query(Materia).filter_by(idMateria=materia_id).first()
            if not materia:
                raise ValueError("La materia no existe")
            if materia.usuario_id != self.usuario_activo.idUsuario:
                raise ValueError("No puede eliminar una materia de otro usuario")

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
        """Retorna una tarea por ID, o None si no existe."""
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
        Elimina una tarea del usuario activo.

        Raises:
            TypeError: Si el ID no es un entero.
            ValueError: Si no hay usuario activo, la tarea no existe o es ajena.
        """
        if not isinstance(id_tarea, int):
            raise TypeError("El ID de la tarea debe ser un número entero")

        self._validar_usuario_activo()

        session = Session()
        try:
            tarea = session.query(Tarea).filter_by(idTarea=id_tarea).first()
            if not tarea:
                raise ValueError(f"La tarea con id {id_tarea} no existe")

            materia = session.query(Materia).filter_by(idMateria=tarea.materia_id).first()
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