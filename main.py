from src.modelo.declarative_base import engine, Base
from datetime import datetime
from src.modelo.modelo import Prioridad

# Carga los modelos (Perfil, Materia, Tarea)
import src.modelo.modelo

# Crea las tablas en db.sqlite
Base.metadata.create_all(engine)

print("Base de datos creada correctamente")

from src.logica.task_manager import TaskManager
from src.modelo.declarative_base import engine, Base
import src.modelo.modelo  # carga los modelos


def inicializar_bd():
    Base.metadata.create_all(engine)


def crear_perfiles_por_defecto(tm: TaskManager):
    perfiles = []
    for nombre in ["Usuario 1", "Usuario 2"]:
        perfil = tm.seleccionar_perfil_por_nombre(nombre)
        if not perfil:
            perfil = tm.crear_perfil(nombre)
        perfiles.append(perfil)
    return perfiles


def mostrar_menu():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Seleccionar Usuario 1")
    print("2. Seleccionar Usuario 2")
    print("0. Salir")

def mostrar_menu_perfil(nombre_perfil):
    print(f"\n=== MENÚ DE {nombre_perfil.upper()} ===")
    print("1. Crear materia")
    print("2. Listar materias")
    print("3. Crear tarea")
    print("0. Volver")



def main():
    inicializar_bd()
    tm = TaskManager()

    # Crear perfiles por defecto
    perfil1 = tm.seleccionar_perfil_por_nombre("Usuario 1") or tm.crear_perfil("Usuario 1")
    perfil2 = tm.seleccionar_perfil_por_nombre("Usuario 2") or tm.crear_perfil("Usuario 2")

    perfiles = {
        "1": perfil1,
        "2": perfil2
    }

    while True:
        mostrar_menu()
        opcion = input("Seleccione un usuario: ")

        if opcion == "0":
            print("Saliendo del programa...")
            break

        if opcion not in perfiles:
            print("Opción inválida")
            continue

        perfil_activo = perfiles[opcion]

        while True:
            mostrar_menu_perfil(perfil_activo.nombre)
            opcion_perfil = input("Seleccione una opción: ")

            if opcion_perfil == "0":
                break

            elif opcion_perfil == "1":
                nombre = input("Nombre de la materia: ")

                try:
                    tm.crear_materia(perfil_activo.idPerfil, nombre)
                    print("Materia creada correctamente")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion_perfil == "2":
                try:
                    materias = tm.listar_materias_por_perfil(perfil_activo.idPerfil)

                    if not materias:
                        print("No hay materias registradas")
                    else:
                        print("\nMaterias:")
                        for m in materias:
                            print(f"- {m.nombre}")
                except ValueError as e:
                    print(f"Error: {e}")
            elif opcion_perfil == "3":
                try:
                    materias = tm.listar_materias_por_perfil(perfil_activo.idPerfil)

                    if not materias:
                        print("No hay materias. Cree una primero.")
                        continue

                    print("\nMaterias disponibles:")
                    for m in materias:
                        print(f"{m.idMateria}. {m.nombre}")

                    materia_id = int(input("Seleccione el ID de la materia: "))

                    titulo = input("Título de la tarea: ")
                    descripcion = input("Descripción: ")

                    print("Prioridad:")
                    print("1. Baja")
                    print("2. Media")
                    print("3. Alta")
                    opcion_prioridad = input("Seleccione prioridad: ")

                    prioridades = {
                        "1": Prioridad.Baja,
                        "2": Prioridad.Media,
                        "3": Prioridad.Alta
                    }

                    if opcion_prioridad not in prioridades:
                        print("Prioridad inválida")
                        continue

                    prioridad = prioridades[opcion_prioridad]

                    fecha_str = input("Fecha de entrega (YYYY-MM-DD) o vacío: ")
                    fecha = None
                    if fecha_str.strip():
                        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

                    tm.crear_tarea(
                        titulo=titulo,
                        descripcion=descripcion,
                        materia_id=materia_id,
                        prioridad=prioridad,
                        fecha=fecha
                    )

                    print("Tarea creada correctamente")

                except ValueError as e:
                    print(f"Error: {e}")
                except Exception:
                    print("Formato de fecha inválido (use YYYY-MM-DD)")

            else:
                print("Opción inválida")


if __name__ == "__main__":
    main()

