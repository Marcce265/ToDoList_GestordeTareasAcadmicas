"""
modelo.py
=========
Definición de los modelos ORM (Object-Relational Mapping) del proyecto
TaskMaster Student usando SQLAlchemy.

Este módulo define las entidades principales del sistema:
    - Prioridad:   Enumeración de niveles de prioridad para tareas.
    - EstadoTarea: Enumeración de estados posibles de una tarea.
    - Usuario:     Representa a un estudiante registrado en el sistema.
    - Materia:     Representa una asignatura académica asociada a un usuario.
    - Tarea:       Representa una tarea académica asociada a una materia.

Relaciones:
    Usuario 1──N Materia 1──N Tarea

Ejecución directa:
    python -m src.model.modelo
    Crea todas las tablas en la base de datos si no existen.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from src.model.declarative_base import Base
import enum


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class Prioridad(enum.Enum):
    """
    Niveles de prioridad disponibles para una tarea académica.

    Valores:
        Baja:  Tarea de baja urgencia o importancia.
        Media: Tarea de importancia moderada (valor por defecto sugerido).
        Alta:  Tarea urgente o de alta importancia.
    """
    Baja = "Baja"
    Media = "Media"
    Alta = "Alta"


class EstadoTarea(enum.Enum):
    """
    Estados posibles en el ciclo de vida de una tarea.

    Valores:
        Pendiente:  La tarea aún no ha sido completada (estado inicial).
        Completada: La tarea fue finalizada por el usuario.
    """
    Pendiente = "Pendiente"
    Completada = "Completada"


# ---------------------------------------------------------------------------
# Modelos ORM
# ---------------------------------------------------------------------------

class Usuario(Base):
    """
    Modelo que representa a un estudiante registrado en el sistema.

    El sistema permite un máximo de 5 usuarios simultáneos. Cada usuario
    puede tener múltiples materias asociadas. Al eliminarse un usuario,
    sus materias (y por cascada, sus tareas) se eliminan automáticamente.

    Atributos:
        idUsuario      (int):  Clave primaria autoincremental.
        nombre         (str):  Nombre completo del usuario (máx. 50 caracteres).
                               Solo letras y espacios, mínimo 3 caracteres.
        correo         (str):  Correo electrónico único (máx. 100 caracteres).
        fecha_creacion (date): Fecha en que se registró el usuario.
        materias       (list): Lista de objetos Materia asociados (relación 1-N).

    Restricciones de BD:
        - correo es UNIQUE a nivel de base de datos.
        - nombre y correo son NOT NULL.
    """

    __tablename__ = 'usuarios'

    idUsuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # ← Agregar longitud máxima
    # ← Agregar longitud máxima
    correo = Column(String(100), nullable=False, unique=True)
    fecha_creacion = Column(Date, nullable=False)  # ← Cambiar a NOT NULL

    # Relación 1-N con Materia.
    # cascade="all, delete-orphan": al eliminar un Usuario,
    # se eliminan automáticamente todas sus Materias.
    materias = relationship(
        "Materia",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Representación legible del objeto para depuración."""
        return f"<Usuario(id={self.idUsuario}, nombre={self.nombre})>"


class Materia(Base):
    """
    Modelo que representa una asignatura académica de un usuario.

    Cada materia pertenece a un único usuario y puede contener múltiples
    tareas. El nombre de la materia debe ser único dentro del mismo usuario,
    pero puede repetirse entre usuarios distintos.

    Atributos:
        idMateria  (int): Clave primaria autoincremental.
        nombre     (str): Nombre de la materia (máx. 50 caracteres, mín. 3).
        color      (str): Color identificador en formato HEX (#RRGGBB, 7 caracteres).
        usuario_id (int): FK hacia la tabla usuarios (NOT NULL).
        usuario    (obj): Objeto Usuario al que pertenece esta materia.
        tareas     (list): Lista de objetos Tarea asociados (relación 1-N).

    Restricciones de BD:
        - Unique constraint compuesto: (nombre, usuario_id).
          Un mismo usuario no puede tener dos materias con el mismo nombre.
        - FK usuario_id con ondelete='CASCADE': si se elimina el usuario,
          se eliminan sus materias automáticamente a nivel de BD.
    """
    __tablename__ = 'materias'

    idMateria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)  # ← Agregar longitud máxima
    # ← Cambiar a 7 caracteres (#RRGGBB)
    color = Column(String(7), nullable=False)

    usuario_id = Column(
        Integer,
        # ← Agregar ondelete
        ForeignKey('usuarios.idUsuario', ondelete='CASCADE'),
        nullable=False
    )

    # Relación inversa hacia Usuario
    usuario = relationship("Usuario", back_populates="materias")

    # Relación 1-N con Tarea.
    # cascade="all, delete-orphan": al eliminar una Materia,
    # se eliminan automáticamente todas sus Tareas.
    tareas = relationship(
        "Tarea",
        back_populates="materia",
        cascade="all, delete-orphan"
    )

    # Constraint único compuesto: un usuario no puede tener dos materias
    # con el mismo nombre.
    __table_args__ = (
        UniqueConstraint('nombre', 'usuario_id', name='uq_materia_usuario'),
    )

    def __repr__(self):
        """Representación legible del objeto para depuración."""
        return f"<Materia(id={self.idMateria}, nombre={self.nombre})>"


class Tarea(Base):
    """

    Cada tarea pertenece a una materia (y por tanto a un usuario). Al
    crearse, el estado inicial es siempre EstadoTarea.Pendiente. El usuario
    puede marcarla como Completada o volver a marcarla como Pendiente.

    Atributos:
        idTarea      (int):         Clave primaria autoincremental.
        titulo       (str):         Título de la tarea (máx. 100 caracteres, mín. 3).
        descripcion  (str|None):    Descripción opcional (máx. 500 caracteres).
        prioridad    (Prioridad):   Nivel de prioridad: Baja, Media o Alta.
        fechaEntrega (date):        Fecha límite de entrega (no puede ser pasada).
        estado       (EstadoTarea): Estado actual: Pendiente o Completada.
        materia_id   (int):         FK hacia la tabla materias (NOT NULL).
        materia      (obj):         Objeto Materia al que pertenece esta tarea.

    Restricciones de BD:
        - FK materia_id con ondelete='CASCADE': si se elimina la materia,
          se eliminan sus tareas automáticamente a nivel de BD.
        - estado tiene valor por defecto EstadoTarea.Pendiente.
    """

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
        ForeignKey('materias.idMateria', ondelete='CASCADE'),
        nullable=False
    )

    # Relación inversa hacia Materia
    materia = relationship("Materia", back_populates="tareas")

    def __repr__(self):
        """Representación legible del objeto para depuración."""
        return f"<Tarea(id={self.idTarea}, titulo={self.titulo})>"


# ---------------------------------------------------------------------------
# Punto de entrada para creación directa de tablas
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from src.model.declarative_base import engine
    Base.metadata.create_all(engine)
    print("✅ Base de datos creada")
