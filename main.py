from src.model.declarative_base import engine, Base

# Carga los modelos (Perfil, Materia, Tarea)
import src.model.modelo

# Crea las tablas en db.sqlite
Base.metadata.create_all(engine)

print("Base de datos creada correctamente")
