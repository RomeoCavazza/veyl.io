"""Ensure projects scope columns and defaults exist

Revision ID: ensure_projects_scope_columns
Revises: align_projects_user_id_uuid
Create Date: 2025-11-10 23:05:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "ensure_projects_scope_columns"
down_revision = "align_projects_user_id_uuid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        DO $$
        BEGIN
            -- scope_type
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'score_type'
            ) THEN
                ALTER TABLE projects RENAME COLUMN score_type TO scope_type;
            ELSIF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'scope_type'
            ) THEN
                ALTER TABLE projects
                ADD COLUMN scope_type VARCHAR(50);
            END IF;

            -- scope_query
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'score_query'
            ) THEN
                ALTER TABLE projects RENAME COLUMN score_query TO scope_query;
            ELSIF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'scope_query'
            ) THEN
                ALTER TABLE projects
                ADD COLUMN scope_query TEXT;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'scope_type'
            ) THEN
                ALTER TABLE projects DROP COLUMN scope_type;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'scope_query'
            ) THEN
                ALTER TABLE projects DROP COLUMN scope_query;
            END IF;
        END $$;
        """
    )


