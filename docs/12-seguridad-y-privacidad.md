# Seguridad y privacidad

## Accesos

- Cada usuario debe autenticarse antes de acceder al panel.
- Cada usuario debe tener un rol definido.
- El administrador tiene acceso global.
- Cada ejecutivo solo accede a sus empresas, leads, reservas y ventas.
- Presidencia tiene acceso de lectura a reportes y dashboards.
- Solo el administrador puede crear, editar, bloquear, desactivar o eliminar
  ejecutivos de ventas.

## Datos sensibles

No se deben exponer ni compartir:

- Contraseñas.
- API keys.
- Tokens de WhatsApp.
- Credenciales de Gmail.
- Credenciales de Supabase.
- Datos personales de contactos.
- Contratos con información sensible.
- Bases de datos exportadas.

## Variables de entorno

Usar `.env` para credenciales locales.

El archivo `.env` nunca debe subirse al repositorio.

Usar `.env.example` con nombres de variables, pero sin valores reales.

```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DEEPSEEK_API_KEY=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
WHATSAPP_TOKEN=
```

## Auditoría

El sistema debe registrar:

- Creación o modificación de usuarios.
- Creación o modificación de empresas.
- Cambio de estado de leads.
- Cambio de estado de stands.
- Envío de correos y WhatsApp.
- Generación de propuestas.
- Reservas y extensiones.
- Ventas confirmadas.
- Acciones realizadas por agentes de IA.

## Respaldos

- Respaldos automáticos diarios.
- Exportación periódica a Excel o CSV.
- Registro de errores.
- Plan de recuperación ante fallos.
- Control de versiones de plantillas y documentos.

## Protección contra abuso

- Validación de formularios.
- Protección anti-bots.
- Límites de envío.
- Control de frecuencia.
- Prevención de duplicados.
- Registro de intentos fallidos.