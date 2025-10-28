# Backend - Plataforma Educativa

Backend de la plataforma educativa desarrollado con Flask y PostgreSQL.

## Características Principales

- Autenticación JWT para profesores y estudiantes
- Gestión de cursos y asignaturas
- Sistema de tareas y evaluaciones
- Retroalimentación automática (placeholder para IA)
- API RESTful documentada
- Migraciones de base de datos automatizadas

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip y virtualenv

## Configuración del Entorno

1. Crear y activar entorno virtual:

```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Configurar variables de entorno:

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones:
# DATABASE_URL=postgresql+psycopg2://postgres:tucontraseña@localhost:5432/Taller_software
# JWT_SECRET_KEY=tu-clave-secreta
```

## Base de Datos

1. Asegúrate de tener PostgreSQL instalado y corriendo

2. Crea la base de datos:
```sql
CREATE DATABASE Taller_software;
```

3. Aplica las migraciones:
```bash
flask db upgrade
```

## Ejecutar el Servidor

1. Activar el entorno virtual (si no está activo):
```powershell
.\venv\Scripts\Activate.ps1
```

2. Iniciar el servidor:
```bash
python main.py
# o
flask run
```

El servidor estará disponible en `http://localhost:5000`

## API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login

### Cursos y Asignaturas
- `POST /api/subjects` - Nueva asignatura
- `POST /api/courses` - Nuevo curso
- `POST /api/course_subjects` - Vincular curso-asignatura

### Tareas y Evaluaciones
- `POST /api/assignments` - Crear tarea/examen
- `POST /api/assignments/<id>/questions` - Añadir preguntas
- `POST /api/assignments/<id>/submit` - Enviar respuestas

### Calificaciones
- `POST /api/submissions/<id>/grade` - Calificar
- `POST /api/submissions/<id>/ai_feedback` - Feedback IA

### Notificaciones
- `GET /api/notifications` - Ver notificaciones

## Estructura del Proyecto

```
server-flask/
├── main.py           # Aplicación principal
├── models.py         # Modelos SQLAlchemy
├── manage.py         # CLI para la BD
├── requirements.txt  # Dependencias
├── .env.example     # Variables de entorno ejemplo
└── migrations/      # Migraciones de la BD
```

## Desarrollo

- Las migraciones se manejan con Flask-Migrate
- Autenticación implementada con JWT
- Roles: teacher, student, admin
- Base de datos: PostgreSQL con SQLAlchemy ORM

## Notas

- La BD por defecto es PostgreSQL
- Autenticación via JWTs (Flask-JWT-Extended)
- Endpoint de IA es placeholder - integrar modelo real en producción
- Logs y debugger activos en desarrollo
