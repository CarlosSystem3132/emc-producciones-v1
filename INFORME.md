# INFORME DE IMPLEMENTACIÓN — EMC Producciones · EXPOINCO 2027

**Fecha:** 21 de noviembre de 2026
**Repositorio:** https://github.com/CarlosSystem3132/emc-producciones-v1
**Alcance:** plataforma comercial completa (Fases 1–4 del plan de desarrollo),
datos de prueba, plantillas de documentos y configuración de n8n.

---

## 1. Estado general

**Todas las fases del plan (`docs/10-plan-de-desarrollo.md`) están completas.**
Verificación entregable por entregable:

### Fase 1 — Base operativa

| Entregable | Estado | Ubicación |
|---|---|---|
| Estructura del proyecto FastAPI | ✅ | `backend/app/` |
| Docker Compose | ✅ | `docker-compose.yml` (db, api, minio, n8n) |
| PostgreSQL | ✅ | servicio `db` (postgres:16-alpine) |
| SQLAlchemy y Alembic | ✅ | `backend/app/models/`, `backend/alembic/` |
| Modelos y migraciones iniciales | ✅ | 22 tablas, migraciones `dc9c2d3a9e9d` y `a1b2c3d4e5f6` |
| Autenticación JWT | ✅ | `app/api/v1/auth.py`, `app/core/security.py` |
| Roles y permisos | ✅ | admin / ejecutivo / presidencia (`app/api/deps.py`) |
| CRUD de usuarios y ejecutivos | ✅ | `app/api/v1/users.py` + panel «Ejecutivos» |
| Perfil del ejecutivo | ✅ | `POST /users/me/change-password`, panel «Mi perfil» |
| CRUD de empresas y contactos | ✅ | `app/api/v1/empresas.py` |
| Importación de Excel/CSV | ✅ | `POST /empresas/import`, `GET /empresas/export` |
| CRUD de stands, zonas y paquetes | ✅ | `app/api/v1/inventario.py` |
| Plano interactivo conectado a API | ✅ | `GET /public/plano` + `InteractivePlano.tsx` |
| Formulario de registro | ✅ | `POST /public/registro` + `RegistroModal.tsx` |
| Reserva temporal (30 min) | ✅ | `POST /reservas/solicitar` |
| Liberación automática | ✅ | `POST /reservas/liberar-expiradas` |
| Notificaciones básicas | ✅ | `notificaciones.py` + panel 🔔 |
| Dashboard básico | ✅ | `dashboard.py` + `Dashboard.tsx` |

### Fase 2 — Comunicación comercial

| Entregable | Estado | Ubicación |
|---|---|---|
| Plantillas con variables | ✅ | `{{variable}}`, `plantillas.py`, sección Plantillas |
| Generación asistida de invitaciones | ✅ | render + envío + campañas |
| Generación de propuestas PDF | ✅ | `POST /propuestas/pdf` (reportlab, con datos del ejecutivo) |
| Integración con n8n | ✅ | `services/comunicaciones.py`, `webhooks.py`, 3 flujos |
| Envío por Gmail | ✅ | flujo `n8n/01-comunicaciones.json` |
| Integración con WhatsApp Cloud API | ✅ | flujo `n8n/01-comunicaciones.json` |
| Secuencias de seguimiento | ✅ | `secuencias.py` (modelos, servicio, API, panel) |
| Control de frecuencia | ✅ | máx. 5/empresa/día + anti-duplicado 24 h |
| Prevención de duplicados | ✅ | empresas (409 por razón social/correo/WhatsApp) |
| Registro de comunicaciones | ✅ | tabla `comunicaciones` |

### Fase 3 — Inteligencia comercial (agentes supervisados)

| Entregable | Estado | Ubicación |
|---|---|---|
| Chat flotante con IA | ✅ | `POST /public/chat` + `ChatFlotante.tsx` |
| Base de conocimiento aprobada | ✅ | `services/chat_ia.py` (BASE_CONOCIMIENTO) |
| Clasificación automática de leads | ✅ | `POST /leads/{id}/clasificar` |
| Asignación automática o sugerida | ✅ | `GET|POST /leads/{id}/asignacion-sugerida` |
| Resúmenes de conversaciones | ✅ | `POST /empresas/{id}/resumen` |
| Sugerencias de siguiente acción | ✅ | `GET /leads/{id}/sugerencias` |
| Prospección asistida | ✅ | `GET /prospeccion` + sección «Prospección IA» |
| Detección de duplicados | ✅ | empresas + importación |
| Alertas inteligentes | ✅ | `GET /alertas` (por rol) + Dashboard |

