# EMC Producciones — Plataforma Comercial Inteligente

Plataforma web para gestionar la comercialización de stands, paquetes,
reservas, empresas expositoras, oportunidades comerciales y reportes de la
**Expo Inmobiliaria y Construcción EMC El Alto 2027**.

## Objetivo

Centralizar y automatizar el proceso comercial de EMC Producciones para
alcanzar el 100% de ocupación de stands interiores y espacios exteriores
destinados a maquinaria pesada.

## Estado actual

El frontend público ya fue reconstruido en Astro y se encuentra operativo.

Avance de los módulos:

- ✅ Autenticación y roles (JWT).
- ✅ Base de datos central (PostgreSQL + Alembic, 15 tablas).
- ✅ Panel de administrador.
- ✅ Panel de ejecutivos (navegación por rol; cada ejecutivo ve solo lo suyo).
- ✅ Gestión de ejecutivos (solo admin).
- ✅ Perfil y datos de contacto del ejecutivo + cambio de contraseña.
- ✅ Carga de base de clientes por ejecutivo (importación Excel/CSV).
- ✅ CRM comercial (empresas, contactos, leads, embudo).
- ✅ Gestión de stands y paquetes.
- ✅ Plano interactivo conectado a base de datos.
- ✅ Formulario de registro y reserva.
- ✅ Bloqueo temporal de stands y liberación automática.
- ✅ Chat flotante con IA supervisada (DeepSeek + FAQ local).
- ✅ Notificaciones básicas (panel + canales externos vía n8n).
- ✅ Propuestas PDF.
- ✅ Campañas por Gmail y WhatsApp (vía n8n).
- ✅ Secuencias de seguimiento (pasos escalonados con control de frecuencia).
- ✅ Agentes de IA: clasificación de leads, asignación sugerida, resúmenes
  de conversaciones, sugerencias de siguiente acción, prospección asistida
  y alertas inteligentes.
- ✅ Reportes avanzados (ventas por ejecutivo, ocupación por zona, embudo,
  comunicaciones, exportación CSV).
- ✅ Pronóstico de ocupación (velocidad de cierre y proyección a abril 2027).
- ✅ Integración con pagos (registro, confirmación y anulación).
- ✅ Firma digital de contratos (enlace tokenizado + trazabilidad).
- ✅ Integración con facturación (facturas y emisión vía n8n).
- ✅ Panel para patrocinadores (gestión + listado público).

## Stack técnico

- Astro
- TypeScript
- Tailwind CSS o CSS modular
- Supabase
- PostgreSQL
- Supabase Auth
- Supabase Storage
- DeepSeek API
- Gmail API
- WhatsApp Cloud API
- Git

## Estructura del proyecto

```text
expoinco-2027/
├── AGENTS.md
├── README.md
├── docs/
├── public/
├── src/
│   ├── components/
│   ├── layouts/
│   ├── lib/
│   ├── pages/
│   └── styles/
├── .env.example
├── astro.config.mjs
└── package.json
```

## Instalación

```bash
npm install
npm run dev
```

## Variables de entorno

Copiar `.env.example` a `.env` y completar las variables requeridas.

Nunca subir el archivo `.env` al repositorio.

## Documentación

Toda la documentación funcional y técnica se encuentra en la carpeta `docs/`.

## Reglas de desarrollo

- No reconstruir la página web existente.
- Analizar primero el código fuente Astro existente.
- Reutilizar la estructura y diseño actual.
- Agregar únicamente los módulos faltantes.
- Mantener el código modular, tipado y documentado.
- Usar Git para controlar cada cambio.