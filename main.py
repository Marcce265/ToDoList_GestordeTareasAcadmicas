import src.model.modelo
from src.logic.task_manager import TaskManager
from src.model.declarative_base import engine, Base
from src.model.modelo import Prioridad, EstadoTarea
from datetime import date, timedelta, datetime

# ── Inicializar BD ─────────────────────────────────────────────────
Base.metadata.create_all(engine)

tm = TaskManager()

# ══════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════

def limpiar():
    print("\n" * 2)

def titulo(texto):
    print("\n" + "=" * 55)
    print(f"  {texto}")
    print("=" * 55)

def subtitulo(texto):
    print(f"\n  ── {texto} ──")

def pedir(pregunta):
    return input(f"  ▶ {pregunta}: ").strip()

def menu(opciones: list) -> int:
    """Muestra opciones numeradas y retorna la elegida."""
    for i, op in enumerate(opciones, 1):
        print(f"     [{i}] {op}")
    while True:
        try:
            eleccion = int(input("  ▶ Elige una opción: "))
            if 1 <= eleccion <= len(opciones):
                return eleccion
            print("  ⚠️  Opción fuera de rango, intenta de nuevo.")
        except ValueError:
            print("  ⚠️  Ingresa un número válido.")

def pausa():
    input("\n  Presiona ENTER para continuar...")

# ══════════════════════════════════════════════════════════
# FLUJO: GESTIÓN DE USUARIOS
# ══════════════════════════════════════════════════════════

def flujo_crear_usuario():
    titulo("👤 CREAR NUEVO USUARIO")
    nombre = pedir("Nombre completo")
    correo = pedir("Correo electrónico")
    try:
        u = tm.crear_usuario(nombre, correo)
        print(f"\n  ✅ Usuario '{u.nombre}' creado correctamente.")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_seleccionar_usuario():
    titulo("🔑 SELECCIONAR USUARIO")
    usuarios = tm.listar_usuarios()
    if not usuarios:
        print("\n  ⚠️  No hay usuarios registrados. Crea uno primero.")
        pausa()
        return False

    subtitulo("Usuarios disponibles")
    for u in usuarios:
        print(f"     [{u.idUsuario}] {u.nombre} — {u.correo}")

    while True:
        try:
            id_sel = int(pedir("Ingresa el ID del usuario"))
            usuario = tm.seleccionar_usuario(id_sel)
            if usuario:
                print(f"\n  ✅ Usuario activo: {tm.usuario_activo.nombre}")
                pausa()
                return True
            else:
                print("  ❌ ID no encontrado, intenta de nuevo.")
        except ValueError as e:
            print(f"  ❌ Error: {e}")

def flujo_editar_usuario():
    titulo("✏️  EDITAR MI USUARIO")
    if not tm.usuario_activo:
        print("\n  ⚠️  Primero selecciona un usuario.")
        pausa()
        return

    print(f"\n  Usuario actual: {tm.usuario_activo.nombre} | {tm.usuario_activo.correo}")
    subtitulo("¿Qué deseas cambiar?")
    opcion = menu(["Nombre", "Correo", "Ambos", "Cancelar"])

    nuevo_nombre = None
    nuevo_correo = None

    if opcion in [1, 3]:
        nuevo_nombre = pedir("Nuevo nombre")
    if opcion in [2, 3]:
        nuevo_correo = pedir("Nuevo correo")
    if opcion == 4:
        return

    try:
        editado = tm.editar_usuario(
            tm.usuario_activo.idUsuario,
            nuevo_nombre=nuevo_nombre or None,
            nuevo_correo=nuevo_correo or None
        )
        print(f"\n  ✅ Usuario actualizado: {editado.nombre} | {editado.correo}")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_eliminar_usuario():
    titulo("🗑️  ELIMINAR MI USUARIO")
    if not tm.usuario_activo:
        print("\n  ⚠️  Primero selecciona un usuario.")
        pausa()
        return

    print(f"\n  ⚠️  Vas a eliminar a: {tm.usuario_activo.nombre}")
    print("  ⚠️  Debes eliminar primero todas tus materias.")
    confirm = pedir("¿Estás seguro? (si/no)")
    if confirm.lower() != "si":
        print("  Operación cancelada.")
        pausa()
        return

    try:
        tm.eliminar_usuario(tm.usuario_activo.idUsuario)
        print("\n  ✅ Usuario eliminado correctamente.")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

