"""add meta payload fields to posts

Revision ID: add_post_meta_fields
Revises: add_projects
Create Date: 2025-02-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_post_meta_fields'
down_revision = 'add_projects'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('external_id', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('api_payload', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('last_fetch_at', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('source', sa.String(length=50), server_default='seed_demo', nullable=True))
    op.create_unique_constraint('uq_posts_external_id', 'posts', ['external_id'])


def downgrade() -> None:
    op.drop_constraint('uq_posts_external_id', 'posts', type_='unique')
    op.drop_column('posts', 'source')
    op.drop_column('posts', 'last_fetch_at')
    op.drop_column('posts', 'api_payload')
    op.drop_column('posts', 'external_id')