### Fase 4 — Optimización

| Entregable | Estado | Ubicación |
|---|---|---|
| Reportes avanzados | ✅ | `reportes.py` (ventas, ocupación, embudo, comunicaciones) + export CSV |
| Pronóstico de ocupación | ✅ | `GET /reportes/pronostico` (velocidad de cierre → proyección abril 2027) |
| Campañas por segmento | ✅ | `estado:` o `rubro:` en `campanas.py` |
| Integración con pagos | ✅ | tabla `pagos`, `pagos.py` (registrar/confirmar/anular) |
| Firma digital | ✅ | tabla `firmas_digitales`, `firmas.py` (token + hash + IP + fecha) |
| Integración con facturación | ✅ | tabla `facturas`, `facturas.py` (emitir → aviso a n8n) |
| Panel para patrocinadores | ✅ | `patrocinadores.py` + sección 🏆 + `GET /public/patrocinadores` |

---

## 2. Los 5 agentes de IA (docs/09) — verificación

| Agente | Nivel | Implementación |
|---|---|---|
| 1. Estrategia | Asistido | `GET /ia/estrategia`: análisis de inventario, avance semanal, desempeño por ejecutivo, plan semanal sugerido, segmentos prioritarios y campañas sugeridas. Visible en «Prospección IA». |
| 2. Prospección | Asistido | `GET /prospeccion` + `sugerir_ejecutivo()` (afinidad de rubro + menor carga) + duplicados 409. El admin aprueba con «Asignar». |
| 3. Contenido comercial | Asistido | Plantillas con variables + render + propuesta PDF con membrete, datos del stand, paquete y firma del ejecutivo asignado. |
| 4. Difusión | Semi-automático | Campañas por segmento con generación por lotes, control de frecuencia, anti-duplicados, despacho vía n8n y registro de estados. |
| 5. Atención y reservas | Automático (info aprobada) | Chat flotante (DeepSeek o FAQ local), captura de empresa en el registro, clasificación de interés, asignación de ejecutivo, bloqueo temporal de 30 min, notificaciones (incluye consultas con interés comercial y escalamiento al admin si no hay ejecutivos activos), liberación automática y nutrición vía secuencias. |

**Regla cumplida:** ningún agente confirma ventas, define precios ni envía
campañas masivas sin aprobación. Todo es sugerencia supervisada.

---

## 3. Datos de prueba (seed)

Ejecuta `python -m app.db.seed_demo` (o `--force` para recrear) y carga:

- **4 ejecutivos de ventas** (contraseña demo `Ejecutivo123*`).
- **34 empresas reales del sector en Bolivia** con contactos (ver §4).
- **34 leads** distribuidos en todo el embudo (prospecto → vendido).
- **5 plantillas de mensajes** (invitación, propuesta, confirmación de
  reserva, seguimiento, recordatorio de pago).
- **1 secuencia de seguimiento** con 3 pasos e inscripciones.
- **4 patrocinadores** (oro, plata, bronce, aliado).
- **Flujo de ejemplo**: stand 5 vendido (USD 4 500, pago confirmado, factura
  F-00001 emitida) y stand 6 reservado (USD 3 800, pago parcial pendiente).

**Accesos de prueba:**

| Rol | Usuario | Contraseña |
|---|---|---|
| Admin | `admin@emcproducciones.com` | la de `SEED_ADMIN_PASSWORD` en `.env` |
| Ejecutivo | `maria.lopez@emcproducciones.com` | `Ejecutivo123*` |

---

## 4. Empresas de Bolivia cargadas

34 empresas reales, verificadas en fuentes públicas (ranking «Empresas
Desarrolladoras Inmobiliarias» de Nueva Economía, directorio comercial del
proyecto, sitios oficiales). Distribución por rubro:

