"""
TaskMaster Student — Bloque 1: Usuarios
Uso: python ui_usuarios.py
"""

import flet as ft
from src.logic.task_manager import TaskManager

# ── Paleta MORADO MINIMALISTA ──────────────────────────────
BG      = "#FAFBFC"   # Fondo blanco suave
SURFACE = "#F5F3FF"   # Sidebar morado clarísimo
CARD    = "#FFFFFF"   # Tarjetas blancas puras
BORDER  = "#E9D5FF"   # Bordes morado pastel
INK     = "#1F1B2E"   # Texto principal oscuro
MUTED   = "#8B7CA8"   # Texto secundario morado grisáceo
ACCENT  = "#8B5CF6"   # Morado vibrante (violet-500)
ACCENT2 = "#A78BFA"   # Morado más claro (violet-400)
DANGER  = "#EC4899"   # Rosa/magenta en lugar de rojo
ERR_BG  = "#FCE7F3"   # Rosa pastel
ERR_FG  = "#AD1010"   # Rosa oscuro
WARN_BG = "#FEF3C7"   # Amarillo pastel
WARN_FG = "#D97706"   # Ámbar
FONT    = "Segoe UI"
AVATARES = ["🎓","👩‍💼","👨‍💻","📚","🧑‍🎓","✨","💜","🌸"]


# ── Helpers ─────────────────────────────────────────────

def _ball(color, w=1):
    s = ft.BorderSide(w, color)
    return ft.Border(top=s, bottom=s, left=s, right=s)

def T(text, size=13, color=INK, weight=ft.FontWeight.NORMAL,
      align=ft.TextAlign.LEFT, italic=False):
    return ft.Text(text, size=size, color=color, weight=weight,
                   text_align=align, font_family=FONT, italic=italic)

def banner_ctrl(text, kind="error"):
    cfg = {
        "error":   (ERR_BG,  ERR_FG,  "✕  "),
        "success": (ACCENT.replace("#", "#15"), ACCENT, "✓  "),
        "warn":    (WARN_BG, WARN_FG, "⚠  "),
    }
    bg, fg, icon = cfg[kind]
    return ft.Container(
        content=ft.Text(icon + text, color=fg, size=12,
                        font_family=FONT, no_wrap=False),
        bgcolor=bg, border=_ball(fg), border_radius=8,
        padding=ft.Padding(12, 9, 12, 9),
    )

def make_banner():
    col = ft.Column([], spacing=0, visible=False)
    def _upd():
        try:
            if col.page: col.update()
        except Exception: pass
    def show(t, k="error"):
        col.controls = [banner_ctrl(t, k)]
        col.visible = True; _upd()
    def hide():
        col.visible = False; _upd()
    return col, show, hide

def filled_btn(label, on_click, danger=False, disabled=False):
    c = DANGER if danger else ACCENT
    return ft.FilledButton(
        content=ft.Text(label, size=12, weight=ft.FontWeight.W_600,
                        font_family=FONT, color="#FFFFFF"),
        on_click=on_click, disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: c,
                     ft.ControlState.HOVERED: c,
                     ft.ControlState.DISABLED: BORDER},
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=0,
            padding=ft.Padding(16, 10, 16, 10),
        ),
    )

def ghost_btn(label, on_click, color=MUTED):
    return ft.TextButton(
        content=ft.Text(label, size=13, weight=ft.FontWeight.W_500,
                        font_family=FONT, color=color),
        on_click=on_click,
    )

def tfield(label, hint="", value=""):
    return ft.TextField(
        label=label, hint_text=hint, value=value,
        border_color=BORDER, focused_border_color=ACCENT,
        border_radius=10,
        text_style=ft.TextStyle(size=13, font_family=FONT, color=INK),
        label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT),
        bgcolor=SURFACE, filled=True, fill_color=SURFACE,
        cursor_color=ACCENT,
    )

