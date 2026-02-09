from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.modelo.declarative_base import Base
import enum


class Prioridad(enum.Enum):
    """
    Enumeración que representa el nivel de prioridad de una tarea.
    """
    Baja = "Baja"
    Media = "Media"
    Alta = "Alta"


class EstadoTarea(enum.Enum):
    """
    Enumeración que representa el estado actual de una tarea.
    """
    Pendiente = "Pendiente"
    Completada = "Completada"


class Perfil(Base):
    """
    Representa un perfil de usuario dentro del sistema.

    Un perfil puede poseer múltiples materias.
    """
    __tablename__ = 'perfiles'

    # Identificador único del perfil
    idPerfil = Column(Integer, primary_key=True)

    # Nombre del perfil
    nombre = Column(String, nullable=False)

    # Relación uno a muchos con Materia
    materias = relationship(
        "Materia",
        back_populates="perfil", cascade="all, delete-orphan")


class Materia(Base):
    """
    Representa una materia o categoría asociada a un perfil.

    Una materia pertenece a un perfil y puede contener varias tareas.
    """
    __tablename__ = 'materias'

    # Identificador único de la materia
    idMateria = Column(Integer, primary_key=True)

    # Nombre de la materia
    nombre = Column(String, nullable=False)

    # Color identificador de la materia
    color = Column(String, nullable=True)

    # Clave foránea que referencia al perfil dueño de la materia
    perfil_id = Column(Integer, ForeignKey('perfiles.idPerfil'))

    # Relación muchos a uno con Perfil
    perfil = relationship(
        "Perfil",
        back_populates="materias"
    )

    # Relación uno a muchos con Tarea
    tareas = relationship(
        "Tarea", back_populates="materia", cascade="all, delete-orphan")
    


class Tarea(Base):
    """
    Representa una tarea dentro de una materia.

    Cada tarea tiene una prioridad, un estado y una fecha de entrega.
    """
    __tablename__ = 'tareas'

    # Identificador único de la tarea
    idTarea = Column(Integer, primary_key=True)

    # Título de la tarea
    titulo = Column(String, nullable=False)

    # Descripción detallada de la tarea
    descripcion = Column(String)

    # Nivel de prioridad de la tarea
    prioridad = Column(Enum(Prioridad), nullable=False)

    # Fecha de entrega de la tarea
    fechaEntrega = Column(Date)

    # Estado actual de la tarea
    estado = Column(Enum(EstadoTarea), nullable=False)

    # Clave foránea que referencia a la materia
    materia_id = Column(Integer, ForeignKey('materias.idMateria'))

    # Relación muchos a uno con Materia
    materia = relationship("Materia", back_populates="tareas")

    