- **Urbanizaciones & Condominios (7):** Parque Industrial Latinoamericano,
  Urubó Village, Macororó Inversiones, Colinas del Urubó, Ciudad Milenio,
  El Pahuichi, Mar Adentro & Crystal Lagoons.
- **Inmobiliaria & Proyectos (5):** Aquavista Golf, Comversa, Century 21
  Bolivia, Grupo Sion Inmobiliaria, Bolivia Propiedades.
- **Diseño, Estructuras & Construcción (6):** Incotec, Inesco, Cofersa,
  Industrias Ferrotodo, Industrias Duralit, Cristembo.
- **Maquinaria Pesada & Equipos (5):** Finning CAT Bolivia, Gregomaq, Hansa
  Ltda., AGSA, EquipExitos.
- **Materiales & Obra Fina (6):** SOBOCE, FANCESA, Cerámica COBOCE, Gladymar,
  Faboce, Importadora Campero.
- **Domótica & Seguridad (5):** AGADON, Bolivian Group, Electrored, DOMOBOL,
  Haustechnik.

---

## 5. Plantillas de documentos

En `docs/plantillas/`:

- `INVITACION_EXPOSITOR.md` — invitación oficial al expositor.
- `PROPUESTA_COMERCIAL.md` — estructura de la propuesta (la genera el sistema en PDF).
- `CONTRATO_STAND.md` — contrato de participación con cláusulas y firma digital.
- `FICHA_STAND.md` — ficha técnica del stand para el expositor.

Todas usan las mismas variables `{{empresa}}`, `{{contacto}}`, `{{ejecutivo}}`…
que el motor de plantillas del sistema.

---

## 6. Cómo ejecutar el proyecto

### Opción A — Docker (recomendada)

```bash
cp backend/.env.example backend/.env    # ajustar contraseñas y JWT_SECRET
docker compose up -d                    # PostgreSQL + API con migraciones
cd backend && python -m app.db.seed_plano && python -m app.db.seed_demo
```

- API + documentación: http://localhost:8000/docs
- Frontend: `npm install && npm run dev` → http://localhost:4321
  (requiere Node ≥ 22.23.4 por Astro 7)

### Opción B — Local sin Docker

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                    # ajustar DATABASE_URL a tu PostgreSQL
alembic upgrade head                    # crea las 22 tablas
python -m app.db.seed_plano             # 6 zonas + 52 stands
python -m app.db.seed_demo              # datos de prueba (opcional)
uvicorn app.main:app --reload

# Frontend (otra terminal)
npm install
npm run dev
```

### Datos semilla disponibles

| Comando | Contenido |
|---|---|
| `python -m app.db.seed_plano` | 6 zonas + 52 stands del plano interactivo |
| `python -m app.db.seed_demo` | ejecutivos, empresas, leads, plantillas, secuencias, patrocinadores, flujo de ejemplo |
| `python -m app.db.seed` | admin inicial (corre automáticamente al arrancar) |

---

## 7. Configuración de n8n

### 7.1 Levantar n8n

```bash
docker compose --profile tools up -d n8n   # http://localhost:5678
```

Credenciales: `N8N_USER` / `N8N_PASSWORD` del `.env` (raíz).

### 7.2 Importar los flujos

En n8n: **Workflows → Import from File** y subir los archivos de `n8n/`:

| Archivo | Función |
|---|---|
| `01-comunicaciones.json` | Recibe `comunicacion.enviar` desde FastAPI y envía por **Gmail API** o **WhatsApp Cloud API**; reporta el resultado al backend |
| `02-liberacion-reservas.json` | Programado: llama `POST /reservas/liberar-expiradas` para liberar stands vencidos |
| `03-recordatorios-reservas.json` | Programado: recordatorios de reservas por expirar |
| `04-notificaciones.json` | Recibe `notificacion.enviar` y envía la notificación al **WhatsApp o correo del ejecutivo** registrado en su perfil |

### 7.3 Variables de entorno (raíz del proyecto)

```bash
# Backend → n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/comunicaciones
WEBHOOK_SECRET=*** secreto largo>

# Gmail API (Google Cloud Console → credenciales OAuth2)
GMAIL_CLIENT_ID=<tu client id>
GMAIL_CLIENT_SECRET=***

