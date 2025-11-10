"""add projects tables with proper schema

Revision ID: add_projects
Revises: initial
Create Date: 2025-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_projects'
down_revision = '1884346654db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Table principale projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='draft', nullable=True),
        sa.Column('platforms', sa.Text(), nullable=True),  # JSON stored as Text
        sa.Column('scope_type', sa.String(length=50), nullable=True),  # 'hashtags', 'creators', 'both'
        sa.Column('scope_query', sa.Text(), nullable=True),
        sa.Column('creators_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('posts_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('signals_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_signal_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    op.create_index('ix_projects_status', 'projects', ['status'], unique=False)
    
    # 2. Table de liaison project_hashtags (réutilise hashtags existante)
    op.create_table(
        'project_hashtags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('hashtag_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hashtag_id'], ['hashtags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'hashtag_id', name='uq_project_hashtag')
    )
    op.create_index(op.f('ix_project_hashtags_id'), 'project_hashtags', ['id'], unique=False)
    op.create_index('ix_project_hashtags_project_id', 'project_hashtags', ['project_id'], unique=False)
    op.create_index('ix_project_hashtags_hashtag_id', 'project_hashtags', ['hashtag_id'], unique=False)
    
    # 3. Table project_creators (créateurs suivis)
    op.create_table(
        'project_creators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('creator_username', sa.String(length=255), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'platform_id', 'creator_username', name='uq_project_creator')
    )
    op.create_index(op.f('ix_project_creators_id'), 'project_creators', ['id'], unique=False)
    op.create_index('ix_project_creators_project_id', 'project_creators', ['project_id'], unique=False)
    op.create_index('ix_project_creators_creator', 'project_creators', ['platform_id', 'creator_username'], unique=False)


def downgrade() -> None:
    # Supprimer dans l'ordre inverse (dépendances d'abord)
    op.drop_index('ix_project_creators_creator', table_name='project_creators')
    op.drop_index(op.f('ix_project_creators_id'), table_name='project_creators')
    op.drop_index('ix_project_creators_project_id', table_name='project_creators')
    op.drop_table('project_creators')
    
    op.drop_index('ix_project_hashtags_hashtag_id', table_name='project_hashtags')
    op.drop_index('ix_project_hashtags_project_id', table_name='project_hashtags')
    op.drop_index(op.f('ix_project_hashtags_id'), table_name='project_hashtags')
    op.drop_table('project_hashtags')
    
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')

