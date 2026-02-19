import sys
import os
from datetime import date

# Agregamos la ruta para encontrar tus módulos
sys.path.append(os.getcwd())

# Importamos tu nueva clase robusta y los Enums necesarios
from src.logic.task_manager import TaskManager
from src.model.modelo import Prioridad, EstadoTarea # Asegúrate de que existan en src/model/modelo.py

def probar_sistema_avanzado():
    print("--- 🧪 INICIANDO ENSAYO DE SISTEMA (MODO PRO) ---\n")
    
    try:
        # 1. Instanciar el gestor
        tm = TaskManager()
        print("✅ Gestor iniciado.")

        # 2. Crear un usuario (o usar uno existente)
        nombre = "Estudiante Avanzado"
        correo = "pro@university.edu"
        
        try:
            usuario = tm.crear_usuario(nombre, correo)
            print(f"✅ Usuario creado: {usuario.nombre} (ID: {usuario.idUsuario})")
        except ValueError as e:
            # Si ya existe, lo buscamos
            print(f"ℹ️ {e} -> Buscando usuario existente...")
            usuario = tm.buscar_usuario_por_correo(correo)
            if not usuario:
                print("❌ Error crítico: No se pudo recuperar el usuario.")
                return

        # 3. Seleccionar usuario (CRUCIAL: Sin esto, tu código lanza error)
        tm.seleccionar_usuario(usuario.idUsuario)
        print(f"✅ Usuario activo: {tm.usuario_activo.nombre}")

        # 4. Crear una MATERIA (Ahora es obligatorio antes de la tarea)
        try:
            materia = tm.crear_materia("Ingeniería de Software", "#FF5733")
            print(f"✅ Materia creada: {materia.nombre} (ID: {materia.idMateria})")
        except ValueError as e:
            print(f"ℹ️ {e}")
            # Buscamos la materia si ya existe (para poder seguir el test)
            # Nota: Esto asume que tienes un método para listar materias o lo sacamos del usuario
            if usuario.materias:
                materia = usuario.materias[0]
                print(f"👉 Usando materia existente: {materia.nombre}")
            else:
                return

        # 5. Crear una TAREA (Con Prioridad y Fecha real)
        try:
            nueva_tarea = tm.crear_tarea(
                titulo="Entrega Final",
                descripcion="Proyecto completo con SQLAlchemy",
                prioridad=Prioridad.Alta, # Usamos el Enum
                fecha_entrega=date(2026, 3, 20), # Usamos objeto date
                materia_id=materia.idMateria
            )
            print(f"✅ Tarea creada: '{nueva_tarea.titulo}' | Prioridad: {nueva_tarea.prioridad.name}")
        except Exception as e:
            print(f"❌ Error al crear tarea: {e}")
            import traceback
            traceback.print_exc()

        print("\n--- 🏁 ENSAYO COMPLETADO ---")

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")

if __name__ == "__main__":
    probar_sistema_avanzado()