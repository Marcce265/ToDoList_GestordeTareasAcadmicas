import reflex as rx
from src.state.app_state import AppState

def seleccionar_perfil_view():
    return rx.vstack(
        rx.text("Selecciona tu perfil"),
        rx.foreach(
            AppState.perfiles,
            lambda p: rx.button(
                p.nombre,
                on_click=lambda: AppState.seleccionar_perfil(p.idPerfil)
            )
        )
    )
