# Agentes de IA — Flujos, configuración y operación n8n

Documento operativo para administradores y desarrolladores. Describe qué hace
cada agente de IA, cómo se configura desde el panel, qué datos usa, qué
devuelve y cómo fluye la información con n8n.

**Archivos raíz de referencia:** `docs/09-agentes-ia.md` (definición de
negocio), `GUIA-DESPLIEGUE.md` (puesta en línea), este documento (operación).

---

## PARTE 1 — Configuración de los agentes (panel del administrador)

**Ruta del panel:** `Panel → Inteligencia → Agentes IA` (solo administrador).
**Componente:** `src/components/admin/sections/AgentesIA.tsx`
**API:** `backend/app/api/v1/config_agentes.py` → tabla `config_agentes`
(`backend/app/models/config_agente.py`, migración `b3c4d5e6f7a8`).

Cada agente tiene tres controles:

| Control | Qué hace |
|---|---|
| **Prompt del sistema** | Instrucciones que el agente sigue en cada acción. Se edita en el panel y se aplica de inmediato. |
| **Modo de autonomía** | `automatico` / `asistido` / `manual` (ver tabla siguiente). |
| **Agente activo** | Desactivado = el agente no interviene; el sistema usa respuestas locales seguras. |

### Modos de autonomía — comportamiento por agente

| Agente | Automático | Asistido (defecto) | Manual |
|---|---|---|---|
| 1 Estrategia | Entrega plan directamente en el panel | Propone plan semanal; el admin aprueba | Solo análisis básico local |
| 2 Prospección | `clasificar` aplica estado/prioridad solo; `asignar-sugerido` asigna | `clasificar` propone y pide confirmación (`aplicar=true`) | Solo diagnóstico; no aplica cambios (409 si se intenta) |
| 3 Contenido | Genera borradores (resúmenes) automáticamente | Resúmenes a pedido con revisión humana | Solo resumen local sin IA |
| 4 Difusión | Campañas/secuencias se generan sin paso extra | Campañas requieren aprobación del admin (comportamiento actual) | Sin generación asistida |
| 5 Atención | El chat público responde con IA automáticamente | Igual que automático (el chat es siempre supervisado por prompt) | El chat responde solo con la FAQ local (sin modelo) |

**Regla de seguridad del sistema (independiente del modo):** ningún agente
confirma ventas, define precios ni envía campañas masivas sin aprobación del
administrador. El modo regula la iniciativa, nunca las reglas de negocio.

---

## PARTE 2 — Flujo de cada agente

### Agente 1 — Estrategia

| Aspecto | Detalle |
|---|---|
| **Recibe** | Consulta del administrador desde el panel (`Prospección IA`). |
| **Procesa** | `GET /api/v1/ia/estrategia` → `backend/app/api/v1/ia.py` → `backend/app/services/ia_comercial.py::analisis_estrategico` |
| **Extrae datos de** | Tablas `stands`, `zonas` (inventario), `leads`, `empresas`, `reservas`, `usuarios`, `comunicaciones`, `actividades` (SQLAlchemy, `backend/app/models/`). |
| **Cómo lo hace** | Reglas determinísticas: % de ocupación global y por zona, avance de 7 días (leads/empresas/reservas), rubros con menor cobertura, desempeño por ejecutivo. Con eso arma: plan semanal sugerido, segmentos prioritarios y campañas sugeridas. |
| **Reglas** | Zonas «casi agotadas» ≤20% disponibles; plan incluye reactivar leads sin interacción, cerrar reservas temporales, campañas a rubros débiles. El prompt configurado (`estrategia`) acompaña el análisis cuando se usa IA (resúmenes). |
| **Devuelve** | JSON: inventario, avance_semanal, rubros_con_menor_cobertura, desempeno_ejecutivos, plan_semanal_sugerido[], segmentos_prioritarios[], campanas_sugeridas[]. |
| **A quién** | Al administrador, en el panel (`src/components/admin/sections/Prospeccion.tsx`, tarjeta «🧠 Agente de Estrategia»). |
| **Archivos** | `backend/app/api/v1/ia.py`, `backend/app/services/ia_comercial.py`, `src/components/admin/sections/Prospeccion.tsx` |

