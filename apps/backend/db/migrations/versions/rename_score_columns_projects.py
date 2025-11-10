"""Renommer les colonnes score_* en scope_* et normaliser le champ platforms.

Cette migration est idempotente : elle vérifie l'existence des colonnes/typiages
avant de tenter de les modifier afin de couvrir les bases de données déjà corrigées
manuellement.

Revision ID: rename_score_columns_projects
Revises: add_projects
Create Date: 2025-11-10 22:00:00.000000
"""

from alembic import op

# Révision Alembic
revision = "rename_score_columns_projects"
down_revision = "add_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Renommer les colonnes si elles existent encore sous l'ancien nom
    conn.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'score_type'
            ) THEN
                ALTER TABLE projects RENAME COLUMN score_type TO scope_type;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'score_query'
            ) THEN
                ALTER TABLE projects RENAME COLUMN score_query TO scope_query;
            END IF;
        END $$;
        """
    )

    # Normaliser le champ platforms en TEXT contenant du JSON si l'ancienne version était un ARRAY
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
            ELSIF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'platforms'
                  AND data_type = 'USER-DEFINED'
                  AND udt_name = '_int8'
            ) THEN
                ALTER TABLE projects
                ALTER COLUMN platforms DROP DEFAULT;

                ALTER TABLE projects
                ALTER COLUMN platforms
                TYPE text
                USING to_json(COALESCE(platforms, ARRAY[]::bigint[]))::text;

                ALTER TABLE projects
                ALTER COLUMN platforms SET DEFAULT '[]';
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    conn = op.get_bind()

    # Revenir au nom initial uniquement si les colonnes actuelles existent
    conn.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'scope_type'
            ) THEN
                ALTER TABLE projects RENAME COLUMN scope_type TO score_type;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'scope_query'
            ) THEN
                ALTER TABLE projects RENAME COLUMN scope_query TO score_query;
            END IF;
        END $$;
        """
    )

    # Revenir à un ARRAY de TEXT pour platforms si nous l'avions converti en TEXT
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

