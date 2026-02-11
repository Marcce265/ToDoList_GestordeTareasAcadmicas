import reflex as rx
from src.logica.task_manager import TaskManager

tm = TaskManager()

class AppState(rx.State):
    perfil_id: int | None = None
    perfiles: list = []

    def cargar_perfiles(self):
        self.perfiles = tm.listar_perfiles()

    def seleccionar_perfil(self, perfil_id: int):
        perfil = tm.seleccionar_perfil(perfil_id)
        if perfil:
            self.perfil_id = perfil.idPerfil
