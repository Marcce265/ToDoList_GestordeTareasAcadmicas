import reflex as rx
import sys
import os

# 1. Ruta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Imports
from src.modelo.declarative_base import Session, engine, Base
from src.modelo.modelo import Tarea, Prioridad, EstadoTarea

# 3. VÍNCULO FORZADO (Antes de cualquier consulta)
Base.metadata.create_all(engine)

class State(rx.State):
    tareas: list[dict] = []

    def obtener_tareas(self):
        with Session(bind=engine) as session:
            resultado = session.query(Tarea).all()
            self.tareas = [
                {"titulo": t.titulo, "prioridad": t.prioridad.value} 
                for t in resultado
            ]

    # NUEVA FUNCIÓN PARA PROBAR
    def crear_tarea_prueba(self):
        with Session(bind=engine) as session:
            nueva = Tarea(
                titulo="¡Mi primera tarea web!",
                prioridad=Prioridad.Alta,
                estado=EstadoTarea.Pendiente
                # Nota: Si materia_id es obligatorio, pon uno que exista o déjalo así si es opcional
            )
            session.add(nueva)
            session.commit()
        # Después de crearla, refrescamos la lista
        return State.obtener_tareas

def index() -> rx.Component:
    return rx.vstack(
            rx.heading("Gestor de Tareas Académicas", size="8"),
            rx.hstack(
                rx.button("Actualizar Lista", on_click=State.obtener_tareas, color_scheme="blue"),
                rx.button("Añadir Tarea de Prueba", on_click=State.crear_tarea_prueba, color_scheme="green"),
            ),
        
        # Si no hay tareas, mostrar un aviso
        rx.cond(
            State.tareas.length() == 0,
            rx.text("No hay tareas en la base de datos.", color="gray"),
            rx.foreach(
                State.tareas,
                lambda tarea: rx.card(
                    rx.hstack(
                        rx.text(tarea["titulo"], weight="bold"),
                        rx.badge(tarea["prioridad"], color_scheme="orange"),
                        justify="between",
                        width="100%",
                    ),
                    width="400px",
                    margin_y="2"
                )
            )
        ),
        spacing="4",
        padding_top="10%",
        align="center",
    )

app = rx.App()
app.add_page(index)