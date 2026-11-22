"""Importar todos los modelos para que Base.metadata los registre (Alembic)."""
from app.models.common import *  # noqa: F401,F403
from app.models.user import Usuario  # noqa: F401
from app.models.crm import Contacto, Empresa, Lead  # noqa: F401
from app.models.inventario import Paquete, Stand, Zona, paquete_stand  # noqa: F401
from app.models.reserva import Reserva  # noqa: F401
from app.models.comunicaciones import (  # noqa: F401
    Actividad,
    Campana,
    Comunicacion,
    Documento,
    Notificacion,
    Plantilla,
)
from app.models.secuencias import (  # noqa: F401
    Secuencia,
    SecuenciaInscripcion,
    SecuenciaPaso,
)
from app.models.comercial import Factura, FirmaDigital, Pago  # noqa: F401
from app.models.patrocinadores import Patrocinador  # noqa: F401
from app.models.config_agente import ConfigAgente  # noqa: F401
