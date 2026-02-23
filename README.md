# TaskMaster Student - Gestor de Tareas Académicas

## 📋 Descripción General
Sistema de gestión de tareas académicas desarrollado en Python que permite a estudiantes organizar sus pendientes por materias, establecer prioridades y llevar seguimiento de su progreso.

## 🎯 Objetivo de la Aplicación
Facilitar la organización académica mediante un gestor de tareas que permita:
- Crear, editar y eliminar tareas
- Marcar tareas como completadas
- Organizar tareas por materias con colores identificadores
- Filtrar y ordenar tareas por diferentes criterios
- Gestionar múltiples perfiles de usuario

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
3. **Activar entorno virtual**
```bash
# Windows (PowerShell)
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Desinstalar versiones previas de flet (importante)**
```bash
pip uninstall flet flet-desktop flet-core flet-runtime -y
```

5. **Instalar dependencias**
```bash
pip install -r requirements.txt

`base datos rescrito ( opcional)
python -c "from src.model.modelo import Base; from src.logic.task_manager import engine; Base.metadata.create_all(engine)"
```

6. **Ejecutar la aplicación (interfaz gráfica)**
```bash
python ui_taskmaster.py
```

7. **Ejecutar la aplicación (terminal)**
```bash
python run.py
```

## 🧪 Ejecución de Pruebas

### Ejecutar pruebas unitarias
```bash
py -m unittest tests.test_task_manager
```
