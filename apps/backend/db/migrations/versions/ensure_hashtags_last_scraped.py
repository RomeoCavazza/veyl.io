"""Ensure hashtags table has last_scraped column

Revision ID: ensure_hashtags_last_scraped
Revises: ensure_projects_platforms_text
Create Date: 2025-11-10 23:35:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "ensure_hashtags_last_scraped"
down_revision = "ensure_projects_platforms_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'hashtags'
                  AND column_name = 'last_scraped'
            ) THEN
                ALTER TABLE hashtags
                ADD COLUMN last_scraped TIMESTAMP;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'hashtags'
                  AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE hashtags
                ADD COLUMN updated_at TIMESTAMP;
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
                WHERE table_name = 'hashtags'
                  AND column_name = 'last_scraped'
            ) THEN
                ALTER TABLE hashtags DROP COLUMN last_scraped;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'hashtags'
                  AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE hashtags DROP COLUMN updated_at;
            END IF;
        END $$;
        """
    )


