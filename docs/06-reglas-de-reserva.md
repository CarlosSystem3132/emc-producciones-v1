# Reglas de reserva de stands

## Estados del stand

| Estado | Significado | Acción permitida |
|---|---|---|
| Disponible | Espacio abierto a la venta. | Puede ser seleccionado y solicitado. |
| Bloqueado temporal | Reserva web activa por 30 minutos. | Puede confirmarse, extenderse o expirar. |
| Reservado | Negociación activa confirmada por ejecutivo. | Puede avanzar a vendido, liberarse o extenderse. |
| Vendido | Venta confirmada. | No vuelve a estar disponible sin autorización. |
| No disponible | Reservado para patrocinador o uso interno. | No puede reservarse desde la web. |

## Flujo de reserva

1. La empresa selecciona un stand en estado “Disponible”.
2. El sistema muestra detalles, dimensiones, precio y paquetes.
3. La empresa presiona “Reservar este stand”.
4. El sistema solicita datos empresariales y de contacto.
5. El sistema crea o actualiza el registro de empresa.
6. El sistema crea una oportunidad comercial.
7. El sistema asigna un ejecutivo.
8. El stand pasa a “Bloqueado temporal”.
9. El sistema inicia un conteo de 30 minutos.
10. El ejecutivo recibe notificación inmediata por panel, correo y WhatsApp.
11. Si el ejecutivo inicia negociación, cambia el estado a “Reservado”.
12. Al cambiar a “Reservado”, se detiene el conteo de 30 minutos.
13. Si la venta se concreta, el ejecutivo cambia el estado a “Vendido”.
14. Si expiran los 30 minutos sin acción, el stand vuelve a “Disponible”.
15. El sistema envía un correo de nutrición a la empresa.
16. La oportunidad permanece registrada para seguimiento posterior.

## Regla de extensión

El ejecutivo podrá extender una reserva cuando exista negociación activa.

- Extensión sugerida: 30 o 60 minutos adicionales.
- Solo se permite una extensión por reserva.
- Debe registrarse quién extendió y por qué.
- La extensión debe quedar visible en el historial.

## Reglas de integridad

- Un stand no puede tener más de una reserva activa.
- Un stand vendido no puede volver a estar disponible sin autorización.
- Un stand bloqueado no puede ser seleccionado por otra empresa.
- La liberación automática debe ejecutarse aunque el usuario cierre el navegador.
- El sistema debe registrar la hora exacta de inicio y expiración.
- El sistema debe registrar quién cambió cada estado.

## Notificaciones

El ejecutivo debe recibir notificación cuando:

- Se crea una reserva temporal.
- La reserva está por expirar.
- La reserva expira.
- La reserva es confirmada.
- La reserva es vendida.

La empresa debe recibir notificación cuando:

- Su solicitud es registrada.
- Su reserva expira.
- Se confirma la reserva.
- Se confirma la venta.