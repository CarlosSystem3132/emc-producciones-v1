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
