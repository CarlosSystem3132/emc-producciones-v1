# Requerimientos funcionales

## Módulo público

La web pública debe permitir:

- Mostrar información del evento.
- Mostrar fecha, lugar y horarios.
- Mostrar plano interactivo de stands.
- Mostrar zonas y tipos de espacios.
- Mostrar paquetes disponibles.
- Mostrar beneficios de cada paquete.
- Mostrar precios públicos cuando corresponda.
- Permitir seleccionar un stand disponible.
- Mostrar detalles del stand seleccionado.
- Permitir completar un formulario de registro.
- Permitir solicitar una propuesta.
- Permitir solicitar reserva de un stand.
- Mostrar chat flotante.
- Mostrar botón de WhatsApp.
- Mostrar botón de ingreso al panel.

## Módulo de autenticación

El sistema debe permitir:

- Inicio de sesión con correo y contraseña.
- Recuperación de contraseña.
- Roles diferenciados.
- Control de acceso por rol.
- Sesiones seguras.
- Cierre de sesión.

## Roles

- Administrador.
- Ejecutivo de ventas.
- Presidencia.
- Cliente potencial.

## Reglas de usuarios

- Solo el administrador puede crear ejecutivos de ventas.
- Solo el administrador puede editar ejecutivos de ventas.
- Solo el administrador puede bloquear ejecutivos de ventas.
- Solo el administrador puede desactivar ejecutivos de ventas.
- Solo el administrador puede eliminar ejecutivos de ventas.
- Solo el administrador puede cambiar roles.
- Solo el administrador puede restablecer contraseñas.
- Cada ejecutivo puede editar únicamente su propio perfil.
- El ejecutivo no puede cambiar su rol, estado ni permisos.
- El número de WhatsApp del ejecutivo será utilizado para notificaciones.
- El correo de contacto del ejecutivo será utilizado para notificaciones.

## Módulo de perfil del ejecutivo

Cada ejecutivo debe poder registrar y editar:

- Nombre completo.
- Número de contacto.
- Número de WhatsApp.
- Correo de contacto.
- Cargo.
- Experiencia profesional.
- Especialidad comercial.
- Foto de perfil.
- Contraseña.

El ejecutivo no puede cambiar:

- Su rol.
- Su estado.
- Sus permisos.
- La asignación de otros ejecutivos.

## Módulo de empresas

El sistema debe permitir:

- Registrar empresas.
- Editar empresas.
- Buscar empresas.
- Filtrar empresas por rubro, estado, ciudad y ejecutivo.
- Importar empresas desde Excel o CSV.
- Exportar empresas a Excel o CSV.
- Registrar contactos por empresa.
- Asignar ejecutivo responsable.
- Registrar historial de actividades.
- Evitar duplicados.

## Base de clientes por ejecutivo

Cada ejecutivo podrá:

- Registrar empresas propias.
- Importar empresas desde Excel o CSV.
- Ver únicamente sus empresas asignadas.
- Editar sus empresas.
- Exportar su base de clientes.
- Registrar contactos.
- Crear oportunidades.
- Ver historial comercial.

El sistema debe validar duplicados por:

- Razón social.
- Nombre comercial.
- Correo electrónico.
- Número de WhatsApp.

## Módulo de leads y oportunidades

El sistema debe permitir:

- Crear oportunidades comerciales.
- Asignar prioridad.
- Asignar ejecutivo.
- Registrar origen del lead.
- Registrar rubro.
- Registrar interés.
- Registrar paquete de interés.
- Registrar stand de interés.
- Cambiar estado comercial.
- Registrar notas y actividades.
- Programar seguimientos.
- Ver embudo comercial.

## Estados de lead

- Prospecto.
- Contactado.
- Interesado.
- Propuesta enviada.
- En negociación.
- Reserva temporal.
- Reservado.
- Vendido.
- Descartado.

## Módulo de stands

El sistema debe permitir:

- Registrar zonas.
- Registrar stands.
- Definir código, tipo, dimensiones y precio.
- Definir descripción.
- Definir estado.
- Asignar ejecutivo responsable.
- Ver disponibilidad en tiempo real.
- Ver historial de reservas y ventas.
- Evitar doble reserva.

## Estados de stand

- Disponible.
- Bloqueado temporal.
- Reservado.
- Vendido.
- No disponible.

## Módulo de paquetes

El sistema debe permitir:

- Crear paquetes.
- Editar paquetes.
- Definir beneficios.
- Definir precios.
- Definir condiciones.
- Asociar paquetes a stands o zonas.
- Ver paquetes más solicitados y vendidos.

## Módulo de reservas

El sistema debe permitir:

- Solicitar reserva desde la web.
- Crear registro de empresa.
- Crear oportunidad comercial.
- Asignar ejecutivo.
- Bloquear stand por 30 minutos.
- Notificar al ejecutivo.
- Permitir extender reserva.
- Permitir confirmar reserva.
- Permitir registrar venta.
- Liberar automáticamente stands expirados.

## Módulo de comunicaciones

El sistema debe permitir:

- Crear plantillas de correo.
- Crear plantillas de WhatsApp.
- Crear plantillas de propuestas.
- Personalizar contenido con variables.
- Enviar correos individuales.
- Enviar campañas por lotes.
- Evitar envíos duplicados.
- Registrar envíos y respuestas.
- Enviar correos de nutrición.

## Módulo de chat

El sistema debe permitir:

- Atender consultas desde el chat flotante.
- Responder preguntas frecuentes.
- Informar sobre el evento.
- Informar sobre stands y paquetes.
- Solicitar datos de la empresa.
- Crear o actualizar registros de empresa.
- Asignar ejecutivo.
- Transferir conversación a ejecutivo.
- Guardar historial completo.

## Módulo de notificaciones

El sistema debe notificar al ejecutivo asignado mediante:

- Panel.
- Correo electrónico.
- WhatsApp.

Eventos que generan notificación:

- Nueva empresa asignada.
- Nueva reserva temporal.
- Reserva por expirar.
- Reserva expirada.
- Nueva consulta desde chat.
- Nuevo lead calificado.
- Nueva solicitud de propuesta.
- Seguimiento pendiente.
- Alerta de oportunidad sin actividad.

## Módulo de reportes

El sistema debe permitir:

- Ver ocupación global.
- Ver ventas totales.
- Ver ventas por ejecutivo.
- Ver ventas por paquete.
- Ver ventas por rubro.
- Ver embudo comercial.
- Ver reservas activas y expiradas.
- Ver avance semanal.
- Exportar reportes.

## Módulo de configuración

El administrador debe poder configurar:

- Usuarios y roles.
- Zonas y stands.
- Precios.
- Paquetes.
- Reglas de asignación.
- Plantillas.
- Límites de envío.
- Horarios de campañas.
- Duración del bloqueo temporal.
- Información aprobada para el chat.