def small_icon_btn(icon, color, on_click, tooltip=""):
    """
    Botón de icono pequeño con estilo minimalista.
    Usa fondo muy sutil y color solo en el icono.
    """
    return ft.Container(
        content=ft.Icon(icon, size=16, color=color),
        width=34, height=34,
        border_radius=8,
        bgcolor="#FFFFFF",  # Fondo blanco
        border=_ball(BORDER, 1),  # Borde sutil
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        ink=True,
        tooltip=tooltip,
        shadow=ft.BoxShadow(
            blur_radius=4,
            spread_radius=0,
            color="#00000008",
            offset=ft.Offset(0, 2)
        ),
    )


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main(page: ft.Page):
    page.title             = "TaskMaster Student"
    page.bgcolor           = BG
    page.window.width      = 620
    page.window.height     = 700
    page.window.min_width  = 520
    page.window.min_height = 540
    page.padding           = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ACCENT, font_family=FONT)

    tm = TaskManager()

    area = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def render(ctrl):
        area.controls = [
            ft.Container(content=ctrl,
                         padding=ft.Padding(32, 32, 32, 32),
                         expand=True)
        ]
        area.update()

    # ── Diálogo CREAR ───────────────────────────────
    dlg_ban, dlg_show, dlg_hide = make_banner()
    tf_n = tfield("Nombre completo",    "Ej: María González")
    tf_c = tfield("Correo electrónico", "Ej: maria@mail.com")

    def dlg_close(e=None): dlg.open = False; page.update()

    def dlg_submit(e):
        dlg_hide()
        try:
            u = tm.crear_usuario(tf_n.value or "", tf_c.value or "")
            dlg_close(); lista_refresh()
            ban_show(f"Usuario '{u.nombre}' creado.", "success")
        except (ValueError, TypeError) as ex:
            dlg_show(str(ex), "error")

    dlg = ft.AlertDialog(
        modal=True,
        title=T("Nuevo usuario", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                dlg_ban, tf_n,
                ft.Container(height=4), tf_c,
                ft.Container(height=2),
                T("Solo letras en el nombre · correo único · máx. 5",
                  size=10, color=MUTED),
            ], spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[
            ghost_btn("Cancelar", dlg_close),
            filled_btn("Crear cuenta", dlg_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg)

    def dlg_open(e=None):
        tf_n.value = ""; tf_c.value = ""
        tf_n.update(); tf_c.update()
        dlg_hide(); dlg.open = True; page.update()

    # ── Diálogo EDITAR ──────────────────────────────
    edit_ban, edit_show, edit_hide = make_banner()
    tf_en = tfield("Nombre completo")
    tf_ec = tfield("Correo electrónico")
    _editing_id = [None]

    def edit_close(e=None): dlg_edit.open = False; page.update()

    def edit_submit(e):
        edit_hide()
        try:
            tm.editar_usuario(_editing_id[0],
                              nuevo_nombre=tf_en.value or None,
                              nuevo_correo=tf_ec.value or None)
            edit_close(); lista_refresh()
        except (ValueError, TypeError) as ex:
            edit_show(str(ex), "error")

    dlg_edit = ft.AlertDialog(
        modal=True,
        title=T("Editar usuario", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                edit_ban, tf_en,
                ft.Container(height=4), tf_ec,
            ], spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[
            ghost_btn("Cancelar", edit_close),
            filled_btn("Guardar", edit_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_edit)

    def edit_open(u):
        _editing_id[0] = u.idUsuario
        # Necesitamos seleccionar el usuario para poder editarlo
        tm.seleccionar_usuario(u.idUsuario)
        tf_en.value = u.nombre
        tf_ec.value = u.correo
        tf_en.update(); tf_ec.update()
        edit_hide(); dlg_edit.open = True; page.update()

    # ── Diálogo ELIMINAR ────────────────────────────
    del_ban, del_show, del_hide = make_banner()
    _deleting_id = [None]

    def del_close(e=None): dlg_del.open = False; page.update()

    def del_confirm(e):
        try:
            tm.seleccionar_usuario(_deleting_id[0])
            tm.eliminar_usuario(_deleting_id[0])
            del_close(); lista_refresh()
        except (ValueError, TypeError) as ex:
            del_show(str(ex), "error")

    dlg_del = ft.AlertDialog(
        modal=True,
        title=T("¿Eliminar usuario?", size=17,
                weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                del_ban,
                T("Esta acción no se puede deshacer.", size=13, color=MUTED),
                T("Se eliminarán todos sus datos.", size=12, color=DANGER),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[
            ghost_btn("Cancelar", del_close),
            filled_btn("Eliminar", del_confirm, danger=True),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_del)

    def del_open(u):
        _deleting_id[0] = u.idUsuario
        del_hide(); dlg_del.open = True; page.update()

    # ── Lista de usuarios ───────────────────────────
    lista_col = ft.Column([], spacing=10)
    ban_col, ban_show, ban_hide = make_banner()

    def _user_card(u):
        emoji = AVATARES[u.idUsuario % len(AVATARES)]

        def _sel(e):
            try:
                tm.seleccionar_usuario(u.idUsuario)
                ir_dashboard()
            except ValueError as ex:
                ban_show(str(ex), "error")

        return ft.Container(
            content=ft.Row([
                # Avatar con fondo BLANCO
                ft.Container(
                    content=ft.Text(emoji, size=22),
                    width=46, height=46,
                    bgcolor="#FFFFFF",  # ← BLANCO en lugar de color
                    border_radius=23,
                    alignment=ft.Alignment(0, 0),
                    border=_ball(BORDER, 1.5),  # ← Borde morado suave
                ),
            # ... resto igual
                # Info
                ft.Column([
                    T(u.nombre, size=14, weight=ft.FontWeight.W_700),
                    T(u.correo, size=11, color=MUTED),
                ], spacing=2, expand=True),
                # Botones: Seleccionar | Editar | Eliminar
                ft.Row([
                    filled_btn("Seleccionar", _sel),
                    small_icon_btn(
                        ft.Icons.EDIT_OUTLINED, MUTED,
                        lambda e, uu=u: edit_open(uu),
                        tooltip="Editar",
                    ),
                    small_icon_btn(
                        ft.Icons.DELETE_OUTLINE, DANGER,
                        lambda e, uu=u: del_open(uu),
                        tooltip="Eliminar",
                    ),
                ], spacing=6,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=14,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=CARD,
            border=_ball(BORDER),
            border_radius=14,
            padding=ft.Padding(14, 14, 14, 14),
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                color="#00000025",
                                offset=ft.Offset(0, 3)),
        )

    def lista_refresh():
        usuarios = tm.listar_usuarios()
        lista_col.controls.clear()
        for u in usuarios:
            lista_col.controls.append(_user_card(u))
        try: lista_col.update()
        except Exception: pass

    # ── Pantalla bienvenida ──────────────────────────
    def build_bienvenida():
        btn_crear = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color="#FFFFFF", size=16),
                T("CREAR NUEVO USUARIO", size=12,
                weight=ft.FontWeight.W_700, color="#FFFFFF"),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=ACCENT,  # ← morado sólido
            border_radius=12,
            padding=ft.Padding(0, 14, 0, 14),
            on_click=dlg_open,
            ink=True,
        )

        return ft.Column([
            # Encabezado
            ft.Container(
                content=ft.Column([
                    ft.Text("👋", size=42, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    T("Bienvenido de vuelta", size=26,
                      weight=ft.FontWeight.BOLD,
                      align=ft.TextAlign.CENTER),
                    T("Selecciona tu usuario para continuar",
                      size=13, color=MUTED, align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=4),
                padding=ft.Padding(0, 0, 0, 28),
            ),
            # Banner feedback
            ban_col,
            # Lista
            lista_col,
            ft.Container(height=8),
            # Botón crear
            btn_crear,
        ], spacing=8)

    # ══════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════
    _dash_body   = ft.Column([], expand=True)
    _nav_idx     = [0]

    # Nav pills
    _nav_col = ft.Column([], spacing=4)

    def _nav_pill(label, idx, icon):
        active = _nav_idx[0] == idx
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon,
                        color=ACCENT if active else MUTED,
                        size=16),
                T(label, size=13,
                  color=ACCENT if active else MUTED,
                  weight=ft.FontWeight.W_600 if active
                  else ft.FontWeight.NORMAL),
            ], spacing=10),
            bgcolor=ACCENT.replace("#", "#18") if active else "transparent",
            border_radius=10,
            padding=ft.Padding(14, 10, 14, 10),
            on_click=lambda e, i=idx: _nav_to(i),
            ink=True,
        )

    def _refresh_nav():
        _nav_col.controls = [
            _nav_pill("Materias", 0, ft.Icons.BOOK_OUTLINED),
            _nav_pill("Tareas",   1, ft.Icons.CHECKLIST_OUTLINED),
        ]
        try: _nav_col.update()
        except Exception: pass

    def _nav_to(idx):
        _nav_idx[0] = idx
        _refresh_nav()
        _show_seccion(idx)

    def _show_seccion(idx):
        labels = [
            ("Materias", ft.Icons.BOOK_OUTLINED),
            ("Tareas",   ft.Icons.CHECKLIST_OUTLINED),
        ]

        lbl, ico = labels[idx]

        _dash_body.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ico, color=ACCENT.replace("#", "#55"), size=48),
                    ft.Container(height=12),
                    T(lbl, size=20,
                    weight=ft.FontWeight.BOLD,
                    align=ft.TextAlign.CENTER),
                    T("Esta sección se implementará en el siguiente bloque.",
                    size=13, color=MUTED,
                    align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        ]
        try: _dash_body.update()
        except Exception: pass

    # Info usuario en sidebar
    _av_txt   = ft.Text("🎓", size=20)
    _uname    = T("—", size=14, weight=ft.FontWeight.W_700)
    _uemail   = T("—", size=11, color=MUTED)
    _av_cont = ft.Container(
        content=_av_txt, width=40, height=40,
        bgcolor="#FFFFFF",  # ← BLANCO
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        border=_ball(BORDER, 1.5),  # ← Borde morado suave
    )

    def _refresh_sidebar_user():
        u = tm.usuario_activo
        if not u: return
        _av_txt.value  = AVATARES[u.idUsuario % len(AVATARES)]
        _uname.value   = u.nombre
        _uemail.value  = u.correo
        try:
            _av_cont.update()
            _uname.update()
            _uemail.update()
        except Exception: pass

    # Diálogos editar/eliminar para el sidebar del dashboard
    dash_edit_ban, dash_edit_show, dash_edit_hide = make_banner()
    tf_de_n = tfield("Nombre completo")
    tf_de_c = tfield("Correo electrónico")

    def dash_edit_close(e=None): dlg_dash_edit.open = False; page.update()

    def dash_edit_submit(e):
        dash_edit_hide()
        u = tm.usuario_activo
        if not u: return
        try:
            tm.editar_usuario(u.idUsuario,
                              nuevo_nombre=tf_de_n.value or None,
                              nuevo_correo=tf_de_c.value or None)
            dash_edit_close()
            _refresh_sidebar_user()
        except (ValueError, TypeError) as ex:
            dash_edit_show(str(ex), "error")

    dlg_dash_edit = ft.AlertDialog(
        modal=True,
        title=T("Editar mi cuenta", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                dash_edit_ban, tf_de_n,
                ft.Container(height=4), tf_de_c,
            ], spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[
            ghost_btn("Cancelar", dash_edit_close),
            filled_btn("Guardar", dash_edit_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_dash_edit)

    def dash_edit_open(e=None):
        u = tm.usuario_activo
        if not u: return
        tf_de_n.value = u.nombre
        tf_de_c.value = u.correo
        tf_de_n.update(); tf_de_c.update()
        dash_edit_hide(); dlg_dash_edit.open = True; page.update()

    dash_del_ban, dash_del_show, dash_del_hide = make_banner()

    def dash_del_close(e=None): dlg_dash_del.open = False; page.update()

    def dash_del_confirm(e):
        u = tm.usuario_activo
        if not u: return
        try:
            tm.eliminar_usuario(u.idUsuario)
            dash_del_close()
            ir_bienvenida()
        except (ValueError, TypeError) as ex:
            dash_del_show(str(ex), "error")

    dlg_dash_del = ft.AlertDialog(
        modal=True,
        title=T("¿Eliminar cuenta?", size=17,
                weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                dash_del_ban,
                T("Esta acción eliminará tu cuenta y todos tus datos.",
                  size=13, color=MUTED),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[
            ghost_btn("Cancelar", dash_del_close),
            filled_btn("Eliminar", dash_del_confirm, danger=True),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_dash_del)

    def dash_del_open(e=None):
        dash_del_hide(); dlg_dash_del.open = True; page.update()

    # Sidebar
    sidebar = ft.Container(
        content=ft.Column([
            # Logo
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.TASK_ALT, color=ACCENT, size=18),
                    T("TaskMaster", size=14, weight=ft.FontWeight.W_700),
                ], spacing=8),
                padding=ft.Padding(18, 20, 18, 16),
            ),
            ft.Divider(color=BORDER, height=1),
            ft.Container(height=10),
            # Navegación
            ft.Container(
                content=_nav_col,
                padding=ft.Padding(8, 0, 8, 0),
            ),
            ft.Container(expand=True),
            ft.Divider(color=BORDER, height=1),
            # Perfil
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        _av_cont,
                        ft.Column([
                            _uname, _uemail,
                        ], spacing=1, expand=True),
                    ], spacing=10,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=10),
                    # Editar y Eliminar cuenta
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EDIT_OUTLINED,
                                        size=13, color=MUTED),
                                T("Editar", size=11, color=MUTED),
                            ], spacing=5),
                            on_click=dash_edit_open,
                            ink=True, border_radius=7,
                            padding=ft.Padding(10, 6, 10, 6),
                            bgcolor=f"{MUTED}12",
                            tooltip="Editar cuenta",
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DELETE_OUTLINE,
                                        size=13, color=DANGER),
                                T("Eliminar", size=11, color=DANGER),
                            ], spacing=5),
                            on_click=dash_del_open,
                            ink=True,
                            border_radius=7,
                            padding=ft.Padding(10, 6, 10, 6),
                            bgcolor=f"{DANGER}15",
                            tooltip="Eliminar cuenta",
                        ),
                    ], spacing=6),
                    ft.Container(height=6),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGOUT,
                                    size=13, color=ACCENT),
                            T("Cerrar sesión", size=11, color=ACCENT),
                        ], spacing=6),
                        on_click=lambda e: ir_bienvenida(),
                        ink=True,
                        border_radius=7,
                        padding=ft.Padding(10, 6, 10, 6),
                        bgcolor=ACCENT.replace("#", "#12"),
                    ),
                ], spacing=0),
                padding=ft.Padding(12, 14, 12, 16),
            ),
        ], spacing=0),
        bgcolor=SURFACE,
        border=ft.Border(right=ft.BorderSide(1, BORDER)),
        width=210,
    )

    dashboard_view = ft.Row([
        sidebar,
        ft.Container(
            content=_dash_body,
            expand=True, bgcolor=BG,
            padding=ft.Padding(36, 32, 36, 32),
        ),
    ], spacing=0, expand=True)

    # ── Navegación principal ─────────────────────────

    def ir_bienvenida():
        lista_refresh()
        render(build_bienvenida())

    def ir_dashboard():
        _refresh_sidebar_user()
        _nav_idx[0] = 0
        _refresh_nav()
        _show_seccion(0)
        render(dashboard_view)

    page.add(
        ft.Column([
            ft.Container(content=area, expand=True, bgcolor=BG),
        ], spacing=0, expand=True)
    )

    ir_bienvenida()


if __name__ == "__main__":
    ft.run(main)