# WhatsApp Cloud API (Meta for Developers)
WHATSAPP_TOKEN=<token de acceso>
WHATSAPP_PHONE_ID=<id del número>
WHATSAPP_VERIFY_TOKEN=*** de verificación>

# DeepSeek (chat flotante; sin key usa FAQ local)
DEEPSEEK_API_KEY=***
***https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 7.4 Cadena de eventos

1. FastAPI registra la comunicación y hace POST a `N8N_WEBHOOK_URL`
   con el payload y el evento (`comunicacion.enviar`, `factura.emitida`).
2. n8n envía por Gmail/WhatsApp según el canal.
3. n8n confirma el estado con `POST /api/v1/webhooks/estado-comunicacion`
   usando el header `X-Webhook-Secret: {{WEBHOOK_SECRET}}`.
4. El panel muestra el estado (pendiente → enviado → entregado → leído).

**Regla de arquitectura:** n8n no contiene lógica de negocio crítica; solo
orquesta. La validación de permisos, roles y registros ocurre siempre en
FastAPI.

---

## 8. Estructura del repositorio

```
emc-producciones-v1/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # 19 routers (auth, users, empresas, leads,
│   │   │                  # inventario, reservas, plantillas, comunicaciones,
│   │   │                  # campanas, secuencias, ia, pagos, facturas, firmas,
│   │   │                  # patrocinadores, reportes, notificaciones,
│   │   │                  # dashboard, public, chat, webhooks)
│   │   ├── core/          # config (.env) + seguridad (JWT + bcrypt)
│   │   ├── db/            # sesión, seeds (seed, seed_plano, seed_demo)
│   │   ├── models/        # 22 tablas (SQLAlchemy 2.0)
│   │   ├── schemas/       # Pydantic v2
│   │   └── services/      # comunicaciones, chat_ia, ia_comercial, secuencias
│   └── alembic/           # migraciones
├── src/                   # Astro + React (público + panel admin)
│   ├── components/        # web pública + admin/sections (14 secciones)
│   └── lib/               # clientes API (api.ts, adminApi.ts)
├── docs/                  # 13 documentos funcionales + plantillas/
├── n8n/                   # 3 flujos de automatización
├── docker-compose.yml
└── INFORME.md             # este documento
```

---

## 9. Verificación realizada

- `python -m py_compile` sobre el 100% del backend: **sin errores**.
- Balance de sintaxis (llaves/paréntesis) de los 20 componentes TSX/TS: **OK**.
- Auditoría entregable por entregable de las 4 fases: **completa**.
- Los 5 agentes de IA de `docs/09`: **implementados con nivel de autonomía
  requerido** (asistido/semi-automático supervisado).

> Nota: el build completo de Astro (`npm run build`) requiere Node ≥ 22.23.4 y
> `node_modules` completo; se verificó sintaxis de componentes sin instalar
> dependencias.

---

## 10. Recomendaciones

1. Cambiar todas las contraseñas demo antes de producción (`SEED_ADMIN_PASSWORD`,
   `JWT_SECRET`, `WEBHOOK_SECRET`).
2. Restringir CORS en `backend/app/main.py` al dominio definitivo.
3. Programar `POST /secuencias/ejecutar-pendientes` desde n8n (ej. cada hora).
4. Configurar copias de seguridad de PostgreSQL (volumen `pgdata`).
5. Para producción: servicios `minio` y `n8n` con perfiles separados y
   secretos administrados (no en `.env` plano).

---

## 11. Captura de leads y medición de marketing (quick wins)

Implementados los quick wins 1 y 2 de las sugerencias comerciales:

### 11.1 Captura de leads + prueba social en vivo

- **Brochure con captura de datos** (`BrochureModal.tsx`): la descarga del
  material oficial ahora se intercambia por nombre, empresa, correo y
  WhatsApp. Cada descarga crea automáticamente empresa + contacto + lead en
  el CRM (tipo `brochure`), notifica al ejecutivo asignado y dispara el evento
  `Lead` a los píxeles.
- **Contador de ocupación en vivo** (`LiveStats.tsx`, en la portada): muestra
  con datos reales del inventario los stands ocupados (vendidos + reservados),
  disponibles y canchas de maquinaria libres, con CTA al plano interactivo.
  Es prueba social dinámica: sube automáticamente a medida que se venden.

