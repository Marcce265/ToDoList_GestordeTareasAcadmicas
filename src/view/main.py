import flet as ft
from src.logic.task_manager import TaskManager

tm = TaskManager()

def main(page: ft.Page):
    page.title = "TaskMaster Pro"
    page.bgcolor = "#F7F2E8"
    page.window_width = 450
    page.window_height = 800

    def mostrar_snack(texto, color="#2E4053"):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # --- HU-001: LOGIN ---
    def vista_login():
        page.clean()
        nombre_tf = ft.TextField(label="Nombre (para registro)", border_radius=15)
        correo_tf = ft.TextField(label="Correo", border_radius=15)

        def ingresar(e):
            if not correo_tf.value: return
            try:
                u = tm.buscar_usuario_por_correo(correo_tf.value)
                if not u and nombre_tf.value:
                    u = tm.crear_usuario(nombre_tf.value, correo_tf.value)
                if u:
                    vista_perfiles()
                else:
                    mostrar_snack("Usuario no encontrado.")
            except Exception as ex:
                mostrar_snack(str(ex), "red")

        page.add(
            ft.Container(
                content=ft.Column([
                    # Usamos strings para evitar errores de atributo
                    ft.Icon("check_circle_outline", size=60, color="#C0392B"),
                    ft.Text("Bienvenido", size=30, weight="bold"),
                    nombre_tf, correo_tf,
                    ft.FilledButton(
                    content=ft.Text("ENTRAR"),  # <-- ASÍ DEBE SER
                    style=ft.ButtonStyle(bgcolor="#2E4053", color="white"),
                    width=400, 
                    on_click=ingresar
)
                ], horizontal_alignment="center", spacing=15),
                padding=40, bgcolor="white", border_radius=30, 
                alignment=ft.alignment.Alignment(0, 0) # Solución manual para center
            )
        )
        page.update()

    # --- HU-002: PERFILES ---
    def vista_perfiles():
        page.clean()
        usuarios = tm.listar_usuarios()
        lista = ft.Column(spacing=10, scroll="auto")
        for u in usuarios:
            lista.controls.append(
                ft.ListTile(
                    leading=ft.Icon("person"),
                    title=ft.Text(u.nombre),
                    subtitle=ft.Text(u.correo),
                    on_click=lambda e, uid=u.idUsuario: vista_tablero(uid)
                )
            )
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona tu perfil", size=20, weight="bold"),
                    lista
                ]), padding=20
            )
        )
        page.update()

    # --- HU-003: MATERIAS ---
    def vista_tablero(uid):
        page.clean()
        u = tm.seleccionar_usuario(uid)
        lista_materias = ft.Column(spacing=10, scroll="auto")
        
        def refrescar():
            u_upd = tm.seleccionar_usuario(uid)
            lista_materias.controls.clear()
            if u_upd.materias:
                for mat in u_upd.materias:
                    lista_materias.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.VerticalDivider(width=5, color=mat.color),
                                ft.Text(mat.nombre, size=18, weight="bold", expand=True),
                                ft.Icon("chevron_right")
                            ]),
                            bgcolor="white", padding=15, border_radius=10
                        )
                    )
            page.update()

        def abrir_modal(e):
            nom = ft.TextField(label="Nombre de Materia", autofocus=True)
            col = ft.Dropdown(label="Color", value="#3498DB", options=[
                ft.dropdown.Option("#3498DB", "Azul"),
                ft.dropdown.Option("#E74C3C", "Rojo"),
                ft.dropdown.Option("#2ECC71", "Verde"),
            ])
            
            def guardar(e):
                if nom.value:
                    tm.crear_materia(nom.value, col.value, uid)
                    dlg.open = False
                    refrescar()

            dlg = ft.AlertDialog(
                title=ft.Text("Nueva Materia"),
                content=ft.Column([nom, col], tight=True),
                actions=[ft.TextButton("Guardar", on_click=guardar)]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        refrescar()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Materias de {u.nombre}", size=24, weight="bold"),
                    lista_materias
                ]), padding=20
            ),
            ft.FloatingActionButton(icon="add", bgcolor="#C0392B", on_click=abrir_modal)
        )
        page.update()

    # EJECUCIÓN INICIAL
    vista_login()

# Usamos run() si app() falla, pero flet.app(target=main) suele bastar
ft.app(target=main)