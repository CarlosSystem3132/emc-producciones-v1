# Decisiones técnicas

## Decisión 1 — Código fuente existente

Ya se cuenta con el código fuente de la página web en Astro.

Por lo tanto, la IA no debe reconstruir la página ni generar un nuevo diseño.

La IA debe analizar el proyecto existente e integrar los módulos faltantes.

## Decisión 2 — Astro como framework principal

Astro fue seleccionado porque:

- La web actual ya fue desarrollada con Astro.
- El sitio público es principalmente informativo.
- Astro permite generar HTML estático y cargar JavaScript solo donde hace falta.
- Permite integrar componentes interactivos para plano, chat y formularios.
- Permite escalar hacia un panel privado.

## Decisión 3 — Supabase como backend inicial

Supabase fue seleccionado porque ofrece:

- Base de datos PostgreSQL.
- Autenticación.
- Almacenamiento de archivos.
- API automática.
- Control de acceso por filas.
- Integración sencilla con Astro.

## Decisión 4 — IA asistida

Los agentes de IA no serán totalmente autónomos.

La IA podrá:

- Analizar.
- Clasificar.
- Redactar.
- Sugerir.
- Responder consultas frecuentes.

El humano deberá:

- Aprobar campañas.
- Validar precios.
- Confirmar contratos.
- Confirmar ventas.
- Validar información sensible.

## Decisión 5 — Gestión de ejecutivos

Solo el administrador puede crear, editar, bloquear, desactivar o eliminar
ejecutivos de ventas.

Cada ejecutivo puede editar únicamente su propio perfil.

Si un ejecutivo tiene registros asociados, debe bloquearse o desactivarse
en lugar de eliminarse físicamente.

## Decisión 6 — Base de clientes por ejecutivo

Cada ejecutivo puede cargar y administrar su propia base de clientes.

El sistema debe validar duplicados y asignar automáticamente el ejecutivo
que realiza la importación.

## Decisión 7 — Notificaciones al ejecutivo

El número de WhatsApp y correo de contacto del ejecutivo serán utilizados
para notificaciones comerciales.

## Decisión 8 — Bloqueo de reserva

El bloqueo inicial de una reserva será de 30 minutos.

El ejecutivo podrá extender la reserva una vez por 30 o 60 minutos
cuando exista negociación activa.

## Decisión 9 — Base de datos única

El Excel dejará de ser la fuente principal de información.

El Excel podrá usarse solo para importación y exportación, pero la base
de datos será la fuente única de verdad.

## Decisión 10 — Control de versiones

Todo el código fuente debe estar versionado en Git desde el inicio.

No se permitirá depender de un único desarrollador sin repositorio,
documentación o respaldos.

## Decisión 11 — Stack backend

Se utilizará Python + FastAPI como backend principal.

FastAPI será responsable de la lógica de negocio, autenticación, permisos,
reglas comerciales, reservas, reportes e integraciones.

## Decisión 12 — PostgreSQL

Se utilizará PostgreSQL como base de datos principal.

PostgreSQL será la única fuente de verdad del sistema.

## Decisión 13 — SQLAlchemy y Alembic

Se utilizará SQLAlchemy 2.0 como ORM.

Se utilizará Alembic para controlar migraciones de base de datos.

## Decisión 14 — Pydantic

Se utilizará Pydantic v2 para validar datos de entrada y salida.

## Decisión 15 — Docker

Se utilizará Docker y Docker Compose para ejecutar el sistema completo
en un entorno reproducible.

Los servicios principales serán:

- Astro.
- FastAPI.
- PostgreSQL.
- n8n.
- Almacenamiento de archivos.

## Decisión 16 — n8n

Se utilizará n8n como motor de automatizaciones.

n8n ejecutará flujos de correo, WhatsApp, recordatorios, nutrición,
liberación de reservas y notificaciones.

n8n no debe contener lógica de negocio crítica.

## Decisión 17 — DeepSeek

Se utilizará DeepSeek API para inteligencia artificial.

DeepSeek será utilizado para chat, clasificación de leads, redacción asistida,
resúmenes y análisis comercial.

La IA no tomará decisiones críticas sin validación humana.