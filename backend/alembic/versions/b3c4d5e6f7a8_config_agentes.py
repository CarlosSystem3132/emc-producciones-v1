"""config_agentes — prompts y modos de autonomía de los agentes de IA

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-11-22 10:30:00.000000

El admin configura desde el panel el prompt del sistema y el modo de trabajo
de cada agente (automatico | asistido | manual) — ver docs/14-agentes-ia-flujos.md.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.models.common import GUID

revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'config_agentes',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('clave', sa.String(length=30), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('prompt_sistema', sa.Text(), nullable=False),
        sa.Column('modo_autonomia', sa.String(length=20), nullable=False),
        sa.Column('activo', sa.Enum('activo', 'inactivo', name='estado_activo', native_enum=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clave'),
    )
    op.create_index('ix_config_agentes_clave', 'config_agentes', ['clave'])


def downgrade() -> None:
    op.drop_index('ix_config_agentes_clave', table_name='config_agentes')
    op.drop_table('config_agentes')