# ══════════════════════════════════════════════════════════
# FLUJO: GESTIÓN DE MATERIAS
# ══════════════════════════════════════════════════════════

COLORES = {
    "1": ("#E74C3C", "Rojo"),
    "2": ("#3498DB", "Azul"),
    "3": ("#2ECC71", "Verde"),
    "4": ("#F39C12", "Naranja"),
    "5": ("#9B59B6", "Morado"),
    "6": ("#1ABC9C", "Turquesa"),
    "7": ("#E67E22", "Amarillo"),
}

def elegir_color():
    subtitulo("Elige un color para la materia")
    for k, (hex_, nombre) in COLORES.items():
        print(f"     [{k}] {nombre} ({hex_})")
    while True:
        op = pedir("Color (número)")
        if op in COLORES:
            return COLORES[op][0]
        print("  ⚠️  Opción inválida.")

def flujo_crear_materia():
    titulo("📚 CREAR MATERIA")
    nombre = pedir("Nombre de la materia")
    color = elegir_color()
    try:
        m = tm.crear_materia(nombre, color)
        print(f"\n  ✅ Materia '{m.nombre}' creada con color {m.color}")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_editar_materia():
    titulo("✏️  EDITAR MATERIA")
    materias = tm.listar_usuarios()  # usamos seleccionar_materia via ID
    # Listar materias del usuario activo
    from src.model.modelo import Materia
    from src.model.declarative_base import Session
    session = Session()
    mis_materias = session.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
    session.close()

    if not mis_materias:
        print("\n  ⚠️  No tienes materias creadas.")
        pausa()
        return

    subtitulo("Tus materias")
    for m in mis_materias:
        print(f"     [{m.idMateria}] {m.nombre} | {m.color}")

    try:
        id_m = int(pedir("ID de la materia a editar"))
        subtitulo("¿Qué deseas cambiar?")
        opcion = menu(["Nombre", "Color", "Ambos", "Cancelar"])

        nuevo_nombre = None
        nuevo_color = None
        if opcion in [1, 3]:
            nuevo_nombre = pedir("Nuevo nombre")
        if opcion in [2, 3]:
            nuevo_color = elegir_color()
        if opcion == 4:
            return

        editada = tm.editar_materia(id_m, nuevo_nombre=nuevo_nombre, nuevo_color=nuevo_color)
        print(f"\n  ✅ Materia actualizada: {editada.nombre} | {editada.color}")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_eliminar_materia():
    titulo("🗑️  ELIMINAR MATERIA")
    from src.model.modelo import Materia
    from src.model.declarative_base import Session
    session = Session()
    mis_materias = session.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
    session.close()

    if not mis_materias:
        print("\n  ⚠️  No tienes materias.")
        pausa()
        return

    for m in mis_materias:
        print(f"     [{m.idMateria}] {m.nombre}")

    try:
        id_m = int(pedir("ID de la materia a eliminar"))
        print("  ⚠️  Esto eliminará también todas sus tareas.")
        confirm = pedir("¿Confirmas? (si/no)")
        if confirm.lower() != "si":
            print("  Cancelado.")
            pausa()
            return
        tm.eliminar_materia(id_m)
        print("\n  ✅ Materia y sus tareas eliminadas.")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

# ══════════════════════════════════════════════════════════
# FLUJO: GESTIÓN DE TAREAS
# ══════════════════════════════════════════════════════════

def listar_mis_materias():
    from src.model.modelo import Materia
    from src.model.declarative_base import Session
    session = Session()
    materias = session.query(Materia).filter_by(usuario_id=tm.usuario_activo.idUsuario).all()
    session.close()
    return materias

