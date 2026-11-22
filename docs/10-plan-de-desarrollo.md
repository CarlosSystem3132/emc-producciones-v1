# Plan de desarrollo e implementación

## Stack definitivo

- Astro para frontend.
- Python + FastAPI para backend.
- PostgreSQL para base de datos.
- SQLAlchemy para ORM.
- Alembic para migraciones.
- Pydantic para validaciones.
- Docker y Docker Compose para contenedores.
- n8n para automatizaciones.
- DeepSeek API para inteligencia artificial.
- Gmail API para correo.
- WhatsApp Cloud API para WhatsApp.

## Principio

El frontend público ya existe en Astro.

El desarrollo debe realizarse por módulos, integrando funcionalidades sobre
el código existente sin reconstruir la página.

## Fase 1 — Base operativa

### Entregables

- Estructura del proyecto FastAPI.
- Docker Compose.
- PostgreSQL.
- SQLAlchemy y Alembic.
- Modelos y migraciones iniciales.
- Autenticación JWT.
- Roles y permisos.
- CRUD de usuarios y ejecutivos.
- Perfil del ejecutivo.
- CRUD de empresas y contactos.
- Importación de Excel/CSV.
- CRUD de stands, zonas y paquetes.
- Plano interactivo conectado a API.
- Formulario de registro.
- Reserva temporal.
- Liberación automática.
- Notificaciones básicas.
- Dashboard básico.

## Fase 2 — Comunicación comercial

### Entregables

- Plantillas con variables.
- Generación asistida de invitaciones.
- Generación de propuestas PDF.
- Integración con n8n.
- Envío por Gmail.
- Integración con WhatsApp Cloud API.
- Secuencias de seguimiento.
- Control de frecuencia.
- Prevención de duplicados.
- Registro de comunicaciones.

## Fase 3 — Inteligencia comercial

### Entregables

- Chat flotante con IA.
- Base de conocimiento aprobada.
- Clasificación automática de leads.
- Asignación automática o sugerida.
- Resúmenes de conversaciones.
- Sugerencias de siguiente acción.
- Prospección asistida.
- Detección de duplicados.
- Alertas inteligentes.

## Fase 4 — Optimización

### Entregables

- Reportes avanzados.
- Pronóstico de ocupación.
- Campañas por segmento.
- Integración con pagos.
- Firma digital.
- Integración con facturación.
- Panel para patrocinadores.
