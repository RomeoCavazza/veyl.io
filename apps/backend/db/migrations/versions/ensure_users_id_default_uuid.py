"""ensure users id column uses uuid default

Revision ID: ensure_users_id_default_uuid
Revises: add_post_meta_fields
Create Date: 2025-11-10 12:15:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ensure_users_id_default_uuid"
down_revision: Union[str, None] = "add_post_meta_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        ALTER TABLE users
          ALTER COLUMN id SET DEFAULT uuid_generate_v4();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
          ALTER COLUMN id DROP DEFAULT;
        """
    )

