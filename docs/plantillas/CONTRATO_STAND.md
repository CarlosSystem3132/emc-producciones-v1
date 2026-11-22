# Plantilla — Contrato de participación (reserva de stand)

> Documento plantilla. Se firma digitalmente vía enlace tokenizado
> (`POST /reservas/{id}/firmas` → `GET|POST /public/firmas/{token}`).
> Personalizar los campos entre `{{ }}`.

---

## CONTRATO DE PARTICIPACIÓN — EXPOINCO 2027

**Entre:** EMC Producciones («la Organización»)
**Y:** {{empresa}}, representada por {{contacto}} ({{cargo}}) («el Expositor»)

### Objeto

La Organización cede al Expositor el derecho de uso del espacio de exhibición
durante la 1ra Expo Inmobiliaria y Construcción Internacional de El Alto
(EXPOINCO 2027), a realizarse en abril de 2027.

### Espacio contratado

- **Stand / Cancha:** {{stand_codigo}} — {{stand_descripcion}}
- **Zona:** {{stand_zona}}
- **Monto total:** USD {{monto}}
- **Reserva (50%):** USD {{monto_reserva}} — vence el {{fecha_vencimiento}}

### Condiciones

1. La reserva se confirma con el pago del anticipo y la firma de este contrato.
2. El saldo se cancela antes del inicio del evento.
3. El stand reservado no puede transferirse sin autorización escrita.
4. La cancelación voluntaria hasta 60 días antes del evento reintegra el
   anticipo menos costos administrativos; después de esa fecha no hay reintegro.
5. El Expositor autoriza el uso de su marca y fotografías del stand para la
   difusión del evento.

### Firmas

| Organización | Expositor |
|--------------|-----------|
| ______________________ | ______________________ |
| {{ejecutivo}}, {{ejecutivo_cargo}} | {{contacto}}, {{cargo}} |
| Fecha: {{fecha}} | Fecha: {{fecha}} |

**Firma digital:** este documento puede validarse por el hash de consentimiento
registrado en el sistema (token de firma: {{token_firma}}).
