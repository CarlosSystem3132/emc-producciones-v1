"""secuencias, pagos, facturas, firmas, patrocinadores

Revision ID: a1b2c3d4e5f6
Revises: dc9c2d3a9e9d
Create Date: 2026-11-21 18:10:00.000000

Entregables agregados:
- Fase 2: secuencias de seguimiento (secuencias, secuencia_pasos, secuencia_inscripciones).
- Fase 4: integración con pagos (pagos), facturación (facturas),
  firma digital (firmas_digitales) y panel para patrocinadores (patrocinadores).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.models.common import GUID

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dc9c2d3a9e9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'secuencias',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('canal', sa.Enum('email', 'whatsapp', 'chat', 'pdf', name='canal_comunicacion', native_enum=False), nullable=False),
        sa.Column('estado', sa.Enum('activo', 'inactivo', name='estado_activo', native_enum=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'secuencia_pasos',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('secuencia_id', GUID(), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('dias_espera', sa.Integer(), nullable=False),
        sa.Column('plantilla_id', GUID(), nullable=True),
        sa.Column('mensaje', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['secuencia_id'], ['secuencias.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plantilla_id'], ['plantillas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_secuencia_pasos_sequencia_id', 'secuencia_pasos', ['secuencia_id'])
    op.create_table(
        'secuencia_inscripciones',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('secuencia_id', GUID(), nullable=False),
        sa.Column('empresa_id', GUID(), nullable=False),
        sa.Column('contacto_id', GUID(), nullable=True),
        sa.Column('lead_id', GUID(), nullable=True),
        sa.Column('paso_actual', sa.Integer(), nullable=False),
        sa.Column('proxima_ejecucion', sa.DateTime(timezone=True), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('ultimo_envio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['secuencia_id'], ['secuencias.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contacto_id'], ['contactos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_secuencia_inscripciones_sequencia_id', 'secuencia_inscripciones', ['secuencia_id'])
    op.create_index('ix_secuencia_inscripciones_empresa_id', 'secuencia_inscripciones', ['empresa_id'])
    op.create_index('ix_secuencia_inscripciones_proxima_ejecucion', 'secuencia_inscripciones', ['proxima_ejecucion'])

    op.create_table(
        'pagos',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('reserva_id', GUID(), nullable=False),
        sa.Column('empresa_id', GUID(), nullable=True),
        sa.Column('monto', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('metodo', sa.String(length=30), nullable=False),
        sa.Column('referencia', sa.String(length=120), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('registrado_por', GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['reserva_id'], ['reservas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['registrado_por'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_pagos_reserva_id', 'pagos', ['reserva_id'])

    op.create_table(
        'facturas',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('reserva_id', GUID(), nullable=True),
        sa.Column('empresa_id', GUID(), nullable=True),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('nit', sa.String(length=50), nullable=True),
        sa.Column('razon_social', sa.String(length=255), nullable=True),
        sa.Column('monto', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['reserva_id'], ['reservas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero'),
    )
    op.create_index('ix_facturas_reserva_id', 'facturas', ['reserva_id'])

    op.create_table(
        'firmas_digitales',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('reserva_id', GUID(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('firmante_nombre', sa.String(length=150), nullable=False),
        sa.Column('firmante_email', sa.String(length=255), nullable=True),
        sa.Column('firma_hash', sa.String(length=128), nullable=True),
        sa.Column('ip', sa.String(length=50), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('firmada_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['reserva_id'], ['reservas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_firmas_digitales_reserva_id', 'firmas_digitales', ['reserva_id'])

    op.create_table(
        'patrocinadores',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('sitio_web', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.Enum('activo', 'inactivo', name='estado_activo', native_enum=False), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('patrocinadores')
    op.drop_index('ix_firmas_digitales_reserva_id', table_name='firmas_digitales')
    op.drop_table('firmas_digitales')
    op.drop_index('ix_facturas_reserva_id', table_name='facturas')
    op.drop_table('facturas')
    op.drop_index('ix_pagos_reserva_id', table_name='pagos')
    op.drop_table('pagos')
    op.drop_index('ix_secuencia_inscripciones_proxima_ejecucion', table_name='secuencia_inscripciones')
    op.drop_index('ix_secuencia_inscripciones_empresa_id', table_name='secuencia_inscripciones')
    op.drop_index('ix_secuencia_inscripciones_sequencia_id', table_name='secuencia_inscripciones')
    op.drop_table('secuencia_inscripciones')
    op.drop_index('ix_secuencia_pasos_sequencia_id', table_name='secuencia_pasos')
    op.drop_table('secuencia_pasos')
    op.drop_table('secuencias')
