import unittest
# Importamos la clase TaskManager desde la ruta correcta
from src.logica.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        # Se ejecuta antes de cada test para tener un gestor limpio
        self.task_manager = TaskManager()

    # --- Test 1: Caso Feliz (Todo correcto) ---
    def test_crear_materia_exitoso(self):
        resultado = self.task_manager.crear_materia("Matemática", "Azul")
        # Esperamos que devuelva el objeto creado con los datos correctos
        self.assertEqual(resultado.nombre, "Matemática")
        self.assertEqual(resultado.color, "Azul")

    # --- Test 2: Caso Infeliz (Nombre vacío) ---
    def test_crear_materia_nombre_vacio(self):
        # Esperamos un error ValueError si el nombre está vacío
        with self.assertRaises(ValueError):
            self.task_manager.crear_materia("", "Verde")

    # --- Test 3: Caso Infeliz (Color vacío) ---
    def test_crear_materia_color_vacio(self):
        # Esperamos un error ValueError si el color está vacío
        with self.assertRaises(ValueError):
            self.task_manager.crear_materia("Física", "")

if __name__ == '__main__':
    unittest.main()