# GUÍA DE DESPLIEGUE — EXPOINCO 2027 (presupuesto cero)

Guía completa para poner en línea la API, conectar n8n desde tu PC, subir la
web a Hostinger y configurar el router de 3 IAs gratuitas. Todo sin tarjeta
de crédito y sin costo, para validar el sistema antes de pedir presupuesto.

**Tiempo estimado:** 2–3 horas la primera vez.

---

## 0. Arquitectura resultante

```
[Hostinger básico]          [Render free]           [Neon free]
 Web Astro (estática)  →    FastAPI (API)      →    PostgreSQL
        ↑                        │
   tus visitantes                │ webhooks (HTTPS)
                                ▼
                     [n8n en tu PC + Cloudflare Tunnel]
                                │
                  Gmail API  /  WhatsApp Cloud API
                                +
                     [Router de IA: Gemini → Groq → OpenRouter]
```

| Pieza | Dónde corre | Costo |
|---|---|---|
| Web (Astro estática) | Hostinger (ya contratado) | $0 |
| API (FastAPI + Docker) | Render — plan free | $0 |
| PostgreSQL | Neon — plan free | $0 |
| n8n | Tu PC (ya instalado) | $0 |
| Túnel n8n | Cloudflare Tunnel | $0 |
| IA (chat, resúmenes) | Gemini + Groq + OpenRouter free | $0 |

**Advertencias del plan free (aceptables para pruebas):**
- Render duerme la API tras 15 min sin uso; la primera petición tarda ~1 min.
- Neon pausa la base tras ~5 min sin uso; se reactiva sola al consultarla.
- Las IAs gratuitas tienen límites diarios; el router rota entre ellas.

---

## 1. Base de datos gratis en Neon (15 min)

1. Entra a **neon.tech** y crea una cuenta gratis (con email; sin tarjeta).
2. Crea un proyecto: nombre `emc-producciones`, región la más cercana
   (ej. us-east-1), PostgreSQL 17.
3. En el panel del proyecto, botón **Connect** → elige **Pooled connection** y
   el driver **Python**. Copia la cadena (empieza con `postgresql://`).
4. Adáptala al formato que usa la API: cambia `postgresql://` por
   `postgresql+psycopg://` y agrega `?sslmode=require` al final.
   Queda así (tus datos serán otros):

```
postgresql+psycopg://neondb:XXXXX@ep-xxxx.aws.neon.tech/neondb?sslmode=require
```

5. **Guárdala**: será la variable `DATABASE_URL` en el Paso 2.

> Alternativa válida: **Supabase** (plan free, 500 MB) — Project → Settings →
> Database → Connection string (URI). Mismo ajuste `postgresql+psycopg://`.

---

## 2. API gratis en Render (30 min)

### 2.1 Crear el servicio

1. Entra a **render.com** y crea una cuenta gratis (email; sin tarjeta).
2. **New → Blueprint** → conecta tu cuenta de GitHub y selecciona el
   repositorio `emc-producciones-v1`.
3. Render lee el archivo `render.yaml` del repositorio y crea el servicio
   `emc-api` automáticamente (plan **Free**). Acepta.

> Si prefieres hacerlo manual: **New → Web Service** → repo → Runtime **Docker** →
> Dockerfile Path `./backend/Dockerfile` → Docker Context `./backend` →
> Plan Free → Start Command:
> `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"`

### 2.2 Configurar las variables de entorno

En **Environment** del servicio, completa:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | la cadena de Neon del Paso 1 |
| `SEED_ADMIN_EMAIL` | tu correo de administrador |
| `SEED_ADMIN_PASSWORD` | una contraseña fuerte (la del admin del panel) |
| `JWT_SECRET` | genera una aleatoria (Render tiene botón «Generate») |
| `WEBHOOK_SECRET` | genera una aleatoria (la usará n8n en el Paso 4) |
| `N8N_WEBHOOK_URL` | la URL del túnel de n8n (Paso 4; puedes dejarla vacía al principio) |
| `IA_GEMINI_KEY` / `IA_GROQ_KEY` / `IA_OPENROUTER_KEY` | Paso 3 |
| `CORS_ORIGINS` | `https://www.expoinmobiliariayconstruccion.com,http://localhost:4321` |

### 2.3 Desplegar y crear los datos

1. **Deploy** → Render construye la imagen y arranca. Las migraciones de
   Alembic corren solas (crean las 22 tablas).
2. Al arrancar se crea el usuario admin automáticamente.
3. Abre **Shell** en Render y ejecuta los datos semilla:

```bash
python -m app.db.seed_plano    # 6 zonas + 52 stands del plano
python -m app.db.seed_demo     # empresas de prueba, leads, plantillas (opcional)
```

