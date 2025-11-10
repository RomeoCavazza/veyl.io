"""Align projects.user_id column with UUID users primary key

Revision ID: align_projects_user_id_uuid
Revises: rename_score_columns_projects
Create Date: 2025-11-10 22:45:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "align_projects_user_id_uuid"
down_revision = "rename_score_columns_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        DO $$
        BEGIN
            -- Vérifier que la colonne est encore en INTEGER avant de migrer
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'projects'
                  AND column_name = 'user_id'
                  AND data_type = 'integer'
            ) THEN
                -- Purger les données dépendantes pour éviter les incohérences (table supposée vide en prod)
                -- Supprimer les contraintes/index existants
                IF EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'projects_user_id_fkey'
                ) THEN
                    ALTER TABLE projects DROP CONSTRAINT projects_user_id_fkey;
                END IF;
                -- Cast direct en UUID si possible
                ALTER TABLE projects
                ALTER COLUMN user_id TYPE uuid USING user_id::text::uuid;

                -- S'assurer que la contrainte FK pointe bien sur users.id en uuid
                BEGIN
                    ALTER TABLE projects
                    ADD CONSTRAINT projects_user_id_fkey
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                EXCEPTION
                    WHEN duplicate_object THEN
                        -- Contrainte déjà présente, ne rien faire
                        NULL;
                END;
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
                  AND column_name = 'user_id'
                  AND data_type = 'uuid'
            ) THEN
                DELETE FROM project_creators;
                DELETE FROM project_hashtags;
                DELETE FROM projects;

                ALTER TABLE projects
                ALTER COLUMN user_id TYPE integer USING (user_id::text)::integer;

                ALTER TABLE projects
                ADD CONSTRAINT projects_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            END IF;
        END $$;
        """
    )