**Flujo del admin:** Panel → Prospección IA → el agente muestra el plan → el
admin lo ejecuta manualmente (crear campaña en Comunicaciones, inscribir en
Secuencias). En modo *asistido* nada se ejecuta solo.

---

### Agente 2 — Prospección

| Aspecto | Detalle |
|---|---|
| **Recibe** | Acciones del admin/ejecutivo sobre un lead, o consulta de prospección. |
| **Procesa** | `POST /api/v1/leads/{id}/clasificar` · `GET|POST /api/v1/leads/{id}/asignacion-sugerida|asignar-sugerido` · `GET /api/v1/prospeccion` → `backend/app/api/v1/ia.py` → `ia_comercial.py` (`clasificar_lead`, `sugerir_ejecutivo`, `prospeccion_asistida`) |
| **Extrae datos de** | `leads`, `contactos`, `comunicaciones`, `actividades`, `reservas` (clasificación); `usuarios` + `empresas` (asignación); cartera de `empresas` y `stands` (prospección). |
| **Cómo lo hace** | *Clasificación:* puntuación por interés concreto (+2), interacciones 30 días (+1 c/u, máx +3), reserva activa (+2), contacto con canal (+1), propuesta previa (+1) → estado/prioridad sugeridos (nunca retrocede el embudo). *Asignación:* afinidad de rubro vs. `usuarios.especialidad` y menor carga (`count(empresas)`). *Prospección:* rubros con menos empresas, zonas con más stands libres, empresas «dormidas» 21 días + borrador de mensaje. |
| **Reglas** | Duplicados: alta de empresa repetida por razón social/correo/WhatsApp → 409 (`backend/app/api/v1/empresas.py`). Modo `manual` → no aplica cambios. Solo el admin reasigna (docs/07). |
| **Devuelve** | Clasificación: puntuación, estado/prioridad sugeridos, motivos[], apto_para_venta. Asignación: ejecutivo sugerido con afinidad y carga. Prospección: rubros/zonas/empresas a reactivar + borrador. |
| **A quién** | Admin/ejecutivo en el panel: botones «Clasificar», «Sugerencias», «Asignar» en `src/components/admin/sections/Leads.tsx`; prospección en `Prospeccion.tsx`. |
| **Archivos** | `backend/app/api/v1/ia.py`, `backend/app/services/ia_comercial.py`, `src/components/admin/sections/Leads.tsx`, `src/components/admin/sections/Prospeccion.tsx` |

**Flujo del ejecutivo:** Leads → botón «Clasificar» sobre su lead → ve la
puntuación y motivos → si el modo es *asistido*, confirma con «¿Aplicar?» →
se actualiza estado/prioridad. «Asignar» solo funciona para el admin.

---

### Agente 3 — Contenido comercial

| Aspecto | Detalle |
|---|---|
| **Recibe** | Solicitud de propuesta PDF, render de plantilla o resumen de una empresa. |
| **Procesa** | `POST /api/v1/propuestas/pdf` · `POST /api/v1/plantillas/{id}/render|enviar` → `backend/app/api/v1/comunicaciones.py`, `plantillas.py` · `POST /api/v1/empresas/{id}/resumen` → `ia_comercial.py::resumen_conversaciones` |
| **Extrae datos de** | `plantillas` (contenido con variables), `empresas`, `contactos`, `usuarios` (ejecutivo asignado: nombre, cargo, email, WhatsApp), `comunicaciones`, `actividades`. |
| **Cómo lo hace** | Renderiza `{{empresa}}`, `{{contacto}}`, `{{ejecutivo}}`… (`services/comunicaciones.py::renderizar`). La propuesta PDF se dibuja con reportlab (`_crear_pdf`) incluyendo membrete, datos de la empresa y firma del ejecutivo. El resumen: análisis local (conteos por canal, últimos eventos) + narrativo con IA usando el prompt configurado del agente (`texto_ia(..., sistema=prompt)`) solo si el agente está activo y no es *manual*. |
| **Reglas** | Todo es borrador hasta revisión humana. No se inventan precios. La propuesta solo la genera quien administra la empresa (admin o su ejecutivo). |
| **Devuelve** | PDF (`propuesta-*.pdf`), texto renderizado con `variables_faltantes`, o resumen {resumen, origen: ia\|local, comunicaciones, actividades, por_canal}. |
| **A quién** | Al admin/ejecutivo (descarga / panel), y al cliente cuando el humano decide enviarlo (vía Agente 4). |
| **Archivos** | `backend/app/api/v1/comunicaciones.py`, `plantillas.py`, `backend/app/services/comunicaciones.py`, `backend/app/services/chat_ia.py::texto_ia`, `src/components/admin/sections/Comunicaciones.tsx`, `Plantillas.tsx`, `Empresas.tsx` (botón «Resumen IA») |

