"""
TaskMaster Student — HU001 a HU011 completo
Uso: python -m src.view.ui_taskmaster  (o copia a raíz y corre directo)
"""

import flet as ft
from datetime import date, timedelta
from src.logic.task_manager import TaskManager
from src.model.modelo import Prioridad, EstadoTarea

# ── Paleta ──────────────────────────────────────────────
# ── Paleta MORADO MINIMALISTA ──────────────────────────────
BG      = "#FAFBFC"   # Fondo blanco suave
SURFACE = "#F5F3FF"   # Sidebar morado clarísimo
CARD    = "#FFFFFF"   # Tarjetas blancas puras
BORDER  = "#E9D5FF"   # Bordes morado pastel
INK     = "#1F1B2E"   # Texto principal oscuro
MUTED   = "#8B7CA8"   # Texto secundario morado grisáceo
ACCENT  = "#8B5CF6"   # Morado vibrante (violet-500)
DANGER  = "#EC4899"   # Rosa/magenta en lugar de rojo
SUCCESS = "#10B981"   # Verde esmeralda
ERR_BG  = "#FCE7F3"   # Rosa pastel
ERR_FG  = "#BE185D"   # Rosa oscuro
OK_BG   = "#ECFDF5"   # Verde menta claro
OK_FG   = "#059669"   # Verde esmeralda oscuro
WARN_BG = "#FEF3C7"   # Amarillo pastel
WARN_FG = "#D97706"   # Ámbar
FONT    = "Segoe UI"
AVATARES = ["🎓","👩‍💼","👨‍💻","📚","🧑‍🎓","✨","💜","🌸"]

COLORES_MATERIA = [
    ("#3B82F6", "Azul"),
    ("#EF4444", "Rojo"),
    ("#22C55E", "Verde"),
    ("#F59E0B", "Naranja"),
    ("#8B5CF6", "Morado"),
    ("#EC4899", "Rosa"),
    ("#14B8A6", "Turquesa"),
    ("#F97316", "Tomate"),
]

PRIORIDADES = [
    (Prioridad.Alta,  "Alta",  "#EF4444"),
    (Prioridad.Media, "Media", "#F59E0B"),
    (Prioridad.Baja,  "Baja",  "#22C55E"),
]

# ── Helpers ─────────────────────────────────────────────
def hex_alpha(color_hex, opacity):
    """
    Convierte color hex + opacidad a formato correcto #AARRGGBB
    opacity: 0.0 a 1.0
    """
    # Quitar el # si existe
    hex_color = color_hex.replace("#", "")
    # Convertir opacidad a hex (00-FF)
    alpha = format(int(opacity * 255), '02x')
    # Formato correcto: #AARRGGBB
    return f"#{alpha}{hex_color}"

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
        "success": (OK_BG,   OK_FG,   "✓  "),
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

def filled_btn(label, on_click, danger=False, disabled=False, icon=None):
    c = DANGER if danger else ACCENT
    return ft.ElevatedButton(
        text=label,
        on_click=on_click, disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor=c,
            color="#FFFFFF",
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
        bgcolor=SURFACE, 
        cursor_color=ACCENT,
    )

def small_icon_btn(icon, color, on_click, tooltip=""):
    return ft.Container(
        content=ft.Icon(icon, size=15, color=color),
        width=30, height=30,
        border_radius=6,
        bgcolor=hex_alpha(color, 0.10),
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        ink=True,
        tooltip=tooltip,
    )

def chip_prioridad(prioridad):
    colores = {Prioridad.Alta: "#EF4444", Prioridad.Media: "#F59E0B", Prioridad.Baja: "#22C55E"}
    nombres = {Prioridad.Alta: "Alta", Prioridad.Media: "Media", Prioridad.Baja: "Baja"}
    c = colores.get(prioridad, MUTED)
    return ft.Container(
        content=T(nombres.get(prioridad, "—"), size=10, color=c, weight=ft.FontWeight.W_600),
        bgcolor=hex_alpha(c, 0.10), border=_ball(hex_alpha(c, 0.20)),
        border_radius=6, padding=ft.Padding(8, 3, 8, 3),
    )

