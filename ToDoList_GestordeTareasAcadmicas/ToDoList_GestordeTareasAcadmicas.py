import reflex as rx
from src.views.seleccionar_perfil import seleccionar_perfil_view

app = rx.App()

app.add_page(
    seleccionar_perfil_view,
    route="/",
    title="Gestor de Tareas Académicas"
)
