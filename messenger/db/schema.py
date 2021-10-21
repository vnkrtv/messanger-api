from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import MetaData

from messenger.settings import Config

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    # Именование индексов
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    # Именование уникальных индексов
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    # Именование CHECK-constraint-ов
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    # Именование внешних ключей
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    # Именование первичных ключей
    "pk": "pk__%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


users_table = Table(
    "users",
    metadata,
    Column("username", String(length=255), primary_key=True),
    Column("password_hash", String(length=64), nullable=False),
    Column("timezone", String(length=128), nullable=False, default=Config.timezone),
    Column("is_yandex_backend_school_student", Boolean, nullable=False, default=False),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now()
    ),
)

sessions_table = Table(
    "sessions",
    metadata,
    Column("session_id", UUID(as_uuid=True), primary_key=True),
    Column(
        "username", String(length=255), ForeignKey("users.username"), nullable=False
    ),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("expired_at", DateTime, nullable=False, server_default=func.now()),
)

chats_table = Table(
    "chats",
    metadata,
    Column("chat_id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(length=255), nullable=False, index=True),
    Column(
        "creator_username",
        String(length=255),
        ForeignKey("users.username"),
        nullable=False,
    ),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("description", String(length=255), nullable=False, default=""),
    Column("is_private", Boolean, nullable=False, default=False),
)

chat_users_table = Table(
    "chat_users",
    metadata,
    Column(
        "chat_id", UUID(as_uuid=True), ForeignKey("chats.chat_id"), primary_key=True
    ),
    Column("chat_user_id", UUID(as_uuid=True), primary_key=True, unique=True),
    Column("chat_username", String(length=255), nullable=False),
    Column(
        "username", String(length=255), ForeignKey("users.username"), nullable=False
    ),
    Column("is_admin", Boolean, nullable=False, default=False),
)

messages_table = Table(
    "messages",
    metadata,
    Column("message_id", UUID(as_uuid=True), primary_key=True),
    Column("text", String, nullable=False),
    Column("chat_id", UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=False),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Column(
        "chat_user_id",
        UUID(as_uuid=True),
        ForeignKey("chat_users.chat_user_id"),
        nullable=False,
    ),
)
