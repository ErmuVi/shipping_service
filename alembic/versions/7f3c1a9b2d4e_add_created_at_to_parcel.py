"""add created_at to parcel

Revision ID: 7f3c1a9b2d4e
Revises: 18eaded18684
Create Date: 2026-10-24 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f3c1a9b2d4e"
down_revision: Union[str, Sequence[str], None] = "18eaded18684"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parcel creation timestamp."""
    op.add_column(
        "parcels",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop parcel creation timestamp."""
    op.drop_column("parcels", "created_at")
