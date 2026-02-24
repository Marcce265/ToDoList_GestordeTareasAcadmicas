# TaskMaster Student - Gestor de Tareas Académicas

## 📋 Descripción General
Sistema de gestión de tareas académicas desarrollado en Python que permite a estudiantes organizar sus pendientes por materias, establecer prioridades y llevar seguimiento de su progreso.

## 🎯 Objetivo de la Aplicación
Brindar una herramienta que permita a los estudiantes:
- Crear, editar y eliminar tareas
- Marcar tareas como completadas
- Organizar tareas por materias
- Gestionar múltiples perfiles
- Filtrar tareas por estado o prioridad
- Llevar control del progreso académico

## 👥 Integrantes del Equipo
- CHUCHON SOTELO ERNESTO MARCIAL - 74765942
- CARHUAMACA VASQUEZ DIEGO RICARDO - 71624462
- MARIN GUTIERREZ KEVIN GERARD - 77504633
- VILA NAVARRO GRECIA KYARA - 76208115

## 🚀 Instrucciones de Ejecución

### Requisitos Previos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Marcce265/ToDoList_GestordeTareasAcadmicas.git
cd ToDoList_GestordeTareasAcadmicas
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv .venv
```

3. **Configurar PowerShell (solo si aparece error de ejecución)**
```bash
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

4. **Activar entorno virtual**
```bash
# Windows (PowerShell)
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

5. **Desinstalar versiones previas de flet (importante)**
```bash
pip uninstall flet flet-desktop flet-core flet-runtime -y
```

6. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

7. **Crear base de datos (si es necesario)**
```bash
python -c "from src.model.modelo import Base; from src.logic.task_manager import engine; Base.metadata.create_all(engine)"
```

### Ejecutar la Aplicación

**Ejecutar la aplicación (interfaz gráfica)**
```bash
python -m src.view.ui_taskmaster
```

**Ejecutar la aplicación (consola)**
```bash
python run.py
```

## 🧪 Ejecución de Pruebas
**Pruebas unitarias**
```bash
py -m unittest tests.test_task_manager
```

**Ejecutar Pruebas con Cobertura**
```bash
python -m coverage run -m unittest tests.test_task_manager
python -m coverage report
```
