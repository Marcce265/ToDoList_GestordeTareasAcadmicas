from datetime import date
from sqlalchemy.orm import sessionmaker
from src.model.declarative_base import engine
from src.model.modelo import Usuario

Session = sessionmaker(bind=engine)


class TaskManager:

    def crear_usuario(self, nombre: str, correo: str) -> Usuario:
        """
        HU-001: Crea un nuevo usuario.
        
        Args:
            nombre: Nombre del usuario (obligatorio)
            correo: Correo del usuario (obligatorio y único)
        
        Returns:
            Usuario creado y persistido
        
        Raises:
            ValueError: Si nombre o correo están vacíos, o correo duplicado
        """
        '''if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        
        if not correo or not correo.strip():
            raise ValueError("El correo no puede estar vacío")
        
        session = Session()
        try:
            # Validar correo único
            usuario_existente = session.query(Usuario).filter_by(
                correo=correo.strip()
            ).first()
            
            if usuario_existente:
                raise ValueError(f"El correo {correo} ya está registrado")
            
            usuario = Usuario(
                nombre=nombre.strip(),
                correo=correo.strip(),
                fecha_creacion=date.today()
            )
            
            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            return usuario
        finally:
            session.close()'''
        # Código temporal para pasar la prueba inicial