**Flujo del admin/ejecutivo:** Comunicaciones → «Generar propuesta PDF» →
elige empresa + plantilla → descarga el PDF. Empresas → «Resumen IA» →
recibe el resumen del seguimiento. Plantillas → «Subir plantilla en PDF» →
extrae el texto (`POST /plantillas/extraer-pdf`, pypdf) → revisa → guarda.

---

### Agente 4 — Difusión

| Aspecto | Detalle |
|---|---|
| **Recibe** | Campañas aprobadas del admin y pasos vencidos de secuencias. |
| **Procesa** | `POST /api/v1/campanas/{id}/generar|despachar` (`backend/app/api/v1/campanas.py`) · `POST /api/v1/secuencias/ejecutar-pendientes` (`services/secuencias.py::ejecutar_paso`) · despacho real vía `services/comunicaciones.py::despachar_n8n`. |
| **Extrae datos de** | `campanas` (segmento: `estado:` o `rubro:`), `plantillas`, `empresas`, `contactos`, `secuencias`/`secuencia_pasos`/`secuencia_inscripciones`, `comunicaciones`. |
| **Cómo lo hace** | 1) Genera comunicaciones pendientes para el segmento renderizando plantillas. 2) **Control de frecuencia**: máx. 5 por empresa/día y anti-duplicado 24 h para la misma plantilla+contacto (`validar_frecuencia`). 3) Despacha a n8n con el payload `comunicacion.enviar`. 4) Registra cada comunicación en `comunicaciones` (estado: pendiente → enviado → entregado…). |
| **Reglas** | Campañas masivas solo admin. El límite diario y anti-duplicado no se pueden saltar. n8n solo envía; la lógica vive en FastAPI. |
| **Devuelve** | {generadas, omitidas} por campaña; resultados por pasos de secuencia; registro de cada envío. |
| **A quién** | A los **contactos de las empresas** por Gmail / WhatsApp Cloud API (a través de n8n, flujo `01-comunicaciones.json`). Confirmaciones vuelven al backend por `POST /api/v1/webhooks/estado-comunicacion`. |
| **Archivos** | `backend/app/api/v1/campanas.py`, `comunicaciones.py`, `secuencias.py`, `backend/app/services/comunicaciones.py`, `secuencias.py`, `n8n/01-comunicaciones.json`, `src/components/admin/sections/Comunicaciones.tsx`, `Secuencias.tsx` |

**Flujo del admin:** Comunicaciones → «Crear campaña» (segmento + plantilla +
canal) → «Generar» (crea los envíos pendientes) → «Despachar» (entrega a n8n).
Secuencias → «Inscribir empresa» → «Ejecutar pasos vencidos» (o lo dispara
n8n con un schedule, ver PARTE 3).

---

### Agente 5 — Atención y reservas

