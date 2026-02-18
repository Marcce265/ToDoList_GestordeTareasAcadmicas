from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.model.declarative_base import Base
import enum


class Prioridad(enum.Enum):
    Baja = "Baja"
    Media = "Media"
    Alta = "Alta"


class EstadoTarea(enum.Enum):
    Pendiente = "Pendiente"
    Completada = "Completada"


class Usuario(Base):
    __tablename__ = 'usuarios'

    idUsuario = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    fecha_creacion = Column(Date, nullable=True)

    materias = relationship(
        "Materia",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario(id={self.idUsuario}, nombre={self.nombre})>"


class Materia(Base):
    __tablename__ = 'materias'

    idMateria = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    color = Column(String, nullable=False)

    usuario_id = Column(
        Integer,
        ForeignKey('usuarios.idUsuario'),
        nullable=False
    )

    usuario = relationship("Usuario", back_populates="materias")

    tareas = relationship(
        "Tarea",
        back_populates="materia",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Materia(id={self.idMateria}, nombre={self.nombre})>"


class Tarea(Base):
    __tablename__ = 'tareas'

    idTarea = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)

    prioridad = Column(Enum(Prioridad), nullable=False)

    fechaEntrega = Column(Date)

    estado = Column(
        Enum(EstadoTarea),
        nullable=False,
        default=EstadoTarea.Pendiente
    )

    materia_id = Column(
        Integer,
        ForeignKey('materias.idMateria'),
        nullable=False
    )

    materia = relationship("Materia", back_populates="tareas")

    def __repr__(self):
        return f"<Tarea(id={self.idTarea}, titulo={self.titulo})>"
