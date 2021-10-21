"""add_gist_index_on_messages

Revision ID: 64482df80342
Revises: 3336355bd4d2
Create Date: 2021-10-19 21:39:35.221048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "64482df80342"
down_revision = "3336355bd4d2"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
     CREATE OR REPLACE FUNCTION make_tsvector(text TEXT)
        RETURNS tsvector AS
    $$
    BEGIN
        RETURN to_tsvector(text);
    END
    $$
        LANGUAGE 'plpgsql' IMMUTABLE
    """
    )
    op.create_index(
        op.f("ix__messages__text"),
        "messages",
        [sa.text("make_tsvector(text)")],
        postgresql_using="gist",
    )


def downgrade():
    op.drop_index("ix__messages__text", table_name="messages")