def chip_estado(estado):
    if estado == EstadoTarea.Completada:
        return ft.Container(
            content=T("✓ Completada", size=10, color=OK_FG, weight=ft.FontWeight.W_600),
            bgcolor=hex_alpha(OK_BG, 0.10), border=_ball(hex_alpha(OK_FG, 0.20)),
            border_radius=6, padding=ft.Padding(8, 3, 8, 3),
        )
    return ft.Container(
        content=T("Pendiente", size=10, color=WARN_FG, weight=ft.FontWeight.W_600),
        bgcolor=hex_alpha(WARN_BG, 0.10), border=_ball(hex_alpha(WARN_FG, 0.20)),
        border_radius=6, padding=ft.Padding(8, 3, 8, 3),
    )


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main(page: ft.Page):
    page.title             = "TaskMaster Student"
    page.bgcolor           = BG
    page.window_width = 820
    page.window_height = 700
    page.window_min_width = 620
    page.window_min_height = 540
    page.padding           = 0
    page.theme_mode        = ft.ThemeMode.LIGHT
    page.theme             = ft.Theme(color_scheme_seed=ACCENT, font_family=FONT)

    tm = TaskManager()

    area = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def render(ctrl):
        page.controls.clear()
        page.add(
            ft.Container(
                content=ctrl,
                padding=ft.Padding(32, 32, 32, 32),
                expand=True,
                bgcolor=BG,
            )
        )
        page.update()

    # ════════════════════════════════════════════════
    # HU001 — CREAR USUARIO
    # ════════════════════════════════════════════════
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
        actions=[ghost_btn("Cancelar", dlg_close), filled_btn("Crear cuenta", dlg_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg)

    def dlg_open(e=None):
        tf_n.value = ""; tf_c.value = ""
        tf_n.update(); tf_c.update()
        dlg_hide(); dlg.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU006 — EDITAR USUARIO (desde lista bienvenida)
    # ════════════════════════════════════════════════
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
            content=ft.Column([edit_ban, tf_en, ft.Container(height=4), tf_ec],
                               spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", edit_close), filled_btn("Guardar", edit_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_edit)

    def edit_open(u):
        _editing_id[0] = u.idUsuario
        tm.seleccionar_usuario(u.idUsuario)
        tf_en.value = u.nombre; tf_ec.value = u.correo
        tf_en.update(); tf_ec.update()
        edit_hide(); dlg_edit.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU007 — ELIMINAR USUARIO (desde lista bienvenida)
    # ════════════════════════════════════════════════
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
        title=T("¿Eliminar usuario?", size=17, weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                del_ban,
                T("Esta acción no se puede deshacer.", size=13, color=MUTED),
                T("Se eliminarán TODAS sus materias y tareas.", size=12, color=DANGER),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", del_close), filled_btn("Eliminar", del_confirm, danger=True)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_del)

    def del_open(u):
        _deleting_id[0] = u.idUsuario
        del_hide(); dlg_del.open = True; page.update()

    # ════════════════════════════════════════════════
    # LISTA USUARIOS (HU002)
    # ════════════════════════════════════════════════
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
                ft.Container(
                    content=ft.Text(emoji, size=22),
                    width=46, height=46,
                    bgcolor=hex_alpha(ACCENT, 0.12), border_radius=23,
                    alignment=ft.Alignment(0, 0),
                    border=_ball(hex_alpha(ACCENT, 0.25), 1),
                ),
                ft.Column([
                    T(u.nombre, size=14, weight=ft.FontWeight.W_700),
                    T(u.correo, size=11, color=MUTED),
                ], spacing=2, expand=True),
                ft.Row([
                    filled_btn("Seleccionar", _sel),
                    small_icon_btn(ft.icons.EDIT_OUTLINED, MUTED,
                                   lambda e, uu=u: edit_open(uu), tooltip="Editar"),
                    small_icon_btn(ft.icons.DELETE_OUTLINE, DANGER,
                                   lambda e, uu=u: del_open(uu), tooltip="Eliminar"),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=CARD, border=_ball(BORDER), border_radius=14,
            padding=ft.Padding(14, 14, 14, 14),
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                color="#00000025", offset=ft.Offset(0, 3)),
        )

    def lista_refresh():
        usuarios = tm.listar_usuarios()
        lista_col.controls.clear()
        for u in usuarios:
            lista_col.controls.append(_user_card(u))
        try: lista_col.update()
        except Exception: pass

    def build_bienvenida():
        btn_crear = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ADD, color=ACCENT, size=16),
                T("CREAR NUEVO USUARIO", size=12, weight=ft.FontWeight.W_700, color=ACCENT),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            border=_ball(ACCENT, 1.5), border_radius=12,
            padding=ft.Padding(0, 14, 0, 14),
            on_click=dlg_open, ink=True, bgcolor=hex_alpha(ACCENT, 0.12),
        )
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("👋", size=42, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    T("Bienvenido de vuelta", size=26, weight=ft.FontWeight.BOLD,
                      align=ft.TextAlign.CENTER),
                    T("Selecciona tu usuario para continuar",
                      size=13, color=MUTED, align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=ft.Padding(0, 0, 0, 28),
            ),
            ban_col, lista_col,
            ft.Container(height=8),
            btn_crear,
        ], spacing=8)

    # ════════════════════════════════════════════════
    # HU003 — CREAR MATERIA
    # ════════════════════════════════════════════════
    mat_ban, mat_show, mat_hide = make_banner()
    tf_mat_nombre = tfield("Nombre de la materia", "Ej: Cálculo I")
    _mat_color_sel = [COLORES_MATERIA[0][0]]
    _color_btns    = ft.Row([], spacing=8, wrap=True)

    def _build_color_picker():
        btns = []
        for hex_c, nombre in COLORES_MATERIA:
            sel = hex_c == _mat_color_sel[0]
            btns.append(ft.Container(
                content=ft.Icon(ft.icons.CHECK, size=12, color="#FFFFFF") if sel
                        else ft.Container(),
                width=28, height=28,
                bgcolor=hex_c, border_radius=14,
                alignment=ft.Alignment(0, 0),
                border=ft.border.all(3, "#FFFFFF") if sel else ft.border.all(2, hex_c),
                shadow=ft.BoxShadow(blur_radius=6, color=hex_alpha(hex_c, 0.33)) if sel else None,
                on_click=lambda e, hc=hex_c: _pick_color(hc),
                ink=True, tooltip=nombre,
            ))
        _color_btns.controls = btns
        try: _color_btns.update()
        except Exception: pass

    def _pick_color(hc):
        _mat_color_sel[0] = hc
        _build_color_picker()

    def mat_close(e=None): dlg_mat.open = False; page.update()

    def mat_submit(e):
        mat_hide()
        try:
            m = tm.crear_materia(tf_mat_nombre.value or "", _mat_color_sel[0])
            mat_close()
            _refresh_materias()
            ban_mat_show(f"Materia '{m.nombre}' creada.", "success")
        except (ValueError, TypeError) as ex:
            mat_show(str(ex), "error")

    dlg_mat = ft.AlertDialog(
        modal=True,
        title=T("Nueva materia", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                mat_ban, tf_mat_nombre,
                ft.Container(height=8),
                T("Color de la materia", size=12, color=MUTED),
                ft.Container(height=4),
                _color_btns,
            ], spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", mat_close), filled_btn("Crear materia", mat_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_mat)

    def mat_open(e=None):
        tf_mat_nombre.value = ""
        _mat_color_sel[0] = COLORES_MATERIA[0][0]
        tf_mat_nombre.update()
        _build_color_picker()
        mat_hide(); dlg_mat.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU008 — EDITAR MATERIA
    # ════════════════════════════════════════════════
    emat_ban, emat_show, emat_hide = make_banner()
    tf_emat_nombre = tfield("Nombre de la materia")
    _emat_color_sel = [COLORES_MATERIA[0][0]]
    _emat_color_btns = ft.Row([], spacing=8, wrap=True)
    _editing_mat_id  = [None]

    def _build_ecolor_picker():
        btns = []
        for hex_c, nombre in COLORES_MATERIA:
            sel = hex_c == _emat_color_sel[0]
            btns.append(ft.Container(
                content=ft.Icon(ft.icons.CHECK, size=12, color="#FFFFFF") if sel
                        else ft.Container(),
                width=28, height=28,
                bgcolor=hex_c, border_radius=14,
                alignment=ft.Alignment(0, 0),
                border=ft.border.all(3, "#FFFFFF") if sel else ft.border.all(2, hex_c),
                shadow=ft.BoxShadow(blur_radius=6, color=hex_alpha(hex_c, 0.33)) if sel else None,
                on_click=lambda e, hc=hex_c: _epick_color(hc),
                ink=True, tooltip=nombre,
            ))
        _emat_color_btns.controls = btns
        try: _emat_color_btns.update()
        except Exception: pass

    def _epick_color(hc):
        _emat_color_sel[0] = hc
        _build_ecolor_picker()

    def emat_close(e=None): dlg_emat.open = False; page.update()

    def emat_submit(e):
        emat_hide()
        try:
            tm.editar_materia(_editing_mat_id[0],
                              nuevo_nombre=tf_emat_nombre.value or None,
                              nuevo_color=_emat_color_sel[0])
            emat_close(); _refresh_materias()
        except (ValueError, TypeError) as ex:
            emat_show(str(ex), "error")

    dlg_emat = ft.AlertDialog(
        modal=True,
        title=T("Editar materia", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                emat_ban, tf_emat_nombre,
                ft.Container(height=8),
                T("Color de la materia", size=12, color=MUTED),
                ft.Container(height=4),
                _emat_color_btns,
            ], spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", emat_close), filled_btn("Guardar", emat_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_emat)

    def emat_open(m):
        _editing_mat_id[0] = m.idMateria
        tf_emat_nombre.value = m.nombre
        _emat_color_sel[0] = m.color
        tf_emat_nombre.update()
        _build_ecolor_picker()
        emat_hide(); dlg_emat.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU010 — ELIMINAR MATERIA
    # ════════════════════════════════════════════════
    delmat_ban, delmat_show, delmat_hide = make_banner()
    _deleting_mat_id = [None]

    def delmat_close(e=None): dlg_delmat.open = False; page.update()

    def delmat_confirm(e):
        try:
            tm.eliminar_materia(_deleting_mat_id[0])
            delmat_close(); _refresh_materias()
        except (ValueError, TypeError) as ex:
            delmat_show(str(ex), "error")

    dlg_delmat = ft.AlertDialog(
        modal=True,
        title=T("¿Eliminar materia?", size=17, weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                delmat_ban,
                T("Se eliminarán también todas las tareas de esta materia.", size=13, color=MUTED),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", delmat_close),
                 filled_btn("Eliminar", delmat_confirm, danger=True)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_delmat)

    def delmat_open(m):
        _deleting_mat_id[0] = m.idMateria
        delmat_hide(); dlg_delmat.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU004 — CREAR TAREA
    # ════════════════════════════════════════════════
    tar_ban, tar_show, tar_hide = make_banner()
    tf_tar_titulo = tfield("Título de la tarea", "Ej: Entrega parcial")
    tf_tar_desc   = ft.TextField(
        label="Descripción (opcional)", multiline=True, min_lines=2, max_lines=4,
        border_color=BORDER, focused_border_color=ACCENT, border_radius=10,
        text_style=ft.TextStyle(size=13, font_family=FONT, color=INK),
        label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT),
        bgcolor=SURFACE, cursor_color=ACCENT,
    )
    _tar_materia_id = [None]
    _tar_prioridad  = [Prioridad.Media]
    _tar_fecha      = [date.today() + timedelta(days=7)]
    _tar_mat_dd     = ft.Dropdown(label="Materia", border_radius=10, border_color=BORDER,
                                   focused_border_color=ACCENT,
                                   label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT))
    _tar_pri_dd     = ft.Dropdown(
        label="Prioridad", border_radius=10, border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT),
        value="Media",
        options=[ft.dropdown.Option("Alta"), ft.dropdown.Option("Media"), ft.dropdown.Option("Baja")],
    )
    tf_tar_fecha = tfield("Fecha entrega (YYYY-MM-DD)",
                          str(date.today() + timedelta(days=7)),
                          str(date.today() + timedelta(days=7)))

    def tar_close(e=None): dlg_tar.open = False; page.update()

    def tar_submit(e):
        tar_hide()
        try:
            pri_map = {"Alta": Prioridad.Alta, "Media": Prioridad.Media, "Baja": Prioridad.Baja}
            prioridad = pri_map.get(_tar_pri_dd.value, Prioridad.Media)
            fecha = date.fromisoformat(tf_tar_fecha.value.strip())
            mat_id = int(_tar_mat_dd.value)
            t = tm.crear_tarea(
                titulo=tf_tar_titulo.value or "",
                descripcion=tf_tar_desc.value or "",
                prioridad=prioridad,
                fecha_entrega=fecha,
                materia_id=mat_id,
            )
            tar_close(); _refresh_tareas()
            ban_tar_show(f"Tarea '{t.titulo}' creada.", "success")
        except ValueError as ex:
            tar_show(str(ex), "error")
        except Exception as ex:
            tar_show(f"Error: {ex}", "error")

    dlg_tar = ft.AlertDialog(
        modal=True,
        title=T("Nueva tarea", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                tar_ban, tf_tar_titulo,
                ft.Container(height=4), tf_tar_desc,
                ft.Container(height=4), _tar_mat_dd,
                ft.Container(height=4), _tar_pri_dd,
                ft.Container(height=4), tf_tar_fecha,
                T("Formato: YYYY-MM-DD  (Ej: 2026-03-15)", size=10, color=MUTED),
            ], spacing=6, tight=True),
            width=380, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", tar_close), filled_btn("Crear tarea", tar_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_tar)

    def tar_open(e=None):
        # Cargar materias del usuario activo
        from src.model.modelo import Materia
        from sqlalchemy.orm import sessionmaker
        from src.model.declarative_base import engine
        S = sessionmaker(bind=engine)
        s = S()
        mats = s.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
        s.close()
        if not mats:
            ban_tar_show("Primero debes crear al menos una materia.", "warn")
            return
        _tar_mat_dd.options = [ft.dropdown.Option(str(m.idMateria), m.nombre) for m in mats]
        _tar_mat_dd.value   = str(mats[0].idMateria)
        tf_tar_titulo.value = ""; tf_tar_desc.value = ""
        _tar_pri_dd.value   = "Media"
        tf_tar_fecha.value  = str(date.today() + timedelta(days=7))
        tf_tar_titulo.update(); tf_tar_desc.update()
        _tar_mat_dd.update(); _tar_pri_dd.update(); tf_tar_fecha.update()
        tar_hide(); dlg_tar.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU009 — EDITAR TAREA
    # ════════════════════════════════════════════════
    etar_ban, etar_show, etar_hide = make_banner()
    tf_etar_titulo = tfield("Título de la tarea")
    tf_etar_desc   = ft.TextField(
        label="Descripción", multiline=True, min_lines=2, max_lines=4,
        border_color=BORDER, focused_border_color=ACCENT, border_radius=10,
        text_style=ft.TextStyle(size=13, font_family=FONT, color=INK),
        label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT),
        bgcolor=SURFACE, cursor_color=ACCENT,
    )
    _etar_pri_dd = ft.Dropdown(
        label="Prioridad", border_radius=10, border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(size=12, color=MUTED, font_family=FONT),
        options=[ft.dropdown.Option("Alta"), ft.dropdown.Option("Media"), ft.dropdown.Option("Baja")],
    )
    tf_etar_fecha  = tfield("Fecha entrega (YYYY-MM-DD)")
    _editing_tar_id = [None]

    def etar_close(e=None): dlg_etar.open = False; page.update()

    def etar_submit(e):
        etar_hide()
        try:
            pri_map = {"Alta": Prioridad.Alta, "Media": Prioridad.Media, "Baja": Prioridad.Baja}
            prioridad = pri_map.get(_etar_pri_dd.value, Prioridad.Media)
            fecha = date.fromisoformat(tf_etar_fecha.value.strip())
            tm.editar_tarea(
                _editing_tar_id[0],
                nuevo_titulo=tf_etar_titulo.value or None,
                nueva_descripcion=tf_etar_desc.value or None,
                nueva_prioridad=prioridad,
                nueva_fecha_entrega=fecha,
            )
            etar_close(); _refresh_tareas()
        except (ValueError, TypeError) as ex:
            etar_show(str(ex), "error")

    dlg_etar = ft.AlertDialog(
        modal=True,
        title=T("Editar tarea", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                etar_ban, tf_etar_titulo,
                ft.Container(height=4), tf_etar_desc,
                ft.Container(height=4), _etar_pri_dd,
                ft.Container(height=4), tf_etar_fecha,
            ], spacing=6, tight=True),
            width=380, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", etar_close), filled_btn("Guardar", etar_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_etar)

    def etar_open(t):
        _editing_tar_id[0] = t.idTarea
        tf_etar_titulo.value = t.titulo
        tf_etar_desc.value   = t.descripcion or ""
        _etar_pri_dd.value   = t.prioridad.name if t.prioridad else "Media"
        tf_etar_fecha.value  = str(t.fechaEntrega)
        tf_etar_titulo.update(); tf_etar_desc.update()
        _etar_pri_dd.update(); tf_etar_fecha.update()
        etar_hide(); dlg_etar.open = True; page.update()

    # ════════════════════════════════════════════════
    # HU011 — ELIMINAR TAREA
    # ════════════════════════════════════════════════
    deltar_ban, deltar_show, deltar_hide = make_banner()
    _deleting_tar_id = [None]

    def deltar_close(e=None): dlg_deltar.open = False; page.update()

    def deltar_confirm(e):
        try:
            tm.eliminar_tarea(_deleting_tar_id[0])
            deltar_close(); _refresh_tareas()
        except (ValueError, TypeError) as ex:
            deltar_show(str(ex), "error")

    dlg_deltar = ft.AlertDialog(
        modal=True,
        title=T("¿Eliminar tarea?", size=17, weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                deltar_ban,
                T("Esta acción no se puede deshacer.", size=13, color=MUTED),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", deltar_close),
                 filled_btn("Eliminar", deltar_confirm, danger=True)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_deltar)

    def deltar_open(t):
        _deleting_tar_id[0] = t.idTarea
        deltar_hide(); dlg_deltar.open = True; page.update()

    # ════════════════════════════════════════════════
    # DASHBOARD — SECCIÓN MATERIAS (HU003/008/010)
    # ════════════════════════════════════════════════
    mat_body    = ft.Column([], spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    ban_mat_col, ban_mat_show, ban_mat_hide = make_banner()

    def _materia_card(m, num_tareas=0):
        return ft.Container(
            content=ft.Row([
                ft.Container(width=8, bgcolor=m.color, border_radius=4,
                             height=50, margin=ft.margin.only(right=4)),
                ft.Column([
                    T(m.nombre, size=14, weight=ft.FontWeight.W_700),
                    T(f"{num_tareas} tareas",
                      size=11, color=MUTED),
                ], spacing=2, expand=True),
                ft.Row([
                    small_icon_btn(ft.icons.EDIT_OUTLINED, MUTED,
                                   lambda e, mm=m: emat_open(mm), tooltip="Editar"),
                    small_icon_btn(ft.icons.DELETE_OUTLINE, DANGER,
                                   lambda e, mm=m: delmat_open(mm), tooltip="Eliminar"),
                ], spacing=6),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=CARD, border=_ball(BORDER), border_radius=14,
            padding=ft.Padding(14, 12, 14, 12),
            shadow=ft.BoxShadow(blur_radius=8, color="#00000015", offset=ft.Offset(0, 2)),
        )

    def _refresh_materias():
        if not tm.usuario_activo: return
        from src.model.modelo import Materia, Tarea
        from sqlalchemy.orm import sessionmaker
        from src.model.declarative_base import engine
        S = sessionmaker(bind=engine)
        s = S()
        mats = s.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
        conteos = {}
        for m in mats:
            conteos[m.idMateria] = s.query(Tarea).filter_by(materia_id=m.idMateria).count()
        s.close()
        mat_body.controls.clear()
        mat_body.controls.append(ban_mat_col)
        if not mats:
            mat_body.controls.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.BOOK_OUTLINED, size=48, color=hex_alpha(MUTED, 0.33)),
                    ft.Container(height=8),
                    T("No tienes materias aún", size=14, color=MUTED,
                      align=ft.TextAlign.CENTER),
                    T("Crea tu primera materia con el botón +",
                      size=12, color=MUTED, align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                alignment=ft.Alignment(0, 0), padding=ft.Padding(0, 40, 0, 0),
            ))
        else:
            for m in mats:
                mat_body.controls.append(_materia_card(m, conteos.get(m.idMateria, 0)))
        try: mat_body.update()
        except Exception: pass

    def build_materias_view():
        return ft.Column([
            ft.Row([
                T("Mis Materias", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                filled_btn("+ Nueva materia", mat_open, icon=ft.icons.ADD),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=16),
            mat_body,
        ], expand=True)

    # ════════════════════════════════════════════════
    # DASHBOARD — SECCIÓN TAREAS (HU004/005/009/011)
    # ════════════════════════════════════════════════
    tar_body    = ft.Column([], spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    ban_tar_col, ban_tar_show, ban_tar_hide = make_banner()
    _filtro_estado = [None]  # None=todos, True=completadas, False=pendientes

    def _tarea_card(t):
        completada = t.estado == EstadoTarea.Completada

        def toggle(e):
            try:
                if completada:
                    tm.desmarcar_tarea(t.idTarea)
                else:
                    tm.marcar_tarea(t.idTarea)
                _refresh_tareas()
            except ValueError as ex:
                ban_tar_show(str(ex), "error")

        return ft.Container(
            content=ft.Row([
                # Checkbox
                ft.Container(
                    content=ft.Icon(
                        ft.icons.CHECK_CIRCLE if completada else ft.icons.RADIO_BUTTON_UNCHECKED,
                        size=22,
                        color=SUCCESS if completada else BORDER,
                    ),
                    on_click=toggle, ink=True,
                    border_radius=11, width=36, height=36,
                    alignment=ft.Alignment(0, 0),
                    tooltip="Marcar/desmarcar",
                ),
                # Info tarea
                ft.Column([
                    ft.Row([
                        T(t.titulo, size=13,
                          weight=ft.FontWeight.W_600,
                          color=MUTED if completada else INK),
                        chip_prioridad(t.prioridad),
                        chip_estado(t.estado),
                    ], spacing=8, wrap=True),
                    T(t.descripcion or "", size=11, color=MUTED,
                      italic=True) if t.descripcion else ft.Container(height=0),
                    T(f"Entrega: {t.fechaEntrega}", size=10, color=MUTED),
                ], spacing=3, expand=True),
                # Acciones
                ft.Row([
                    small_icon_btn(ft.icons.EDIT_OUTLINED, MUTED,
                                   lambda e, tt=t: etar_open(tt), tooltip="Editar"),
                    small_icon_btn(ft.icons.DELETE_OUTLINE, DANGER,
                                   lambda e, tt=t: deltar_open(tt), tooltip="Eliminar"),
                ], spacing=6),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=f"{SURFACE}" if completada else CARD,
            border=_ball(BORDER),
            border_radius=14,
            padding=ft.Padding(12, 12, 12, 12),
            shadow=ft.BoxShadow(blur_radius=8, color="#00000015", offset=ft.Offset(0, 2)),
            opacity=0.7 if completada else 1.0,
        )

    def _refresh_tareas():
        if not tm.usuario_activo: return
        from src.model.modelo import Tarea, Materia
        from sqlalchemy.orm import sessionmaker
        from src.model.declarative_base import engine
        S = sessionmaker(bind=engine)
        s = S()
        # Tareas del usuario activo
        mats = s.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
        mat_ids = [m.idMateria for m in mats]
        tareas = []
        if mat_ids:
            tareas = s.query(Tarea).filter(Tarea.materia_id.in_(mat_ids)).all()
        s.close()

        tar_body.controls.clear()
        tar_body.controls.append(ban_tar_col)

        # Filtro
        filtradas = tareas
        if _filtro_estado[0] is True:
            filtradas = [t for t in tareas if t.estado == EstadoTarea.Completada]
        elif _filtro_estado[0] is False:
            filtradas = [t for t in tareas if t.estado == EstadoTarea.Pendiente]

        if not filtradas:
            tar_body.controls.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.CHECKLIST_OUTLINED, size=48, color=f"{MUTED}55"),
                    ft.Container(height=8),
                    T("No hay tareas aquí", size=14, color=MUTED, align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                alignment=ft.Alignment(0, 0), padding=ft.Padding(0, 40, 0, 0),
            ))
        else:
            for t in filtradas:
                tar_body.controls.append(_tarea_card(t))
        try: tar_body.update()
        except Exception: pass

    def build_tareas_view():
        def set_filtro(v):
            _filtro_estado[0] = v
            _refresh_tareas()

        filtros = ft.Row([
            ft.TextButton("Todas",      on_click=lambda e: set_filtro(None)),
            ft.TextButton("Pendientes", on_click=lambda e: set_filtro(False)),
            ft.TextButton("Completadas",on_click=lambda e: set_filtro(True)),
        ], spacing=4)

        return ft.Column([
            ft.Row([
                T("Mis Tareas", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                filled_btn("+ Nueva tarea", tar_open, icon=ft.icons.ADD),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            filtros,
            ft.Container(height=8),
            tar_body,
        ], expand=True)

    # ════════════════════════════════════════════════
    # DASHBOARD LAYOUT
    # ════════════════════════════════════════════════
    _dash_body = ft.Column([], expand=True)
    _nav_idx   = [0]
    _nav_col   = ft.Column([], spacing=4)

    def _nav_pill(label, idx, icon):
        active = _nav_idx[0] == idx
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ACCENT if active else MUTED, size=16),
                T(label, size=13, color=ACCENT if active else MUTED,
                  weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL),
            ], spacing=10),
            bgcolor=hex_alpha(ACCENT, 0.10) if active else "transparent",
            border_radius=10,
            padding=ft.Padding(14, 10, 14, 10),
            on_click=lambda e, i=idx: _nav_to(i),
            ink=True,
        )

    def _refresh_nav():
        _nav_col.controls = [
            _nav_pill("📚 Materias",   0, ft.icons.BOOK_OUTLINED),
            _nav_pill("📝 Tareas",     1, ft.icons.CHECKLIST_OUTLINED),
            _nav_pill("👤 Mi Usuario", 2, ft.icons.PERSON_OUTLINED),
        ]
        try: _nav_col.update()
        except Exception: pass

    def _nav_to(idx):
        _nav_idx[0] = idx
        _refresh_nav()
        _show_seccion(idx)

    def build_usuario_view():
        u = tm.usuario_activo
        if not u:
            return ft.Container()
        return ft.Column([
            T("Mi Usuario", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(AVATARES[u.idUsuario % len(AVATARES)], size=32),
                        ft.Column([
                            T(u.nombre, size=16, weight=ft.FontWeight.W_700),
                            T(u.correo, size=13, color=MUTED),
                        ], spacing=2, expand=True),
                    ], spacing=14),
                    ft.Container(height=16),
                    ft.Row([
                        filled_btn("Editar", dash_edit_open),
                        filled_btn("Eliminar", dash_del_open, danger=True),
                    ], spacing=10),
                ], spacing=8),
                bgcolor=CARD, border=_ball(BORDER), border_radius=14,
                padding=ft.Padding(24, 20, 24, 20),
            ),
        ], expand=True)

    def _show_seccion(idx):
        if idx == 0:
            _refresh_materias()
            _dash_body.controls = [build_materias_view()]
        elif idx == 1:
            _refresh_tareas()
            _dash_body.controls = [build_tareas_view()]
        elif idx == 2:
            _dash_body.controls = [build_usuario_view()]
        try: _dash_body.update()
        except Exception: pass

    # Sidebar usuario info
    _av_txt  = ft.Text("🎓", size=20)
    _uname   = T("—", size=14, weight=ft.FontWeight.W_700)
    _uemail  = T("—", size=11, color=MUTED)
    _av_cont = ft.Container(
        content=_av_txt, width=40, height=40,
        bgcolor=hex_alpha(ACCENT, 0.15), border_radius=20,
        alignment=ft.Alignment(0, 0),
        border=_ball(hex_alpha(ACCENT, 0.20), 1),
    )

    def _refresh_sidebar_user():
        u = tm.usuario_activo
        if not u: return
        _av_txt.value = AVATARES[u.idUsuario % len(AVATARES)]
        _uname.value  = u.nombre
        _uemail.value = u.correo
        try: _av_cont.update(); _uname.update(); _uemail.update()
        except Exception: pass

    # Editar/Eliminar desde sidebar dashboard
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
            dash_edit_close(); _refresh_sidebar_user()
        except (ValueError, TypeError) as ex:
            dash_edit_show(str(ex), "error")

    dlg_dash_edit = ft.AlertDialog(
        modal=True,
        title=T("Editar mi cuenta", size=17, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([dash_edit_ban, tf_de_n,
                               ft.Container(height=4), tf_de_c],
                               spacing=8, tight=True),
            width=360, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", dash_edit_close),
                 filled_btn("Guardar", dash_edit_submit)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_dash_edit)

    def dash_edit_open(e=None):
        u = tm.usuario_activo
        if not u: return
        tf_de_n.value = u.nombre; tf_de_c.value = u.correo
        tf_de_n.update(); tf_de_c.update()
        dash_edit_hide(); dlg_dash_edit.open = True; page.update()

    dash_del_ban, dash_del_show, dash_del_hide = make_banner()

    def dash_del_close(e=None): dlg_dash_del.open = False; page.update()

    def dash_del_confirm(e):
        u = tm.usuario_activo
        if not u: return
        try:
            tm.eliminar_usuario(u.idUsuario)
            dash_del_close(); ir_bienvenida()
        except (ValueError, TypeError) as ex:
            dash_del_show(str(ex), "error")

    dlg_dash_del = ft.AlertDialog(
        modal=True,
        title=T("¿Eliminar cuenta?", size=17, weight=ft.FontWeight.BOLD, color=DANGER),
        content=ft.Container(
            content=ft.Column([
                dash_del_ban,
                T("Esta acción eliminará tu cuenta y todos tus datos.", size=13, color=MUTED),
            ], spacing=8, tight=True),
            width=320, padding=ft.Padding(0, 4, 0, 4),
        ),
        actions=[ghost_btn("Cancelar", dash_del_close),
                 filled_btn("Eliminar", dash_del_confirm, danger=True)],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=CARD,
    )
    page.overlay.append(dlg_dash_del)

    def dash_del_open(e=None):
        dash_del_hide(); dlg_dash_del.open = True; page.update()

    sidebar = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.TASK_ALT, color=ACCENT, size=18),
                    T("TaskMaster", size=14, weight=ft.FontWeight.W_700),
                ], spacing=8),
                padding=ft.Padding(18, 20, 18, 16),
            ),
            ft.Divider(color=BORDER, height=1),
            ft.Container(height=10),
            ft.Container(content=_nav_col, padding=ft.Padding(8, 0, 8, 0)),
            ft.Container(expand=True),
            ft.Divider(color=BORDER, height=1),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        _av_cont,
                        ft.Column([_uname, _uemail], spacing=1, expand=True),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.EDIT_OUTLINED, size=13, color=MUTED),
                                T("Editar", size=11, color=MUTED),
                            ], spacing=5),
                            on_click=dash_edit_open, ink=True, border_radius=7,
                            padding=ft.Padding(10, 6, 10, 6), bgcolor=hex_alpha(MUTED, 0.07),
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.DELETE_OUTLINE, size=13, color=DANGER),
                                T("Eliminar", size=11, color=DANGER),
                            ], spacing=5),
                            on_click=dash_del_open, ink=True, border_radius=7,
                            padding=ft.Padding(10, 6, 10, 6), bgcolor=hex_alpha(DANGER, 0.07),
                        ),
                    ], spacing=6),
                    ft.Container(height=6),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.LOGOUT, size=13, color=MUTED),
                            T("Cerrar sesión", size=11, color=MUTED),
                        ], spacing=6),
                        on_click=lambda e: ir_bienvenida(),
                        ink=True, border_radius=7,
                        padding=ft.Padding(10, 6, 10, 6), bgcolor=hex_alpha(MUTED, 0.04),
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
            padding=ft.Padding(32, 28, 32, 28),
        ),
    ], spacing=0, expand=True)

    # ════════════════════════════════════════════════
    # NAVEGACIÓN PRINCIPAL
    # ════════════════════════════════════════════════
    def ir_bienvenida():
        lista_refresh()
        render(build_bienvenida())

    def ir_dashboard():
        _refresh_sidebar_user()
        _nav_idx[0] = 0
        _refresh_nav()
        _show_seccion(0)
        render(dashboard_view)

    tm.usuario_activo = None
    lista_refresh()
    render(build_bienvenida())


if __name__ == "__main__":
    ft.app(target=main)