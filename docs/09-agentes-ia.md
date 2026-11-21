# Agentes de inteligencia artificial

## Principio general

La IA debe funcionar como **asistente comercial supervisado**.

La IA puede:

- Analizar información.
- Clasificar leads.
- Redactar borradores.
- Resumir conversaciones.
- Sugerir acciones.
- Responder consultas frecuentes.
- Preparar propuestas.

La IA no debe:

- Confirmar ventas.
- Modificar precios.
- Aprobar contratos.
- Enviar campañas masivas sin autorización.
- Inventar información comercial.
- Tomar decisiones críticas sin validación humana.

## Agente 1 — Estrategia

### Función

Analiza metas, inventario, rubros, avance comercial y desempeño.

### Tareas

- Analizar metas y objetivos.
- Analizar ocupación y avance.
- Identificar rubros con menor cobertura.
- Identificar zonas con mayor disponibilidad.
- Proponer plan semanal.
- Proponer segmentos prioritarios.
- Sugerir campañas.
- Coordinar instrucciones con otros agentes.

### Nivel de autonomía

Asistido. El administrador aprueba el plan.

## Agente 2 — Prospección

### Función

Busca y organiza empresas potenciales.

### Tareas

- Buscar empresas por rubro.
- Buscar empresas por ciudad o región.
- Buscar empresas en web, Google Maps y redes.
- Detectar duplicados.
- Organizar datos de contacto.
- Proponer asignación de ejecutivo.
- Enviar lista para validación.

### Nivel de autonomía

Asistido. Requiere validación del administrador.

## Agente 3 — Contenido comercial

### Función

Prepara invitaciones y propuestas comerciales.

### Tareas

- Preparar invitación en texto plano.
- Preparar propuesta PDF.
- Personalizar contenido por empresa.
- Incluir información del evento.
- Incluir datos del stand.
- Incluir paquete y beneficios.
- Incluir datos del ejecutivo.
- Generar borrador para revisión.

### Nivel de autonomía

Asistido. Requiere revisión humana antes del envío.

## Agente 4 — Difusión

### Función

Organiza y ejecuta envíos controlados.

### Tareas

- Recibir contenido aprobado.
- Identificar destinatarios.
- Evitar envíos duplicados.
- Organizar envíos por lotes.
- Respetar límites diarios.
- Enviar por Gmail.
- Enviar por WhatsApp.
- Registrar envíos.
- Registrar respuestas.
- Actualizar estado del lead.

### Nivel de autonomía

Semi-automático. Campañas masivas requieren aprobación.

## Agente 5 — Atención y reservas

### Función

Atiende consultas, captura datos y gestiona reservas temporales.

### Tareas

- Responder consultas frecuentes.
- Informar sobre el evento.
- Informar sobre stands y paquetes.
- Solicitar datos de la empresa.
- Crear o actualizar empresa.
- Clasificar interés.
- Asignar ejecutivo.
- Activar bloqueo temporal.
- Notificar al ejecutivo.
- Vigilar expiración.
- Liberar stand expirado.
- Enviar nutrición comercial.

### Datos del ejecutivo utilizados

El Agente 5 debe utilizar los datos de contacto del ejecutivo asignado:

- Nombre del ejecutivo.
- Correo de contacto.
- Número de WhatsApp.
- Especialidad.
- Cargo.

### Eventos que generan notificación

- Nueva empresa asignada.
- Nueva reserva temporal.
- Reserva por expirar.
- Reserva expirada.
- Nueva consulta desde chat.
- Nuevo lead calificado.
- Nueva solicitud de propuesta.
- Seguimiento pendiente.
- Alerta de oportunidad sin actividad.

### Reglas

- El agente debe notificar al ejecutivo asignado.
- Si el ejecutivo está bloqueado, el sistema debe reasignar o escalar al administrador.
- El agente no debe enviar información sensible a terceros.
- El agente debe registrar cada notificación en el historial.

### Nivel de autonomía

Automático para información aprobada. Humano para negociación y venta.

## Base de conocimiento

El chat y los agentes deben usar únicamente información aprobada:

- Información del evento.
- Fecha y lugar.
- Dimensiones de stands.
- Precios y paquetes.
- Beneficios.
- Formas de pago.
- Políticas de reserva.
- Políticas de cancelación.
- Preguntas frecuentes.
- Datos de contacto.