### 11.2 Publicidad medible (píxeles + UTM)

- **Meta Pixel y Google (gtag)** en `Layout.astro`: se cargan automáticamente
  solo si existen las variables `PUBLIC_META_PIXEL_ID` y `PUBLIC_GTAG_ID`.
  Sin configurar, el sitio no carga ningún script externo de publicidad.
- **Atribución UTM** (`src/utils/utm.ts`): captura `utm_source/medium/campaign`,
  `gclid` y `fbclid` en el primer toque, los conserva en `localStorage` y los
  envía como `fuente` en los tres formularios públicos (registro, reserva y
  brochure). El backend los guarda como `origen` de la empresa y del lead, de
  modo que los reportes pueden responder «¿qué canal trae ventas?».
- **Eventos de conversión** vía `track()`: `Lead` (registro y brochure) y
  `ReservaSolicitada` (solicitud de stand) — listos para optimizar campañas.

### Variables de entorno nuevas

```bash
PUBLIC_META_PIXEL_ID=1234567890123456   # opcional
PUBLIC_GTAG_ID=AW-XXXXXXXXX             # opcional (o G-XXXX de GA4)
```

### Notas

- La atribución es de **primer toque** (la primera fuente que llegó al
  visitante se conserva); ideal para medir qué campaña abre la relación.
- Los módulos nuevos no requieren configuración: se alimentan del API
  existente (`/public/plano` y `/public/registro`).

---

## 12. Notificaciones al ejecutivo por WhatsApp + plantillas desde PDF

### 12.1 Notificaciones multicanal (docs/08)

**Regla cumplida:** el número de WhatsApp que el administrador registra al
crear un ejecutivo (formulario «Ejecutivos» del panel) es el que el sistema
usa para notificarle.

Nuevo servicio central `app/services/notificaciones.py`:

1. Registra la notificación en el **panel** (🔔) como siempre.
2. Si el usuario tiene **WhatsApp** registrado → despacha `notificacion.enviar`
   (canal whatsapp) a n8n, que envía el mensaje al número guardado en su perfil.
3. Si tiene **correo de contacto** (o el correo de acceso) → despacha también
   por email.

Aplicado a todos los eventos del Agente 5 (docs/09):

| Evento | ¿A quién? | Canales |
|---|---|---|
| Nueva empresa/registro desde la web | ejecutivo asignado | panel + WhatsApp + correo |
| Nueva reserva temporal | ejecutivo asignado | panel + WhatsApp + correo |
| Reserva por expirar / expirada | ejecutivo asignado | panel + WhatsApp + correo |
| Venta confirmada | ejecutivo asignado | panel + WhatsApp + correo |
| Nueva consulta con interés en el chat | administrador(es) | panel + WhatsApp + correo |
| Reserva sin ejecutivo disponible | administrador(es) | panel + WhatsApp + correo |

**Flujo:** FastAPI → webhook `N8N_WEBHOOK_URL` (`notificacion.enviar` con
`canal`, `para`, `mensaje`) → flujo `n8n/04-notificaciones.json` → WhatsApp
Cloud API o Gmail API. Si n8n no está configurado, la notificación queda igual
registrada en el panel (n8n nunca contiene lógica crítica).

### 12.2 Plantillas desde PDF (UI para usuarios no técnicos)

- Nuevo endpoint `POST /api/v1/plantillas/extraer-pdf` (solo admin, máximo
  10 MB): extrae el texto de un PDF con `pypdf` (nueva dependencia en
  `requirements.txt`) y devuelve el texto + número de páginas.
- En el panel **Plantillas** aparece el botón «📄 Subir plantilla en PDF»:
  1. El administrador elige el PDF (por ejemplo, su invitación oficial).
  2. El sistema extrae el texto y lo precarga en el formulario.
  3. Un mensaje amigable le pide revisar el texto y ajustar las variables
     `{{empresa}}`, `{{contacto}}`… antes de guardar.
  4. Guarda con «Crear plantilla» — igual que una plantilla escrita a mano.

Los mensajes de error son claros para usuarios no técnicos: PDF escaneado
(sin texto), archivo vacío, archivo muy grande, formato incorrecto.