def listar_mis_tareas():
    from src.model.modelo import Tarea, Materia
    from src.model.declarative_base import Session
    session = Session()
    tareas = session.query(Tarea).join(Materia).filter(
        Materia.usuario_id == tm.usuario_activo.idUsuario
    ).all()
    session.close()
    return tareas

def flujo_crear_tarea():
    titulo("📝 CREAR TAREA")

    materias = listar_mis_materias()
    if not materias:
        print("\n  ⚠️  Primero crea una materia.")
        pausa()
        return

    subtitulo("¿En qué materia?")
    for m in materias:
        print(f"     [{m.idMateria}] {m.nombre}")

    try:
        id_m = int(pedir("ID de la materia"))
    except ValueError:
        print("  ❌ ID inválido.")
        pausa()
        return

    titulo_tarea = pedir("Título de la tarea")
    descripcion = pedir("Descripción (opcional, ENTER para omitir)")

    subtitulo("Prioridad")
    op_prior = menu(["Baja", "Media", "Alta"])
    prioridad = [Prioridad.Baja, Prioridad.Media, Prioridad.Alta][op_prior - 1]

    subtitulo("Fecha de entrega")
    print("     [1] En 3 días")
    print("     [2] En 1 semana")
    print("     [3] En 2 semanas")
    print("     [4] Ingresar fecha manualmente (YYYY-MM-DD)")
    op_fecha = menu(["En 3 días", "En 1 semana", "En 2 semanas", "Fecha manual"])

    if op_fecha == 1:
        fecha = date.today() + timedelta(days=3)
    elif op_fecha == 2:
        fecha = date.today() + timedelta(days=7)
    elif op_fecha == 3:
        fecha = date.today() + timedelta(days=14)
    else:
        while True:
            try:
                fecha_str = pedir("Fecha (YYYY-MM-DD)")
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                break
            except ValueError:
                print("  ⚠️  Formato inválido. Usa YYYY-MM-DD")

    try:
        tarea = tm.crear_tarea(
            titulo=titulo_tarea,
            descripcion=descripcion,
            prioridad=prioridad,
            fecha_entrega=fecha,
            materia_id=id_m
        )
        print(f"\n  ✅ Tarea '{tarea.titulo}' creada")
        print(f"     Prioridad: {tarea.prioridad.value} | Entrega: {tarea.fechaEntrega} | Estado: {tarea.estado.value}")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_ver_tareas():
    titulo("📋 MIS TAREAS")
    tareas = listar_mis_tareas()

    if not tareas:
        print("\n  ⚠️  No tienes tareas creadas.")
        pausa()
        return

    pendientes = [t for t in tareas if t.estado == EstadoTarea.Pendiente]
    completadas = [t for t in tareas if t.estado == EstadoTarea.Completada]

    if pendientes:
        subtitulo("🔴 Pendientes")
        for t in pendientes:
            print(f"     [{t.idTarea}] {t.titulo} | {t.prioridad.value} | Entrega: {t.fechaEntrega}")

    if completadas:
        subtitulo("✅ Completadas")
        for t in completadas:
            print(f"     [{t.idTarea}] {t.titulo} | {t.prioridad.value}")

    pausa()

def flujo_marcar_tarea():
    titulo("✅ MARCAR / DESMARCAR TAREA")
    tareas = listar_mis_tareas()

    if not tareas:
        print("\n  ⚠️  No tienes tareas.")
        pausa()
        return

    for t in tareas:
        estado_icono = "✅" if t.estado == EstadoTarea.Completada else "🔴"
        print(f"     [{t.idTarea}] {estado_icono} {t.titulo}")

    try:
        id_t = int(pedir("ID de la tarea"))
        subtitulo("¿Qué deseas hacer?")
        op = menu(["Marcar como Completada", "Marcar como Pendiente", "Cancelar"])

        if op == 1:
            t = tm.marcar_tarea(id_t)
            print(f"\n  ✅ Tarea marcada como: {t.estado.value}")
        elif op == 2:
            t = tm.desmarcar_tarea(id_t)
            print(f"\n  ✅ Tarea marcada como: {t.estado.value}")
        else:
            print("  Cancelado.")
    except ValueError as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