| Aspecto | Detalle |
|---|---|
| **Recibe** | Consultas del chat público, formularios de registro/reserva y eventos de vencimiento. |
| **Procesa** | Chat: `POST /api/v1/public/chat` (`backend/app/api/v1/chat.py`) → `services/chat_ia.py::responder_chat` → router `services/ia_router.py`. Registro: `POST /api/v1/public/registro` (`public.py`). Reservas: `POST /api/v1/reservas/solicitar` + `liberar-expiradas` (`reservas.py`). |
| **Extrae datos de** | Base de conocimiento aprobada (`chat_ia.py::BASE_CONOCIMIENTO`), FAQ local, tabla `config_agentes` (prompt y modo del agente), `empresas`/`contactos`/`leads`/`stands`/`reservas`, datos del ejecutivo asignado (`usuarios.whatsapp`, `usuarios.correo_contacto`). |
| **Cómo lo hace** | 1) El chat responde con el prompt configurado vía router de IA (Gemini→Groq→OpenRouter→DeepSeek); si el agente está en modo *manual* o todos los proveedores fallan, responde la FAQ local. 2) Consultas con palabras de interés (reservar, stand, precio…) generan **notificación multicanal** al admin (`services/notificaciones.py`: panel + WhatsApp + correo). 3) El registro crea/actualiza empresa + contacto + lead, asigna ejecutivo (menor carga) y notifica. 4) La reserva bloquea el stand 30 min, notifica al ejecutivo; al expirar, libera el stand y notifica. 5) Si no hay ejecutivos activos, escala al administrador. |
| **Reglas** | No confirma ventas ni precios; siempre sugiere dejar datos con un ejecutivo. Rate limit: 10 consultas/min por IP. Las notificaciones usan SIEMPRE el WhatsApp/correo que el admin registró al crear el ejecutivo (docs/08). |
| **Devuelve** | Chat: {respuesta, origen: ia\|faq}. Registro/Reserva: confirmación + datos de la reserva temporal. Notificaciones: registradas en `notificaciones` y despachadas a n8n (`notificacion.enviar`). |
| **A quién** | Al visitante (chat/formularios); al **ejecutivo asignado** (notificaciones por WhatsApp/correo/panel); al **admin** (consultas con interés y escalamientos). |
| **Archivos** | `backend/app/api/v1/chat.py`, `public.py`, `reservas.py`, `backend/app/services/chat_ia.py`, `ia_router.py`, `notificaciones.py`, `src/components/ChatFlotante.tsx`, `RegistroModal.tsx`, `ReservaModal.tsx`, `BrochureModal.tsx`, `LiveStats.tsx`, `n8n/04-notificaciones.json` |

**Flujo del visitante → ejecutivo:** visitante escribe en el chat «quiero un
stand» → el agente informa y sugiere dejar datos → el sistema notifica al
admin (panel+WhatsApp+correo) → el visitante completa el formulario de
reserva → se crea empresa/lead/reserva temporal → **el ejecutivo asignado
recibe la notificación en su WhatsApp registrado** → confirma, vende o
cancela desde el panel.

---

## PARTE 3 — n8n: configuración, flujos y quién recibe/entrega la información

### Visión

```
FastAPI (Render)                        n8n (tu PC)                    Destinos
──────────────                          ───────────                    ────────
comunicacion.enviar  ──webhook──────▶  01-comunicaciones  ──Gmail───▶  Contacto (email)
notificacion.enviar  ──webhook──────▶  04-notificaciones  ──WhatsApp▶  Ejecutivo/admin
schedule (cada X)    ◀──pull─────────  02-liberacion      ──POST───▶  /reservas/liberar-expiradas
schedule (cada X)    ◀──pull─────────  03-recordatorios   ──WhatsApp▶  Contacto por expirar
                     ◀──confirmación── (01) POST /webhooks/estado-comunicacion
```

**De quién recibe n8n:** exclusivamente del backend FastAPI, vía
`N8N_WEBHOOK_URL` (evento en el campo `evento`) y de schedules propios.
**A quién entrega:** a contactos de empresas (Gmail / WhatsApp Cloud API),
a ejecutivos y administradores (notificaciones), y confirmaciones de vuelta
al backend con el header `X-Webhook-Secret`.

### Cómo levantar n8n

```bash
# Opción A — ya lo tienes instalado local:
n8n start                      # http://localhost:5678

# Opción B — Docker (repo):
docker compose --profile tools up -d n8n
```

Accesible desde internet (necesario para que Render le envíe webhooks):

```bash
cloudflared tunnel --url http://localhost:5678
# → https://xxxx.trycloudflare.com  (pegar en Render: N8N_WEBHOOK_URL)
```

