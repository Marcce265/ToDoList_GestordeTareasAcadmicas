from datetime import date
from sqlalchemy.orm import sessionmaker
from src.model.declarative_base import engine
from src.model.modelo import Usuario

Session = sessionmaker(bind=engine)


class TaskManager:

    def crear_usuario(self, nombre: str, correo: str) -> Usuario:
        """HU-001: Crea un nuevo usuario (Versión Refactorizada)"""
        
        # 1. Limpieza y validación temprana (fail-fast)
        nombre_clean = nombre.strip() if nombre else ""
        correo_clean = correo.strip() if correo else ""

        if not nombre_clean:
            raise ValueError("El nombre no puede estar vacío")
        if not correo_clean:
            raise ValueError("El correo no puede estar vacío")

        session = Session()
        try:
            # 2. Verificación de existencia
            if session.query(Usuario).filter_by(correo=correo_clean).first():
                raise ValueError(f"El correo {correo_clean} ya está registrado")

            # 3. Persistencia limpia
            nuevo_usuario = Usuario(
                nombre=nombre_clean,
                correo=correo_clean
                # La fecha se genera sola en el modelo ahora
            )
            
            session.add(nuevo_usuario)
            session.commit()
            session.refresh(nuevo_usuario)
            return nuevo_usuario
        finally:
            session.close()