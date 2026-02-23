"""
declarative_base.py
====================
Módulo de configuración de la base de datos para el proyecto TaskMaster Student.

Este módulo centraliza la configuración de SQLAlchemy, definiendo el motor de
base de datos (engine), la fábrica de sesiones (Session) y la clase base
declarativa (Base) que heredan todos los modelos ORM del proyecto.

La base de datos utilizada es SQLite, almacenada localmente en el mismo
directorio que este archivo (src/model/db.sqlite).

Uso típico:
    from src.model.declarative_base import Base, engine, Session

    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(engine)

    # Abrir una sesión
    session = Session()
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Configuración de ruta de la base de datos
# ---------------------------------------------------------------------------

# Obtener la ruta absoluta del directorio donde reside este archivo (src/model)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta completa al archivo SQLite
db_path = os.path.join(current_dir, 'db.sqlite')

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

# Crear el motor de conexión SQLite.
# echo=False desactiva el log de sentencias SQL en consola.
# Para depuración, cambiar a echo=True.
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

# Session es una fábrica de sesiones ligada al engine.
# Cada componente (TaskManager, etc.) debe crear su propia sesión
# para evitar conflictos de estado entre operaciones concurrentes.
# NO se debe crear una sesión global compartida.
Session = sessionmaker(bind=engine)

# ---------------------------------------------------------------------------
# Base declarativa
# ---------------------------------------------------------------------------

# Base es la clase padre de todos los modelos ORM del proyecto.
# Al heredar de Base, un modelo queda registrado en Base.metadata,
# lo que permite crear/eliminar sus tablas con create_all / drop_all.
Base = declarative_base()