4. **Verifica:**
   - `https://emc-api.onrender.com/health` → `{"status":"ok"}`
   - `https://emc-api.onrender.com/docs` → documentación interactiva.
   - `https://emc-api.onrender.com/api/v1/public/plano` → JSON del plano.

---

## 3. Router de IA gratuita (20 min)

El chat usa la cadena **Gemini → Groq → OpenRouter** (y tu DeepSeek como
opción final). Cuando uno agota su cuota diaria, salta al siguiente
automáticamente; si todos fallan, responde la FAQ local.

### 3.1 Crear las 3 API keys (todas gratuitas, sin tarjeta)

| Proveedor | Dónde | Plan |
|---|---|---|
| **Google Gemini** | aistudio.google.com → «Get API key» | Free tier generoso |
| **Groq** | console.groq.com → API Keys | Free (Llama, muy rápido) |
| **OpenRouter** | openrouter.ai → Keys | Modelos `:free` |

1. Crea las tres cuentas y genera una API key en cada una.
2. En Render → Environment, pega cada key en su variable:
   `IA_GEMINI_KEY`, `IA_GROQ_KEY`, `IA_OPENROUTER_KEY`.
3. (Opcional) `DEEPSEEK_API_KEY` si quieres agregar un cuarto proveedor.

Los modelos por defecto ya vienen configurados en `.env.example`
(`gemini-2.5-flash`, `llama-3.3-70b-versatile`,
`meta-llama/llama-3.3-70b-instruct:free`). Puedes cambiarlos con las variables
`IA_GEMINI_MODEL`, `IA_GROQ_MODEL`, `IA_OPENROUTER_MODEL`.

### 3.2 Verificar el router

1. Inicia sesión en el panel (`/admin`) con tu usuario admin.
2. Abre: `https://emc-api.onrender.com/api/v1/ia/estado`
   (con el header `Authorization: Bearer <token>` o desde `/docs`).
3. Debes ver los proveedores con `"situacion": "disponible"`.
4. Prueba el chat flotante en la web: responde una IA y, si un proveedor se
   agota (429), el siguiente toma el relevo solo.

---

## 4. n8n en tu PC + Cloudflare Tunnel (30 min)

Tu API en la nube necesita llegar a tu n8n local. El túnel gratuito de
Cloudflare expone tu n8n con una URL HTTPS pública.

### 4.1 Túnel

1. Descarga **cloudflared** (developers.cloudflare.com → Cloudflare Tunnel →
   «Try Cloudflare Tunnel» / «docker» o instalador según tu sistema).
2. Ejecuta:

```bash
cloudflared tunnel --url http://localhost:5678
```

3. Te dará una URL temporal tipo `https://xxxx-yyyy.trycloudflare.com`.
   **Anótala** (cambia al reiniciar; más abajo hay opción permanente).

### 4.2 Configurar la API

En Render → Environment:

```
N8N_WEBHOOK_URL=https://xxxx-yyyy.trycloudflare.com/webhook/comunicaciones
```

Guarda y redespliega. La API empezará a despachar comunicaciones y
notificaciones a tu n8n.

### 4.3 Importar los flujos y credenciales

1. Abre `https://xxxx-yyyy.trycloudflare.com` (tu n8n).
2. **Workflows → Import from File** y sube los 4 archivos de `n8n/`:
   `01-comunicaciones.json`, `02-liberacion-reservas.json`,
   `03-recordatorios-reservas.json`, `04-notificaciones.json`.
3. Crea las credenciales en n8n:
   - **Gmail API** (Google Cloud Console → OAuth2 Client ID «Desktop») →
     asígnala a los nodos «Enviar por Gmail».
   - **WhatsApp API** (Meta for Developers → WhatsApp → token permanente) →
     asígnala a los nodos «Enviar por WhatsApp». En n8n, variable de entorno
     `WHATSAPP_PHONE_ID` con tu ID de número.
4. En cada flujo, activa el **Active** switch.
5. Configura en n8n la variable `WEBHOOK_SECRET` (el mismo valor que en
   Render) para que los webhooks de confirmación sean aceptados.

### 4.4 Túnel permanente (opcional, recomendado)

La URL `trycloudflare` cambia al reiniciar. Para una URL fija:

1. Crea una cuenta gratis en Cloudflare (dominio opcional).
2. `cloudflared tunnel login` → `cloudflared tunnel create emc-n8n` →
   `cloudflared tunnel route dns emc-n8n n8n.tudominio.com` →
   config `config.yml` con el tunnel id. (Detalles en la docs de Cloudflare.)

### 4.5 Prueba de humo de n8n

Desde Render Shell o cualquier terminal:

```bash
curl -X POST "https://TU-TUNEL.trycloudflare.com/webhook/comunicaciones" \
  -H "Content-Type: application/json" \
  -d '{"evento":"comunicacion.enviar","canal":"whatsapp","whatsapp":"+59170000000","contenido":"Prueba EMC"}'
```

Debes ver el mensaje llegar a n8n (y fallar el envío real solo si las
credenciales aún no están listas — eso es esperado).

---

## 5. Web en Hostinger (20 min)

1. En tu PC, construye la web **apuntando a la API de Render**:

```bash
cd emc-producciones-v1
VITE_API_URL=https://emc-api.onrender.com/api/v1 npm run build
```

2. Se genera la carpeta `dist/` con la web estática.
3. Sube el **contenido** de `dist/` a Hostinger:
   - hPanel → Administrador de archivos → `public_html` (o por FTP).
4. Abre tu dominio: la web debe cargar con el plano interactivo funcionando
   (los datos vienen de la API de Render).
5. Verifica el panel: `https://tudominio.com/admin`.

> Si usas píxeles de publicidad, incluye las variables en el build:
> `PUBLIC_META_PIXEL_ID=... PUBLIC_GTAG_ID=... VITE_API_URL=... npm run build`

---

## 6. Lista de chequeo final

| # | Prueba | Esperado |
|---|---|---|
| 1 | `GET /health` en Render | `{"status":"ok"}` |
| 2 | `/docs` en Render | documentación carga |
| 3 | Web en Hostinger → plano interactivo | muestra 52 stands con estados reales |
| 4 | Registro desde la web | lead aparece en el panel + notificación al ejecutivo |
| 5 | Solicitud de reserva | stand queda «bloqueado_temporal» 30 min |
| 6 | Chat flotante | responde con IA (o FAQ) |
| 7 | `/ia/estado` | proveedores «disponible» |
| 8 | Plantilla → «Subir plantilla en PDF» | extrae el texto |
| 9 | Comunicación de campaña | llega a n8n y n8n confirma al backend |
| 10 | Notificación al ejecutivo | llega por WhatsApp/correo (con n8n activo) |

---

## 7. Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| La primera petición tarda ~1 min | Render duerme el servicio (free) | Normal; opcional: cron gratis (cron-job.org) con ping a `/health` cada 10 min |
| Error CORS desde la web | dominio no permitido | agrega el dominio a `CORS_ORIGINS` en Render |
| `relation ... does not exist` | faltan migraciones | Render Shell: `alembic upgrade head` |
| El chat responde siempre la FAQ | sin keys de IA o todas agotadas | revisa `/ia/estado`; las cuotas se reinician a diario |
| n8n no recibe nada | URL del túnel cambió o flujo inactivo | repite el túnel, actualiza `N8N_WEBHOOK_URL`, verifica «Active» |
| 429 en un proveedor IA | cuota diaria agotada | el router salta al siguiente solo; esperado |
| Login del panel falla | admin no creado | Render Shell: revisa `SEED_ADMIN_EMAIL`; el seed corre solo si no existen admins |

---

## 8. Seguridad (importante)

- Nunca subas `.env` al repositorio; las keys viven solo en Render (variables
  de entorno) y en tu PC (n8n).
- `JWT_SECRET` y `WEBHOOK_SECRET` con valores aleatorios largos.
- Cambia `SEED_ADMIN_PASSWORD` por una contraseña propia antes de exponer.
- El plan free es **solo para validación**: cuando la empresa asigne
  presupuesto, migra a un VPS o plan pago con el **mismo código y el mismo
  `docker-compose.yml`** (ver §9).

---

## 9. Cuando llegue el presupuesto

Todo lo probado se mantiene igual; solo cambia dónde corre:

| Opción | Para qué | Costo aprox. |
|---|---|---|
| VPS (Hetzner/DigitalOcean/OVH) + Coolify | todo junto (API + Postgres + n8n) con `docker compose up -d` | US$ 4–8/mes |
| Render pago | quitar el sleep y sumar ancho de banda | US$ 7+/mes |
| n8n Cloud oficial | n8n administrado, sin túnel ni PC encendida | desde US$ 20/mes |

Pasos de migración: crear el VPS → `git clone` del repo → copiar `.env` de
producción → `docker compose up -d` → apuntar el DNS. **Cero reescritura de
código.**

---

## 10. Resumen de comandos (chuleta)

```bash
# Local — probar como en producción
cd backend && pip install -r requirements.txt
alembic upgrade head && python -m app.db.seed_plano
uvicorn app.main:app --reload

# Frontend — build contra la API de Render
VITE_API_URL=https://emc-api.onrender.com/api/v1 npm run build

# n8n local
cloudflared tunnel --url http://localhost:5678

# Render Shell — datos y migraciones
alembic upgrade head
python -m app.db.seed_plano
python -m app.db.seed_demo
```
