# Backend — EMC Producciones (FastAPI)

API REST del sistema (Fase 1 — Base operativa). Documentación interactiva en `/docs`.

## Requisitos

- Python 3.12+
- PostgreSQL 16 (o Docker)

## Arranque rápido con Docker (recomendado)

Desde la raíz del repositorio:

```bash
cp backend/.env.example backend/.env   # ajusta contraseñas y JWT_SECRET
docker compose up -d                   # PostgreSQL + API con migraciones
```

- API: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Servicios opcionales (Fase 2+): `docker compose --profile tools up -d` (MinIO + n8n).

## Arranque local sin Docker

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                   # ajusta DATABASE_URL a tu PostgreSQL
alembic upgrade head                   # crea el esquema
uvicorn app.main:app --reload
```

## Autenticación

- `POST /api/v1/auth/login` — devuelve JWT (OAuth2 password form o JSON).
- `GET /api/v1/auth/me` — usuario actual.
- Al arrancar se crea el admin inicial si no existe ninguno
  (ver `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` en `.env`).

## Chat flotante (Fase 3 — docs/09)

- `POST /api/v1/public/chat` — asistente virtual supervisado para la web
  pública (sin autenticación, límite de 10 consultas/min por IP).
- Responde con DeepSeek si `DEEPSEEK_API_KEY` está configurada; si no, con la
  base de conocimiento local por palabras clave (el chat nunca queda roto).
- Reglas: no confirma ventas ni precios y siempre deriva con un ejecutivo.

## Gestión de usuarios (solo admin)

- `GET /api/v1/users` — listar (filtros: `rol`, `estado`, `search`).
- `POST /api/v1/users` — crear ejecutivo.
- `PATCH /api/v1/users/{id}` — editar (el ejecutivo solo su perfil, sin rol/estado).
- `POST /api/v1/users/{id}/block|activate|deactivate` — estados.
- `POST /api/v1/users/{id}/reset-password` — restablecer contraseña.
- `DELETE /api/v1/users/{id}` — soft delete; si tiene empresas asignadas
  responde 409 y sugiere reasignar o desactivar (docs/07).

## Empresas y contactos

- `GET|POST /api/v1/empresas` — listar/crear (duplicados por razón social,
  correo y WhatsApp → 409). El ejecutivo solo ve/gestiona las suyas.
- `GET|PATCH|DELETE /api/v1/empresas/{id}` — detalle, edición y soft delete.
- `GET|POST /api/v1/empresas/{id}/contactos` y `PATCH|DELETE .../{contacto_id}`.

## Leads (embudo comercial)

- `GET|POST /api/v1/leads` — filtros por estado, prioridad, rubro, ejecutivo.
- `GET /api/v1/leads/embudo` — conteo por estado.
- `PATCH /api/v1/leads/{id}` — cambios de estado auditados como actividad.

## Inventario (zonas, stands, paquetes)

- `GET|POST /api/v1/inventario/zonas`, `/stands`, `/paquetes` (CRUD admin).
- `PUT /api/v1/inventario/paquetes/{id}/stands/{id}` — asociar stand a paquete.
- Un stand vendido no vuelve a disponible ni se elimina (docs/06).
- `GET /api/v1/public/plano` — disponibilidad para el plano interactivo (sin auth).

## Reservas (docs/06)

- `POST /api/v1/reservas/solicitar` — flujo web público: crea/actualiza empresa,
  contacto y lead, asigna ejecutivo y bloquea el stand 30 minutos.
- `POST /api/v1/reservas/{id}/confirmar` — «Reservado»; detiene el conteo.
- `POST /api/v1/reservas/{id}/extender` — una sola vez, 30 o 60 min, con motivo.
- `POST /api/v1/reservas/{id}/vender` — venta con monto y comprobante.
- `POST /api/v1/reservas/{id}/cancelar` — libera el stand; el lead queda en seguimiento.
- `POST /api/v1/reservas/liberar-expiradas` — liberación automática de bloqueos
  vencidos (también corre al consultar reservas; funciona aunque el usuario
  cierre el navegador).

## Plantillas

- `GET|POST /api/v1/plantillas` — listar/crear (admin crea; ejecutivo usa).
- `POST /api/v1/plantillas/extraer-pdf` — crea el borrador de plantilla desde
  un PDF (extrae el texto; pensado para usuarios no técnicos).
- `POST /api/v1/plantillas/{id}/render` — vista previa con variables.
- `POST /api/v1/plantillas/{id}/enviar` — envío a empresa/contacto con
  control de frecuencia.

## Notificaciones multicanal (docs/08)

- El sistema notifica por **panel + WhatsApp + correo** usando los datos que
  el administrador registró al crear el ejecutivo (WhatsApp y correo).
- Eventos: nuevo registro, reservas (temporal/expiración/venta), consultas de
  chat con interés y escalamientos al administrador.
- Despacho vía n8n (`n8n/04-notificaciones.json`, evento `notificacion.enviar`).

## Secuencias de seguimiento (Fase 2)

- `GET|POST /api/v1/secuencias` — listar/crear secuencias con pasos
  (formato: días de espera + plantilla o mensaje).
- `POST /api/v1/secuencias/{id}/inscribir` — inscribe una empresa/contacto.
- `POST /api/v1/secuencias/ejecutar-pendientes` — ejecuta los pasos vencidos.
- `GET /api/v1/secuencias/inscripciones/listado` — seguimiento de inscripciones.

## Inteligencia comercial (Fase 3 — docs/09)

- `POST /api/v1/leads/{id}/clasificar?aplicar=` — clasificación automática
  (propone estado/prioridad; con `aplicar=true` la aplica).
- `GET /api/v1/leads/{id}/asignacion-sugerida` · `POST .../asignar-sugerido` —
  asignación sugerida por afinidad de rubro y carga (aplicar solo admin).
- `GET /api/v1/leads/{id}/sugerencias` — sugerencias de siguiente acción.
- `POST /api/v1/empresas/{id}/resumen` — resumen de conversaciones
  (extractivo; narrativo con DeepSeek si hay API key).
- `GET /api/v1/prospeccion` — prospección asistida + borrador de mensaje.
- `GET /api/v1/alertas` — alertas inteligentes por rol.

## Reportes y pronóstico (Fase 4)

- `GET /api/v1/reportes/ventas-por-ejecutivo|ocupacion-por-zona|embudo|comunicaciones`.
- `GET /api/v1/reportes/pronostico` — velocidad de cierre y proyección de ocupación.
- `GET /api/v1/reportes/export?tipo=ventas|ocupacion|embudo` — exportación CSV.

## Pagos, facturación y firma digital (Fase 4)

- `POST|GET /api/v1/reservas/{id}/pagos` — registro de pagos;
  `POST /api/v1/pagos/{id}/confirmar|anular`.
- `POST|GET /api/v1/facturas` — facturas;
  `POST /api/v1/facturas/{id}/emitir|anular` (emisión notificada a n8n).
- `POST /api/v1/reservas/{id}/firmas` — solicitud de firma (enlace tokenizado);
  `GET|POST /api/v1/public/firmas/{token}` — consulta y firma del contrato
  (registra hash de consentimiento, IP y fecha).

## Patrocinadores (Fase 4)

- `GET|POST /api/v1/patrocinadores` · `PATCH|DELETE /api/v1/patrocinadores/{id}` (admin).
- `GET /api/v1/public/patrocinadores` — listado público de activos.

## Datos semilla disponibles

| Comando | Contenido | ¿Cuándo usarlo? |
|---|---|---|
| `python -m app.db.seed_plano` | 6 zonas + 52 stands del plano interactivo (inventario real) | Siempre |
| `python -m app.db.seed_empresas` | **134 empresas reales de Bolivia** (prospección) + 5 plantillas operativas. Sin datos simulados: no crea ejecutivos, leads, reservas ni notificaciones | **Producción / poblado real** |
| `python -m app.db.seed_demo` | Datos de demostración (ejecutivos de prueba, leads, reservas, pagos…) | Solo demos / QA, nunca producción |

## Migraciones (Alembic)

```bash
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Seed del plano del pabellón

