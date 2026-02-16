import src.model.modelo  # carga los modelos
from src.logic.task_manager import TaskManager
from src.model.declarative_base import engine, Base
from datetime import datetime
from src.model.modelo import Prioridad

# Carga los modelos (Perfil, Materia, Tarea)
import src.model.modelo

# Crea las tablas en db.sqlite
Base.metadata.create_all(engine)

print("Base de datos creada correctamente")
