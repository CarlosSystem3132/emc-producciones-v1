# Modelo de datos

## Principio general

La base de datos será la única fuente de verdad del sistema.

El Excel podrá utilizarse solo para importación y exportación, pero no como
sistema principal de gestión.

## Tabla: usuarios

La tabla `usuarios` almacenará administradores, ejecutivos de ventas
y usuarios de presidencia.

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| nombre_completo | text | Nombre completo. |
| email | text | Correo de acceso. |
| telefono | text | Teléfono principal. |
| whatsapp | text | Número de WhatsApp para notificaciones. |
| correo_contacto | text | Correo para notificaciones comerciales. |
| cargo | text | Cargo del usuario. |
| experiencia | text | Experiencia profesional. |
| especialidad | text | Rubro o especialidad comercial. |
| foto_url | text | Foto de perfil. |
| rol | text | admin, ejecutivo, presidencia. |
| estado | text | activo, bloqueado, inactivo. |
| creado_por | UUID | Administrador que creó la cuenta. |
| created_at | timestamp | Fecha de creación. |
| updated_at | timestamp | Fecha de última actualización. |

## Reglas de usuarios

- Solo el administrador puede crear ejecutivos.
- Solo el administrador puede editar ejecutivos.
- Solo el administrador puede bloquear ejecutivos.
- Solo el administrador puede desactivar ejecutivos.
- Solo el administrador puede eliminar ejecutivos.
- Solo el administrador puede cambiar roles.
- Solo el administrador puede restablecer contraseñas.
- El ejecutivo puede editar únicamente su propio perfil.
- El ejecutivo no puede cambiar su rol ni estado.
- El número de WhatsApp del ejecutivo será utilizado para notificaciones.
- El correo de contacto del ejecutivo será utilizado para notificaciones.
- Si un ejecutivo tiene registros asociados, debe bloquearse o desactivarse
  en lugar de eliminarse físicamente.

## Tabla: empresas

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| razon_social | text | Razón social. |
| nombre_comercial | text | Nombre comercial. |
| rubro | text | Rubro comercial. |
| ciudad | text | Ciudad. |
| pais | text | País. |
| sitio_web | text | Sitio web. |
| linkedin | text | Perfil de LinkedIn. |
| facebook | text | Perfil de Facebook. |
| instagram | text | Perfil de Instagram. |
| tamano_empresa | text | Pequeña, mediana, grande. |
| estado | text | Prospecto, contactado, interesado, etc. |
| ejecutivo_id | UUID | Ejecutivo asignado. |
| origen | text | Web, chat, WhatsApp, importación, prospección. |
| creado_por | UUID | Usuario que registró la empresa. |
| created_at | timestamp | Fecha de creación. |
| updated_at | timestamp | Fecha de actualización. |

## Reglas de empresas

- Cada ejecutivo puede ver únicamente sus empresas asignadas.
- El administrador puede ver todas las empresas.
- Un ejecutivo puede registrar empresas propias.
- Un ejecutivo puede importar su propia base de clientes.
- El sistema debe validar duplicados por razón social, correo y WhatsApp.
- El origen debe registrar si la empresa fue cargada por el ejecutivo,
  administrador, chat, web o campaña.

## Tabla: contactos

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa asociada. |
| nombre | text | Nombre del contacto. |
| cargo | text | Cargo. |
| email | text | Correo. |
| whatsapp | text | Número de WhatsApp. |
| telefono | text | Teléfono. |
| estado | text | Activo o inactivo. |
| created_at | timestamp | Fecha de creación. |

## Tabla: leads

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa asociada. |
| contacto_id | UUID | Contacto asociado. |
| ejecutivo_id | UUID | Ejecutivo asignado. |
| origen | text | Web, chat, WhatsApp, campaña, importación. |
| rubro | text | Rubro comercial. |
| interes | text | Nivel de interés. |
| prioridad | text | Alta, media, baja. |
| paquete_interes_id | UUID | Paquete de interés. |
| stand_interes_id | UUID | Stand de interés. |
| estado | text | Estado comercial. |
| proxima_accion | text | Próxima acción. |
| fecha_proxima_accion | timestamp | Fecha programada. |
| created_at | timestamp | Fecha de creación. |

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

## Tabla: zonas

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| nombre | text | Nombre de la zona. |
| tipo | text | Interior o exterior. |
| descripcion | text | Descripción. |
| capacidad | integer | Capacidad o cantidad de espacios. |

## Tabla: stands

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| codigo | text | Código único del stand. |
| zona_id | UUID | Zona asociada. |
| tipo | text | Stand, cancha, espacio exterior. |
| dimensiones | text | Dimensiones. |
| precio_base | numeric | Precio base. |
| descripcion | text | Descripción. |
| estado | text | Disponible, bloqueado, reservado, vendido, no disponible. |
| ejecutivo_id | UUID | Ejecutivo responsable. |
| reserva_activa_id | UUID | Reserva activa. |
| created_at | timestamp | Fecha de creación. |
| updated_at | timestamp | Fecha de actualización. |

## Estados de stand