Crea las 6 zonas y los 52 stands del plano interactivo (códigos `1`–`52`,
que es como `InteractivePlano.tsx` los vincula al mapa):

```bash
python -m app.db.seed_plano
```

## Estructura

```
backend/
├── app/
│   ├── main.py           # FastAPI + CORS + seed
│   ├── core/             # config (.env), seguridad (JWT + bcrypt)
│   ├── db/               # engine, sesión, seed admin
│   ├── models/           # SQLAlchemy 2.0 (15 tablas, docs/04)
│   ├── schemas/          # Pydantic v2
│   └── api/v1/           # auth, users, empresas, leads, inventario, reservas, public
├── alembic/              # migraciones
├── Dockerfile
└── requirements.txt
```

## Configuración de agentes de IA (solo admin)

- `GET /api/v1/config/agentes` — lista los 5 agentes con su prompt y modo.
- `PATCH /api/v1/config/agentes/{clave}` — edita `prompt_sistema`,
  `modo_autonomia` (`automatico | asistido | manual`) y `activo`.
- Claves: `estrategia`, `prospeccion`, `contenido`, `difusion`, `atencion`.
- El modo regula la iniciativa del agente (aplicar cambios solo o a pedido);
  las reglas de negocio (no confirmar ventas, no inventar precios) siempre
  prevalecen. Detalle completo: `docs/14-agentes-ia-flujos.md`.