### Los 4 flujos (archivos en `n8n/`)

| Archivo | Recibe | Hace | Entrega |
|---|---|---|---|
| `01-comunicaciones.json` | `POST /webhook/comunicaciones` con `{evento:"comunicacion.enviar", canal, whatsapp, email, contenido, comunicacion_id}` | Rama por canal: Gmail API o WhatsApp Cloud API | Mensaje al **contacto de la empresa**; luego confirma al backend `POST /api/v1/webhooks/estado-comunicacion` (`{comunicacion_id, estado}` + `X-Webhook-Secret`) |
| `02-liberacion-reservas.json` | Schedule interno (cada 5–10 min) | Llama `POST {API_URL}/api/v1/reservas/liberar-expiradas` | Libera stands con bloqueo vencido y notifica al ejecutivo |
| `03-recordatorios-reservas.json` | Schedule interno | Consulta `GET {API_URL}/api/v1/reservas/por-expirar` | Recordatorio por WhatsApp/email al **contacto** antes de que expire el bloqueo |
| `04-notificaciones.json` | `POST /webhook/notificaciones` con `{evento:"notificacion.enviar", canal:"whatsapp"\|"email", para, nombre, mensaje}` | Rama por canal | Mensaje al **ejecutivo/admin** en su `para` (el WhatsApp o correo registrado en su perfil) |

### Configuración paso a paso

1. **Importar:** Workflows → Import from File → los 4 archivos de `n8n/`.
2. **Variables de entorno de n8n** (según cómo lo levantes):
   - `API_URL` = `https://emc-api.onrender.com` (URL base del backend).
   - `WEBHOOK_SECRET` = mismo valor que en Render.
   - `WHATSAPP_PHONE_ID` = ID de tu número de WhatsApp Cloud API.
3. **Credenciales:**
   - *Gmail API*: Google Cloud Console → proyecto → Gmail API → OAuth Client
     (Desktop) → credencial «Gmail API» en n8n → asignar a los nodos Gmail.
   - *WhatsApp API*: Meta for Developers → WhatsApp → token permanente →
     credencial «WhatsApp API» en n8n → asignar a los nodos WhatsApp.
4. **Activar** el switch *Active* de cada flujo.
5. **Probar:** desde Render Shell o terminal:

```bash
curl -X POST "https://TU-TUNEL/webhook/comunicaciones" \
  -H "Content-Type: application/json" \
  -d '{"evento":"comunicacion.enviar","canal":"whatsapp","whatsapp":"+59170000000","contenido":"Prueba EMC"}'
```

### Cadena completa de una campaña (ejemplo)

1. Admin crea campaña (segmento `rubro:cemento`, plantilla «Invitación», canal
   whatsapp) en Comunicaciones → `POST /api/v1/campanas`.
2. «Generar» → `POST /campanas/{id}/generar` → crea comunicaciones
   `pendientes` renderizadas (con frecuencia/anti-duplicados).
3. «Despachar» → `POST /campanas/{id}/despachar` → FastAPI hace POST a
   `N8N_WEBHOOK_URL` (`comunicacion.enviar`) por cada comunicación.
4. n8n `01-comunicaciones` envía por WhatsApp Cloud API al número del contacto.
5. n8n confirma → `POST /webhooks/estado-comunicacion` → la comunicación pasa
   a `enviado`/`entregado`/`error` y se ve en el panel.

---

## Anexo — matriz «quién ve qué»

| Rol | Puede | No puede |
|---|---|---|
| Administrador | Configurar agentes (prompts y modos), todo el CRM, campañas, ejecutivos, patrocinadores, facturas | — |
| Ejecutivo | Sus empresas/leads/reservas, clasificar sus leads, resúmenes, propuestas, plantillas (usar), su perfil, notificaciones | Ver datos de otros ejecutivos, gestionar cuentas, aprobar campañas, configurar agentes |
| Visitante | Chat, registro, reserva temporal, brochure | Acceso al panel |

Ver también: `docs/07-panel-administrador.md`, `docs/08-panel-ejecutivo.md`,
`docs/09-agentes-ia.md`, `GUIA-DESPLIEGUE.md`.
