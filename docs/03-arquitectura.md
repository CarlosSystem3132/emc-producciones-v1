# Arquitectura del sistema

## Principio de desarrollo

El frontend público ya existe en Astro.

La IA y el desarrollo deben integrar nuevos módulos sobre el código existente,
sin reconstruir la página ni cambiar innecesariamente el diseño actual.

## Stack definitivo

- Frontend: Astro
- Backend: Python + FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy
- Migraciones: Alembic
- Validaciones: Pydantic
- Autenticación: JWT + OAuth2
- Contenedores: Docker y Docker Compose
- Automatizaciones: n8n
- IA: DeepSeek API
- Correo: Gmail API
- WhatsApp: WhatsApp Cloud API
- Almacenamiento: MinIO, S3 o compatible

## Arquitectura general

```text
Empresa interesada
        |
        v
Web pública Astro
- Plano interactivo
- Paquetes
- Formulario
- Chat flotante
- WhatsApp
        |
        v
FastAPI Backend
- Autenticación y roles
- CRM
- Inventario de stands
- Reservas
- Reglas de negocio
- Reportes
        |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
PostgreSQL          n8n                DeepSeek API
Empresas            Correos             Chat
Contactos           WhatsApp            Clasificación
Leads               Recordatorios       Propuestas
Stands              Liberaciones        Prospección asistida
Paquetes            Nutrición
Reservas            Alertas
Actividades
        |
        v
Docker
- Astro
- FastAPI
- PostgreSQL
- n8n
- MinIO / almacenamiento
```

## Responsabilidades

### Astro

Astro será responsable de:

- Página pública.
- Plano interactivo.
- Paquetes.
- Formulario de registro.
- Formulario de reserva.
- Chat flotante.
- Panel privado.
- Consumo de la API FastAPI.

### FastAPI

FastAPI será responsable de:

- Autenticación y autorización.
- Gestión de usuarios y roles.
- Gestión de empresas y contactos.
- Gestión de leads y oportunidades.
- Gestión de stands, zonas y paquetes.
- Gestión de reservas.
- Validación de datos.
- Reglas de negocio.
- Control de inventario.
- Reportes.
- Integración con n8n.
- Integración con DeepSeek.

### PostgreSQL

PostgreSQL será responsable de almacenar:

- Usuarios.
- Empresas.
- Contactos.
- Leads.
- Stands.
- Zonas.
- Paquetes.
- Reservas.
- Comunicaciones.
- Actividades.
- Notificaciones.
- Configuraciones.
- Auditoría.

### n8n

n8n será responsable de automatizaciones y orquestación, no de lógica crítica.

Puede ejecutar:

- Envío de correos.
- Envío de WhatsApp.
- Recordatorios.
- Liberación de reservas expiradas.
- Correos de nutrición.
- Alertas al ejecutivo.
- Integración con Gmail.
- Integración con WhatsApp Business.
- Integración con DeepSeek.
- Notificaciones al ejecutivo asignado.

### Docker

Docker será responsable de:

- Ejecutar Astro.
- Ejecutar FastAPI.
- Ejecutar PostgreSQL.
- Ejecutar n8n.
- Ejecutar almacenamiento de archivos.
- Mantener un entorno reproducible.
- Facilitar el despliegue.

## Reglas de arquitectura

- Astro es exclusivamente frontend.
- FastAPI es el backend principal.
- PostgreSQL es la única fuente de verdad.
- n8n no debe contener lógica de negocio crítica.
- n8n debe ejecutar automatizaciones, integraciones y orquestación.
- FastAPI debe validar permisos, roles y propiedad de registros.
- Docker debe permitir ejecutar todo el sistema localmente.
- Las credenciales no deben estar en el código ni en Docker Compose.
- Las variables sensibles deben manejarse mediante .env y secretos.

## Seguridad

- Autenticación JWT.
- Roles y permisos en FastAPI.
- Control de acceso por ejecutivo.
- Validación con Pydantic.
- Migraciones controladas con Alembic.
- Auditoría de acciones críticas.
- Respaldos automáticos de PostgreSQL.
- Variables sensibles en .env o secretos.
- No exponer claves API en el frontend.