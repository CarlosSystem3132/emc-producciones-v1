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

El proyecto debe incorporar progresivamente:

- Autenticación y roles.
- Base de datos central.
- Panel de administrador.
- Panel de ejecutivos de ventas.
- Gestión de ejecutivos.
- Perfil y datos de contacto del ejecutivo.
- Carga de base de clientes por ejecutivo.
- CRM comercial.
- Gestión de stands y paquetes.
- Plano interactivo conectado a base de datos.
- Formulario de registro y reserva.
- Bloqueo temporal de stands.
- Chat flotante.
- Notificaciones.
- Propuestas PDF.
- Campañas por Gmail y WhatsApp.
- Agentes de IA.
- Reportes comerciales.

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