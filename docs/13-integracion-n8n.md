# Integración con n8n — EMC Producciones

Los flujos de comunicación (Gmail, WhatsApp) y automatizaciones se ejecutan
en **n8n**. La API FastAPI prepara, valida y registra; n8n ejecuta el envío
y confirma el resultado. La lógica de negocio crítica **no** vive en n8n
(docs/03 — Reglas de arquitectura).

## Workflows incluidos (`n8n/`)

| Archivo | Función | Disparador |
|---|---|---|
| `01-comunicaciones.json` | Envía por Gmail o WhatsApp lo que recibe del backend y confirma el estado | Webhook `POST /webhook/comunicaciones` |
| `02-liberacion-reservas.json` | Libera bloqueos de 30 min expirados | Cada 5 minutos |
| `03-recordatorios-reservas.json` | Avisa de reservas por expirar (≤15 min) | Cada 10 minutos |

## Configuración paso a paso

1. **Levanta el stack**: `docker compose up -d` (incluye n8n con
   `docker compose --profile tools up -d`).
2. **Importa los workflows**: n8n → *Workflows* → *Import from file* →
   selecciona cada JSON de `n8n/`.
3. **Variables de entorno de n8n** (Settings → Environment):

   ```
   API_URL=http://api:8000          # dentro de docker compose
   WEBHOOK_SECRET=<mismo valor que en backend/.env>
   WHATSAPP_PHONE_ID=<tu phone number id>
   ```

4. **Credenciales de n8n**:
   - *Gmail API* (OAuth2) para el nodo "Enviar por Gmail".
   - *WhatsApp API* (token de WhatsApp Cloud API) para el nodo "Enviar por WhatsApp".
   - *Header Auth* para los nodos que llaman a la API:
     `Authorization: Bearer <token de admin>` (lo obtienes con
     `POST /api/v1/auth/login`).
5. **Backend** (`backend/.env`):

   ```
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/comunicaciones
   WEBHOOK_SECRET=<secreto_largo_y_aleatorio>
   ```

6. Activa los workflows (toggle *Active*).

## Flujo de una comunicación

1. El panel o una campaña generan la comunicación (`estado: pendiente`).
2. FastAPI renderiza la plantilla y hace POST a `N8N_WEBHOOK_URL` con:
   `{ evento, canal, empresa, contacto, email, whatsapp, contenido }`.
3. n8n envía por Gmail o WhatsApp según `canal`.
4. n8n confirma con `POST /api/v1/webhooks/estado-comunicacion`
   (header `X-Webhook-Secret`) → la comunicación pasa a `enviado`
   (o `entregado` / `leído` / `error` según los callbacks que configures).

Si n8n no responde, la comunicación queda `pendiente` y puede reenviarse:
nunca se pierde (la base de datos es la fuente de verdad).

## Notas de seguridad

- `WEBHOOK_SECRET` debe ser idéntico en n8n y en `backend/.env`, y **no**
  debe subirse a Git.
- El endpoint de confirmación rechaza peticiones sin secreto (401) o si el
  secreto no está configurado (503).
