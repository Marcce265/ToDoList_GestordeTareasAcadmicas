import reflex as rx
from src.state.app_state import AppState
from src.views.seleccionar_perfil import seleccionar_perfil_view

def index():
    return seleccionar_perfil_view()

app = rx.App(_state=AppState)
app.add_page(index)
