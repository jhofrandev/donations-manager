# Donations Manager

Sistema de gestión de campañas solidarias con seguimiento de tareas para beneficiarios.
Incluye backend en Django + DRF, frontend en Next.js, base de datos PostgreSQL y orquestación con Docker Compose.

---

## Tabla de Contenidos
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelos y relaciones](#modelos-y-relaciones)
- [API y documentación](#api-y-documentación)
- [Gestión de roles y permisos](#gestión-de-roles-y-permisos)
- [Servicio de correo](#servicio-de-correo)
- [Pruebas](#pruebas)
- [Notas adicionales](#notas-adicionales)

---

## Características
- Autenticación JWT (registro/login)
- Gestión de campañas, beneficiarios y tareas
- Permisos por rol (admin/beneficiary)
- Notificaciones por correo al crear o actualizar tareas
- Reordenamiento de tareas por beneficiario
- Documentación interactiva de la API (Swagger)
- Infraestructura dockerizada (backend, frontend, base de datos)
- Variables sensibles gestionadas por `.env`

---

## Requisitos
- Docker y Docker Compose
- (Opcional) Node.js y Python 3.11+ si deseas correr localmente sin Docker

---

## Instalación y ejecución

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/tu_usuario/donations-manager.git
   cd donations-manager
   ```

2. **Configura las variables de entorno:**
   - Copia los archivos `.env.example` a `.env` en los directorios `backend/` y `frontend/` y completa los valores necesarios (ver sección [Variables de entorno](#variables-de-entorno)).

3. **Levanta todos los servicios con Docker Compose:**
   ```sh
   docker compose up --build
   ```
   Esto iniciará:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - Base de datos PostgreSQL

4. **Accede a la documentación de la API:**
   - http://localhost:8000/swagger/

5. **Accede al panel de administración de Django:**
   - http://localhost:8000/admin/

---

## Variables de entorno

### Backend (`backend/.env`)
```
DEBUG=1
SECRET_KEY=tu_clave_secreta
DB_NAME=donations_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EMAIL_HOST=smtp.tuservicio.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@dominio.com
EMAIL_HOST_PASSWORD=tu_password
EMAIL_USE_TLS=True
```

### Frontend (`frontend/.env`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/
```

---

## Estructura del proyecto

```
donations-manager/
│
├── backend/
│   ├── core/
│   ├── donations_backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── .env
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Modelos y relaciones

- **User**: Usuario autenticado (admin o beneficiario)
- **Role**: Relación 1:1 con User, define el tipo de usuario
- **Campaign**: Campaña de donación
- **Beneficiary**: Relación 1:1 con User, pertenece a una campaña
- **Task**: Relacionada a un beneficiario y campaña, tiene estado y orden

---

## API y documentación

- Todos los endpoints están documentados en `/swagger/`.
- Endpoints principales:
  - `/api/auth/` (registro/login)
  - `/api/campaigns/` (CRUD campañas, solo admin)
  - `/api/beneficiaries/` (CRUD beneficiarios, solo admin)
  - `/api/tasks/` (CRUD tareas, admin y beneficiario según permisos)

---

## Gestión de roles y permisos

- Los roles solo pueden ser asignados o modificados desde el admin de Django o directamente en la base de datos.
- Los beneficiarios solo pueden ver y actualizar sus propias tareas.
- Los administradores pueden gestionar campañas, beneficiarios y tareas.

---

## Servicio de correo

- El envío de correos se realiza mediante SMTP.
- Configura los datos de tu proveedor en el archivo `.env` del backend.
- Si el envío de correo falla, la tarea no se crea ni se actualiza (manejo transaccional).

---

## Pruebas

- Los tests automáticos están en `backend/core/tests.py`.
- Para ejecutar los tests:
  ```sh
  docker compose exec backend python manage.py test
  ```

---

## Notas adicionales

- El campo `orden` en las tareas permite reordenarlas manualmente desde el frontend.
- El frontend utiliza Next.js y Tailwind CSS.
- Para desarrollo local sin Docker, instala dependencias con `pip` y `npm` en los respectivos directorios.
