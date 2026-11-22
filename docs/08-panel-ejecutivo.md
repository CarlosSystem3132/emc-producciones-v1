# Panel del ejecutivo de ventas

## Objetivo

El panel del ejecutivo debe permitir gestionar su propia base de clientes,
oportunidades, reservas, propuestas, comunicaciones y ventas.

## Permisos

Cada ejecutivo solo puede ver:

- Sus empresas asignadas.
- Sus oportunidades.
- Sus reservas.
- Sus stands asignados.
- Sus campañas.
- Sus reportes personales.

El ejecutivo no puede:

- Crear otros ejecutivos.
- Editar otros ejecutivos.
- Bloquear otros ejecutivos.
- Eliminar otros ejecutivos.
- Cambiar su rol.
- Cambiar su estado.
- Ver la base de clientes de otro ejecutivo.

## Perfil del ejecutivo

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

El número de WhatsApp y correo de contacto serán utilizados por el sistema
para enviar notificaciones comerciales.

## Notificaciones

El ejecutivo debe recibir notificaciones cuando:

- Se le asigna una nueva empresa.
- Se crea una reserva temporal.
- Una reserva está por expirar.
- Una reserva expira.
- Un cliente solicita una propuesta.
- Un lead es calificado.
- Existe un seguimiento pendiente.
- Una oportunidad no tiene actividad.

Los canales de notificación son:

- Panel.
- Correo electrónico.
- WhatsApp.

## Mis clientes

Cada ejecutivo podrá:

- Ver únicamente sus empresas asignadas.
- Registrar nuevas empresas.
- Editar sus empresas.
- Importar empresas desde Excel o CSV.
- Exportar su base de clientes.
- Buscar y filtrar clientes.
- Registrar contactos.
- Crear oportunidades.
- Ver historial comercial.

## Importación de base de clientes

El ejecutivo podrá importar un archivo Excel o CSV con:

- Razón social.
- Rubro.
- Nombre del contacto.
- Correo.
- WhatsApp.
- Teléfono.
- Ciudad.
- Estado.

El sistema debe:

- Asignar automáticamente el ejecutivo que realiza la importación.
- Validar duplicados.
- Permitir revisar duplicados antes de importar.
- Permitir corregir errores.
- Registrar el origen como `carga_ejecutivo`.
- Crear o actualizar contactos.
- Crear oportunidades si corresponde.

## Oportunidades

Debe permitir:

- Ver embudo personal.
- Filtrar por estado, rubro, prioridad y fecha.
- Registrar notas.
- Registrar llamadas.
- Registrar reuniones.
- Programar seguimientos.
- Cambiar estados.
- Ver historial completo.

## Reservas

Debe permitir:

- Ver solicitudes asignadas.
- Ver cronómetro de bloqueo.
- Confirmar reserva.
- Extender reserva.
- Liberar reserva.
- Registrar venta.
- Adjuntar comprobante.
- Adjuntar contrato.
- Ver historial de cambios.

## Comunicación

Debe permitir:

- Enviar invitaciones.
- Solicitar propuesta PDF.
- Revisar propuesta antes de enviar.
- Enviar por Gmail.
- Enviar por WhatsApp.
- Ver historial de envíos.
- Registrar respuestas.

## Reportes personales

Debe permitir:

- Ver ventas totales.
- Ver stands vendidos.
- Ver paquetes vendidos.
- Ver embudo personal.
- Ver avance semanal.
- Exportar reporte individual.