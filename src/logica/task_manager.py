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
            materia = session.query(Materia).filter_by(idMateria=materia_id).first()
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
    


