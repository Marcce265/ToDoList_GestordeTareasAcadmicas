import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Obtener la ruta del directorio actual (src/modelo)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Crear la ruta de la base de datos en src/modelo
db_path = os.path.join(current_dir, 'db.sqlite')
# Configurar base de datos SQLite en el directorio src/modelo
engine = create_engine(f'sqlite:///{db_path}', echo=False)
# engine = create_engine(f'sqlite:///data.db', echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()
session = Session()

# Crear la base de datos en memoria
# engine = create_engine('sqlite:///:memory:')
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
