"""add skill tool providers

Revision ID: 7b12f604f04e
Revises: 03ea244985ce
Create Date: 2025-12-23 12:00:00.000000

"""
from alembic import op
import models as models
import sqlalchemy as sa


def _is_pg(conn):
    return conn.dialect.name == "postgresql"


# revision identifiers, used by Alembic.
revision = '7b12f604f04e'
down_revision = '03ea244985ce'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    if _is_pg(conn):
        op.create_table('tool_skill_providers',
            sa.Column('id', models.types.StringUUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('skill_identifier', sa.String(length=64), nullable=False),
            sa.Column('icon', sa.String(length=255), nullable=True),
            sa.Column('tenant_id', models.types.StringUUID(), nullable=False),
            sa.Column('user_id', models.types.StringUUID(), nullable=False),
            sa.Column('source_type', sa.String(length=32), nullable=False),
            sa.Column('source_url', sa.Text(), nullable=True),
            sa.Column('source_hash', sa.String(length=64), nullable=False),
            sa.Column('version', sa.String(length=32), nullable=False),
            sa.Column('author', sa.String(length=128), nullable=True),
            sa.Column('skill_license', sa.String(length=64), nullable=True),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('compatibility', sa.Text(), nullable=True),
            sa.Column('allowed_tools', sa.Text(), nullable=True),
            sa.Column('metadata_extra', sa.Text(), nullable=True),
            sa.Column('full_content', sa.Text(), nullable=False),
            sa.Column('has_scripts', sa.Boolean(), nullable=False),
            sa.Column('scripts_manifest', sa.Text(), nullable=True),
            sa.Column('enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
            sa.PrimaryKeyConstraint('id', name='tool_skill_provider_pkey'),
            sa.UniqueConstraint('tenant_id', 'name', name='unique_skill_provider_name'),
            sa.UniqueConstraint('tenant_id', 'skill_identifier', name='unique_skill_provider_identifier')
        )
    else:
        op.create_table('tool_skill_providers',
            sa.Column('id', models.types.StringUUID(), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('skill_identifier', sa.String(length=64), nullable=False),
            sa.Column('icon', sa.String(length=255), nullable=True),
            sa.Column('tenant_id', models.types.StringUUID(), nullable=False),
            sa.Column('user_id', models.types.StringUUID(), nullable=False),
            sa.Column('source_type', sa.String(length=32), nullable=False),
            sa.Column('source_url', models.types.LongText(), nullable=True),
            sa.Column('source_hash', sa.String(length=64), nullable=False),
            sa.Column('version', sa.String(length=32), nullable=False),
            sa.Column('author', sa.String(length=128), nullable=True),
            sa.Column('skill_license', sa.String(length=64), nullable=True),
            sa.Column('description', models.types.LongText(), nullable=False),
            sa.Column('compatibility', models.types.LongText(), nullable=True),
            sa.Column('allowed_tools', models.types.LongText(), nullable=True),
            sa.Column('metadata_extra', models.types.LongText(), nullable=True),
            sa.Column('full_content', models.types.LongText(), nullable=False),
            sa.Column('has_scripts', sa.Boolean(), nullable=False),
            sa.Column('scripts_manifest', models.types.LongText(), nullable=True),
            sa.Column('enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
            sa.PrimaryKeyConstraint('id', name='tool_skill_provider_pkey'),
            sa.UniqueConstraint('tenant_id', 'name', name='unique_skill_provider_name'),
            sa.UniqueConstraint('tenant_id', 'skill_identifier', name='unique_skill_provider_identifier')
        )


def downgrade():
    op.drop_table('tool_skill_providers')
