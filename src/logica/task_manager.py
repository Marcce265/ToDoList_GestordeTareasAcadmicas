import sqlite3
from src.modelo.task import Materia

class TaskManager:
    def __init__(self):
        # 1. Nos conectamos a la base de datos (creará el archivo si no existe)
        self.conexion = sqlite3.connect('DB.sqlite')
        self.cursor = self.conexion.cursor()
        # 2. Inicializamos las tablas necesarias
        self.crear_tablas()

    def crear_tablas(self):
        """Crea la tabla de materias si no existe aún"""
        query = '''
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            color TEXT NOT NULL
        )
        '''
        self.cursor.execute(query)
        self.conexion.commit()

    def crear_materia(self, nombre, color):
        # --- Validaciones (Igual que antes) ---
        if not nombre:
            raise ValueError("El nombre de la materia es obligatorio")
        if not color:
            raise ValueError("El color es obligatorio")

        # --- Guardar en Base de Datos (SQLite) ---
        try:
            # Insertamos los datos
            self.cursor.execute(
                "INSERT INTO materias (nombre, color) VALUES (?, ?)",
                (nombre, color)
            )
            self.conexion.commit() # Confirmamos el cambio
            
            # Retornamos el objeto para que el test siga pasando
            return Materia(nombre, color)
            
        except sqlite3.Error as e:
            # Si falla la BD, lanzamos error (opcional, pero buena práctica)
            raise Exception(f"Error al guardar en BD: {e}")

    def __del__(self):
        # Cierra la conexión cuando se destruye el objeto (limpieza)
        if hasattr(self, 'conexion'):
            self.conexion.close()