# AGENTS.md — Instrucciones para asistentes de IA

## Contexto del proyecto

Este proyecto pertenece a **EMC Producciones** y corresponde al desarrollo de
una plataforma web comercial para gestionar la captación, atención, seguimiento,
reserva y venta de stands y paquetes de la **Expo Inmobiliaria y Construcción
EMC El Alto 2027**.

El objetivo comercial es alcanzar el **100% de ocupación** de los stands
interiores y espacios exteriores destinados a maquinaria pesada.

## Estado actual del proyecto

El código fuente de la página web pública ya existe y fue reconstruido en Astro.

La página actual incluye:

- Información del evento.
- Plano de stands.
- Paquetes.
- Botón flotante de WhatsApp.
- Estructura visual ya implementada.

Por lo tanto, la IA **no debe reconstruir la página web ni generar un nuevo diseño**.

La IA debe:

- Analizar el código fuente Astro existente.
- Identificar páginas, componentes, layouts, rutas, estilos y librerías.
- Reutilizar la estructura, diseño y componentes existentes.
- Agregar únicamente los módulos faltantes.
- Integrar autenticación, base de datos, panel, formularios, reservas y agentes.
- Proponer cambios antes de modificar archivos importantes.
- Mantener la compatibilidad con el diseño actual.

## Stack técnico aprobado

- Frontend: Astro
- Lenguaje frontend: TypeScript
- Estilos: Tailwind CSS o CSS modular
- Backend: Python 3.11+
- Framework backend: FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy 2.0
- Migraciones: Alembic
- Validaciones: Pydantic v2
- Autenticación: JWT + OAuth2
- Contenedores: Docker y Docker Compose
- Automatizaciones: n8n
- IA: DeepSeek API
- Correo: Gmail API o servicio transaccional
- WhatsApp: WhatsApp Cloud API
- Almacenamiento: MinIO, S3 o almacenamiento compatible
- Control de versiones: Git

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

## Reglas obligatorias de negocio

- El administrador es el único usuario autorizado para crear, editar, bloquear,
  desactivar o eliminar ejecutivos de ventas.
- Cada ejecutivo puede editar únicamente su propio perfil.
- Cada ejecutivo puede cargar y administrar su propia base de clientes.
- Cada ejecutivo solo puede ver sus empresas, leads, reservas y ventas.
- El ejecutivo no puede cambiar su rol, estado ni permisos.
- El número de WhatsApp del ejecutivo será utilizado para notificaciones.
- El correo de contacto del ejecutivo será utilizado para notificaciones.
- Si un ejecutivo tiene registros asociados, debe bloquearse o desactivarse
  en lugar de eliminarse físicamente.
- No modificar precios, descuentos, contratos o condiciones sin autorización.
- No enviar campañas masivas sin aprobación del administrador.
- No confirmar ventas automáticamente.
- No inventar información comercial, precios, disponibilidad ni condiciones.
- No eliminar funcionalidades existentes sin confirmación explícita.
- No subir archivos `.env` ni claves API al repositorio.

## Reglas de desarrollo

- Analizar primero el código fuente Astro existente.
- Identificar componentes, páginas, rutas, estilos y estructura actual.
- Reutilizar la estructura, diseño y componentes existentes.
- Agregar únicamente los módulos faltantes.
- Proponer un plan antes de realizar cambios grandes.
- No modificar archivos sin entender su función.
- Mantener compatibilidad con Astro, Supabase y PostgreSQL.
- Usar TypeScript para lógica de negocio.
- Mantener componentes pequeños, reutilizables y documentados.
- Mantener una sola fuente de verdad en la base de datos.
- Registrar auditoría de acciones críticas.
- Proteger datos personales y comerciales de empresas y contactos.

## Flujo de trabajo con IA

1. Leer primero `AGENTS.md`.
2. Leer `docs/01-objetivos-y-alcance.md`.
3. Leer el documento relacionado con la tarea.
4. Analizar los archivos de código relevantes.
5. Identificar la estructura actual del proyecto.
6. Proponer un plan antes de realizar cambios grandes.
7. Esperar aprobación antes de implementar cambios estructurales.
8. Implementar cambios en una rama Git.
9. Explicar qué archivos fueron modificados y por qué.
10. Actualizar la documentación si cambia una regla de negocio.

## Prioridad actual

La prioridad es implementar el **MVP de la Fase 1**:

- Base de datos central.
- Autenticación y roles.
- Panel de administrador.
- Panel de ejecutivos.
- Gestión de ejecutivos por el administrador.
- Perfil y datos de contacto del ejecutivo.
- Carga de base de clientes por ejecutivo.
- Administración de empresas, contactos y leads.
- Administración de stands, zonas y paquetes.
- Plano interactivo conectado a base de datos.
- Formulario de registro.
- Bloqueo temporal de 30 minutos.
- Liberación automática.
- Notificaciones al ejecutivo.
- Dashboard básico.

Los agentes de IA completos se implementarán después de que la base operativa
esté estable y probada.

## Documentación principal

- `docs/01-objetivos-y-alcance.md`
- `docs/02-requerimientos-funcionales.md`
- `docs/03-arquitectura.md`
- `docs/04-modelo-de-datos.md`
- `docs/05-flujos-comerciales.md`
- `docs/06-reglas-de-reserva.md`
- `docs/07-panel-administrador.md`
- `docs/08-panel-ejecutivo.md`
- `docs/09-agentes-ia.md`
- `docs/10-plan-de-desarrollo.md`
- `docs/11-decisiones-tecnicas.md`
- `docs/12-seguridad-y-privacidad.md`