def flujo_eliminar_tarea():
    titulo("🗑️  ELIMINAR TAREA")
    tareas = listar_mis_tareas()

    if not tareas:
        print("\n  ⚠️  No tienes tareas.")
        pausa()
        return

    for t in tareas:
        print(f"     [{t.idTarea}] {t.titulo} | {t.estado.value}")

    try:
        id_t = int(pedir("ID de la tarea a eliminar"))
        confirm = pedir("¿Confirmas eliminación? (si/no)")
        if confirm.lower() != "si":
            print("  Cancelado.")
            pausa()
            return
        tm.eliminar_tarea(id_t)
        print("\n  ✅ Tarea eliminada correctamente.")
    except (ValueError, TypeError) as e:
        print(f"\n  ❌ Error: {e}")
    pausa()

# ══════════════════════════════════════════════════════════
# MENÚS PRINCIPALES
# ══════════════════════════════════════════════════════════

def menu_materias():
    while True:
        titulo("📚 GESTIÓN DE MATERIAS")
        op = menu([
            "Crear materia",
            "Editar materia",
            "Eliminar materia",
            "Volver al menú principal"
        ])
        if op == 1:
            flujo_crear_materia()
        elif op == 2:
            flujo_editar_materia()
        elif op == 3:
            flujo_eliminar_materia()
        elif op == 4:
            break

def menu_tareas():
    while True:
        titulo("📝 GESTIÓN DE TAREAS")
        op = menu([
            "Ver mis tareas",
            "Crear tarea",
            "Marcar / Desmarcar tarea",
            "Eliminar tarea",
            "Volver al menú principal"
        ])
        if op == 1:
            flujo_ver_tareas()
        elif op == 2:
            flujo_crear_tarea()
        elif op == 3:
            flujo_marcar_tarea()
        elif op == 4:
            flujo_eliminar_tarea()
        elif op == 5:
            break

def menu_usuario():
    while True:
        titulo("👤 GESTIÓN DE USUARIO")
        op = menu([
            "Editar mi usuario",
            "Eliminar mi usuario",
            "Volver al menú principal"
        ])
        if op == 1:
            flujo_editar_usuario()
        elif op == 2:
            flujo_eliminar_usuario()
            if not tm.usuario_activo:
                break
        elif op == 3:
            break

def menu_principal():
    while True:
        usuario_info = f"{tm.usuario_activo.nombre}" if tm.usuario_activo else "Ninguno"
        titulo(f"🎓 GESTOR DE TAREAS ACADÉMICAS\n  Usuario activo: {usuario_info}")

        op = menu([
            "📚 Gestión de Materias",
            "📝 Gestión de Tareas",
            "👤 Gestión de Usuario",
            "🔄 Cambiar de usuario",
            "🚪 Salir"
        ])

        if op == 1:
            menu_materias()
        elif op == 2:
            menu_tareas()
        elif op == 3:
            menu_usuario()
            if not tm.usuario_activo:
                return
        elif op == 4:
            flujo_seleccionar_usuario()
        elif op == 5:
            titulo("👋 ¡Hasta luego!")
            break

# ══════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════

def main():
    titulo("🎓 BIENVENIDO AL GESTOR DE TAREAS ACADÉMICAS")
    print("\n  ¿Qué deseas hacer?")
    op = menu([
        "Crear nuevo usuario",
        "Seleccionar usuario existente",
        "Salir"
    ])

    if op == 1:
        flujo_crear_usuario()
        if tm.listar_usuarios():
            flujo_seleccionar_usuario()
    elif op == 2:
        exito = flujo_seleccionar_usuario()
        if not exito:
            return
    elif op == 3:
        titulo("👋 ¡Hasta luego!")
        return

    if tm.usuario_activo:
        menu_principal()

if __name__ == "__main__":
    main()