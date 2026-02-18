import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Obtener la ruta del directorio actual (src/model)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Crear la ruta de la base de datos en src/model
db_path = os.path.join(current_dir, 'db.sqlite')

# Configurar base de datos SQLite en el directorio src/model
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# ✅ MEJORA: No crear session global aquí
# Crear factory de sesiones
Session = sessionmaker(bind=engine)

Base = declarative_base()

# ❌ ELIMINAR: No crear session global
# session = Session()
# Razón: Cada TaskManager debe crear su propia sesión