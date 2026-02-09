from src.modelo.declarative_base import Session
from src.modelo.modelo import Perfil

class TaskManager:
    def crear_perfil(self, nombre):
        session = Session()
        perfil = Perfil(nombre=nombre)
        session.add(perfil)
        session.commit()
        session.refresh(perfil)
        session.close()
        return perfil

    def seleccionar_perfil(self, id_perfil):
        session = Session()
        perfil = session.query(Perfil).filter_by(idPerfil=id_perfil).first()
        session.close()
        return perfil

