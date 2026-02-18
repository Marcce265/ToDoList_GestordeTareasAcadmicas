from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, UniqueConstraint
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

    idUsuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # ← Agregar longitud máxima
    correo = Column(String(100), nullable=False, unique=True)  # ← Agregar longitud máxima
    fecha_creacion = Column(Date, nullable=False)  # ← Cambiar a NOT NULL

    materias = relationship(
        "Materia",
        back_populates="usuario",
        cascade="all, delete-orphan"  # ✅ Ya lo tienes
    )

    def __repr__(self):
        return f"<Usuario(id={self.idUsuario}, nombre={self.nombre})>"


class Materia(Base):
    __tablename__ = 'materias'

    idMateria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # ← Agregar longitud máxima
    color = Column(String(7), nullable=False)  # ← Cambiar a 7 caracteres (#RRGGBB)

    usuario_id = Column(
        Integer,
        ForeignKey('usuarios.idUsuario', ondelete='CASCADE'),  # ← Agregar ondelete
        nullable=False
    )

    usuario = relationship("Usuario", back_populates="materias")

    tareas = relationship(
        "Tarea",
        back_populates="materia",
        cascade="all, delete-orphan"  # ✅ Ya lo tienes
    )

    # ✅ NUEVO: Constraint único compuesto (nombre + usuario_id)
    __table_args__ = (
        UniqueConstraint('nombre', 'usuario_id', name='uq_materia_usuario'),
    )

    def __repr__(self):
        return f"<Materia(id={self.idMateria}, nombre={self.nombre})>"


class Tarea(Base):
    __tablename__ = 'tareas'

    idTarea = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)  # ← Agregar longitud máxima
    descripcion = Column(String(500))  # ← Agregar longitud máxima

    prioridad = Column(Enum(Prioridad), nullable=False)

    fechaEntrega = Column(Date, nullable=False)  # ← Cambiar a NOT NULL

    estado = Column(
        Enum(EstadoTarea),
        nullable=False,
        default=EstadoTarea.Pendiente
    )

    materia_id = Column(
        Integer,
        ForeignKey('materias.idMateria', ondelete='CASCADE'),  # ← Agregar ondelete
        nullable=False
    )

    materia = relationship("Materia", back_populates="tareas")

    def __repr__(self):
        return f"<Tarea(id={self.idTarea}, titulo={self.titulo})>"

if __name__ == "__main__":
    from src.model.declarative_base import engine
    Base.metadata.create_all(engine)
    print("✅ Base de datos creada")