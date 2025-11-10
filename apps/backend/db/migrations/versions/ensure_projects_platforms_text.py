"""Ensure projects.platforms is stored as JSON text

Revision ID: ensure_projects_platforms_text
Revises: ensure_projects_scope_columns
Create Date: 2025-11-10 23:15:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "ensure_projects_platforms_text"
down_revision = "ensure_projects_scope_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'platforms'
                  AND data_type = 'ARRAY'
            ) THEN
                ALTER TABLE projects
                ALTER COLUMN platforms DROP DEFAULT;

                ALTER TABLE projects
                ALTER COLUMN platforms
                TYPE text
                USING to_json(COALESCE(platforms, ARRAY[]::text[]))::text;

                ALTER TABLE projects
                ALTER COLUMN platforms SET DEFAULT '[]';
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
                  AND column_name = 'platforms'
                  AND data_type = 'text'
            ) THEN
                ALTER TABLE projects
                ALTER COLUMN platforms DROP DEFAULT;

                ALTER TABLE projects
                ALTER COLUMN platforms
                TYPE text[]
                USING (
                    SELECT COALESCE(
                        ARRAY(
                            SELECT value
                            FROM json_array_elements_text(
                                CASE
                                    WHEN platforms IS NULL OR platforms = ''
                                    THEN '[]'::json
                                    ELSE platforms::json
                                END
                            )
                        ),
                        ARRAY[]::text[]
                    )
                );

                ALTER TABLE projects
                ALTER COLUMN platforms SET DEFAULT ARRAY[]::text[];
            END IF;
        END $$;
        """
    )


