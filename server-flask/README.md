# Backend - Plataforma Educativa

Backend de la plataforma educativa desarrollado con Flask y PostgreSQL con integración de IA (Gemini).

## Características Principales

- ✅ Autenticación JWT para profesores y estudiantes
- ✅ Gestión completa de cursos y asignaturas
- ✅ Sistema de tareas, cuestionarios y exámenes
- ✅ **Retroalimentación automática con Gemini AI**
- ✅ **Sistema de recordatorios automáticos**
- ✅ **Notificaciones en tiempo real**
- ✅ API RESTful completa documentada
- ✅ Migraciones de base de datos automatizadas

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip y virtualenv
- API Key de Google Gemini

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
DATABASE_URL=postgresql+psycopg2://postgres:tucontraseña@localhost:5432/Taller_software
JWT_SECRET_KEY=tu-clave-secreta
GEMINI_API_KEY=tu-api-key-de-gemini
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
```

El servidor estará disponible en `http://localhost:5000`

## API Endpoints

### 🔐 Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Iniciar sesión

### 📚 Cursos y Asignaturas (Profesor/Estudiante)
- `GET /api/courses` - Listar todos los cursos
- `GET /api/subjects` - Listar todas las asignaturas
- `GET /api/teacher/<id>/courses` - Cursos de un profesor
- `POST /api/subjects` - Crear asignatura (profesor)
- `POST /api/courses` - Crear curso (profesor)
- `POST /api/course_subjects` - Vincular curso-asignatura (profesor)

### 📝 Tareas y Evaluaciones
- `GET /api/assignments` - Listar tareas (con filtros)
- `GET /api/assignments/<id>` - Detalle de tarea
- `POST /api/assignments` - Crear tarea/examen (profesor)
- `POST /api/assignments/<id>/questions` - Añadir preguntas (profesor)
- `POST /api/assignments/<id>/submit` - Enviar respuestas (estudiante)

### ✅ Calificaciones y Retroalimentación
- `GET /api/teacher/submissions` - Ver todas las entregas (profesor)
- `GET /api/submissions/<id>` - Detalle de entrega
- `POST /api/submissions/<id>/grade` - Calificar (profesor)
- `POST /api/submissions/<id>/ai_feedback` - **Generar feedback con IA** (profesor)

### 🎓 Estudiantes
- `GET /api/student/courses` - Materias asignadas
- `GET /api/student/assignments/pending` - Actividades pendientes
- `GET /api/student/grades` - Todas las calificaciones
- `GET /api/student/submissions/<id>/grade` - Ver calificación específica

### 🔔 Notificaciones
- `GET /api/notifications` - Ver notificaciones
- `POST /api/notifications/create` - Crear recordatorio
- `PATCH /api/notifications/<id>/read` - Marcar como leída

## Estructura del Proyecto

```
server-flask/
├── main.py              # Aplicación principal
├── models.py            # Modelos SQLAlchemy
├── routes.py            # Rutas adicionales
├── ai_service.py        # Servicio de Gemini AI
├── reminder_service.py  # Sistema de recordatorios
├── schemas.py           # Validación con Pydantic
├── manage.py            # CLI para la BD
├── requirements.txt     # Dependencias
├── .env.example        # Variables de entorno ejemplo
└── migrations/         # Migraciones de la BD
```

## Casos de Uso Implementados

### Para Profesores:
- ✅ CU-01: Iniciar sesión
- ✅ CU-02: Seleccionar asignaturas y cursos
- ✅ CU-03: Crear y asignar tareas
- ✅ CU-04: Crear cuestionarios
- ✅ CU-05: Crear exámenes
- ✅ CU-06: Enviar actividades a alumnos
- ✅ CU-07: **Retroalimentación automática con IA**
- ✅ CU-08: Revisar entregas
- ✅ CU-09: Calificar y retroalimentar
- ✅ CU-10: Generar recordatorios

### Para Estudiantes:
- ✅ CU-11: Iniciar sesión
- ✅ CU-12: Consultar materias asignadas
- ✅ CU-13: Revisar actividades pendientes
- ✅ CU-13: Resolver y enviar tareas con confirmación
- ✅ CU-14: Consultar calificaciones
- ✅ CU-15: Recibir recordatorios

## Integración de IA

El sistema utiliza **Google Gemini AI** para:
- 📝 Analizar respuestas de texto abierto
- 💡 Generar retroalimentación constructiva
- 🎯 Sugerir calificaciones automáticas
- 📊 Identificar fortalezas y áreas de mejora

## Sistema de Recordatorios

- ⏰ Verificación automática cada hora
- 📧 Notificaciones 24 horas antes del vencimiento
- 🔔 Alertas de nuevas tareas asignadas
- ✉️ Confirmación automática de entregas

## Desarrollo

- Base de datos: PostgreSQL con SQLAlchemy ORM
- Autenticación: JWT (Flask-JWT-Extended)
- Roles: teacher, student, admin
- Scheduler: APScheduler para tareas automáticas
- IA: Google Gemini Pro

## Próximas Mejoras

- [ ] Sistema de upload/download de archivos
- [ ] Sistema de matrícula de estudiantes
- [ ] Tests unitarios completos
- [ ] Documentación Swagger/OpenAPI
- [ ] Rate limiting y seguridad avanzada

## Soporte

Para problemas o preguntas, crear un issue en el repositorio de GitHub.