- Disponible.
- Bloqueado temporal.
- Reservado.
- Vendido.
- No disponible.

## Tabla: paquetes

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| nombre | text | Diamante, Platino, Oro, etc. |
| descripcion | text | Descripción. |
| precio | numeric | Precio. |
| beneficios | jsonb | Lista de beneficios. |
| condiciones | text | Condiciones comerciales. |
| estado | text | Activo o inactivo. |
| created_at | timestamp | Fecha de creación. |

## Tabla: paquete_stand

| Campo | Tipo | Descripción |
|---|---|---|
| paquete_id | UUID | Paquete asociado. |
| stand_id | UUID | Stand asociado. |

## Tabla: reservas

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa solicitante. |
| lead_id | UUID | Lead asociado. |
| stand_id | UUID | Stand solicitado. |
| ejecutivo_id | UUID | Ejecutivo asignado. |
| estado | text | Bloqueado, reservado, vendido, expirado, cancelado. |
| fecha_inicio | timestamp | Inicio del bloqueo. |
| fecha_expiracion | timestamp | Expiración del bloqueo. |
| fecha_extension | timestamp | Fecha de extensión. |
| motivo_extension | text | Motivo de la extensión. |
| monto | numeric | Monto de venta. |
| comprobante_url | text | Comprobante. |
| contrato_url | text | Contrato. |
| created_at | timestamp | Fecha de creación. |

## Tabla: plantillas

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| nombre | text | Nombre de la plantilla. |
| tipo | text | Invitación, propuesta, contrato, nutrición. |
| canal | text | Email, WhatsApp, PDF. |
| contenido | text | Contenido con variables. |
| estado | text | Activa o inactiva. |
| created_at | timestamp | Fecha de creación. |

## Tabla: campanas

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| nombre | text | Nombre de la campaña. |
| segmento | text | Segmento objetivo. |
| plantilla_id | UUID | Plantilla utilizada. |
| canal | text | Email o WhatsApp. |
| estado | text | Borrador, aprobada, enviando, finalizada. |
| fecha_inicio | timestamp | Inicio. |
| fecha_fin | timestamp | Fin. |
| limite_diario | integer | Límite de envíos. |
| creado_por | UUID | Usuario que creó la campaña. |

## Tabla: comunicaciones

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa asociada. |
| lead_id | UUID | Lead asociado. |
| contacto_id | UUID | Contacto asociado. |
| canal | text | Email, WhatsApp, chat. |
| plantilla_id | UUID | Plantilla utilizada. |
| contenido | text | Contenido enviado. |
| estado | text | Enviado, entregado, leído, respondido, error. |
| agente | text | Usuario o agente de IA. |
| created_at | timestamp | Fecha de envío. |

## Tabla: actividades

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa asociada. |
| lead_id | UUID | Lead asociado. |
| usuario_id | UUID | Usuario responsable. |
| tipo | text | Llamada, nota, correo, WhatsApp, reunión, cambio de estado. |
| descripcion | text | Detalle. |
| resultado | text | Resultado. |
| created_at | timestamp | Fecha de registro. |

## Tabla: documentos

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| empresa_id | UUID | Empresa asociada. |
| lead_id | UUID | Lead asociado. |
| tipo | text | Propuesta, contrato, comprobante. |
| nombre | text | Nombre del documento. |
| url | text | URL del archivo. |
| created_at | timestamp | Fecha de creación. |

## Tabla: notificaciones

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único. |
| usuario_id | UUID | Usuario destinatario. |
| tipo | text | Reserva, lead, seguimiento, alerta. |
| titulo | text | Título. |
| mensaje | text | Mensaje. |
| canal | text | Panel, email, WhatsApp. |
| estado | text | Pendiente, enviado, leído. |
| referencia_id | UUID | Registro relacionado. |
| created_at | timestamp | Fecha de creación. |

## Tecnología de base de datos

La base de datos será PostgreSQL.

El acceso será realizado mediante SQLAlchemy 2.0.

Las migraciones serán gestionadas con Alembic.

Las validaciones de entrada y salida serán realizadas con Pydantic v2.

## Convenciones recomendadas

- Usar snake_case para tablas y columnas.
- Usar UUID como clave primaria.
- Usar timestamps con zona horaria.
- Usar foreign keys para relaciones.
- Usar índices en campos de búsqueda frecuente.
- Usar constraints para evitar estados inválidos.
- Usar soft delete para usuarios, empresas y leads cuando corresponda.
- Mantener auditoría de cambios críticos.

## Relaciones principales

- Un usuario puede tener muchas empresas asignadas.
- Una empresa puede tener muchos contactos.
- Una empresa puede tener muchos leads.
- Un lead pertenece a una empresa.
- Un lead puede tener un ejecutivo asignado.
- Un stand pertenece a una zona.
- Un stand puede tener una reserva activa.
- Una reserva pertenece a una empresa y un stand.
- Un paquete puede estar asociado a muchos stands.
- Una empresa puede tener muchas comunicaciones.
- Una empresa puede tener muchas actividades.
- Una empresa puede tener muchos documentos.
- Un usuario puede recibir muchas notificaciones.