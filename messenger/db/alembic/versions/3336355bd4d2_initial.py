"""Initial

Revision ID: 3336355bd4d2
Revises: 
Create Date: 2021-10-16 01:14:54.092730

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3336355bd4d2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=64), nullable=False),
        sa.Column("timezone", sa.String(length=128), nullable=False),
        sa.Column("is_yandex_backend_school_student", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("username", name=op.f("pk__users")),
    )
    op.create_table(
        "chats",
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("creator_username", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_username"],
            ["users.username"],
            name=op.f("fk__chats__creator_username__users"),
        ),
        sa.PrimaryKeyConstraint("chat_id", name=op.f("pk__chats")),
    )
    op.create_index(op.f("ix__chats__name"), "chats", ["name"], unique=False)
    op.create_table(
        "sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "expired_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["username"], ["users.username"], name=op.f("fk__sessions__username__users")
        ),
        sa.PrimaryKeyConstraint("session_id", name=op.f("pk__sessions")),
    )
    op.create_table(
        "chat_users",
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_username", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chat_id"], ["chats.chat_id"], name=op.f("fk__chat_users__chat_id__chats")
        ),
        sa.ForeignKeyConstraint(
            ["username"],
            ["users.username"],
            name=op.f("fk__chat_users__username__users"),
        ),
        sa.PrimaryKeyConstraint("chat_id", "chat_user_id", name=op.f("pk__chat_users")),
        sa.UniqueConstraint("chat_user_id", name=op.f("uq__chat_users__chat_user_id")),
    )
    op.create_table(
        "messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("chat_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["chat_id"], ["chats.chat_id"], name=op.f("fk__messages__chat_id__chats")
        ),
        sa.ForeignKeyConstraint(
            ["chat_user_id"],
            ["chat_users.chat_user_id"],
            name=op.f("fk__messages__chat_user_id__chat_users"),
        ),
        sa.PrimaryKeyConstraint("message_id", name=op.f("pk__messages")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    op.drop_table("chat_users")
    op.drop_table("sessions")
    op.drop_index(op.f("ix__chats__name"), table_name="chats")
    op.drop_table("chats")
    op.drop_table("users")
    # ### end Alembic commands ###