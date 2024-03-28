"""Added User, Token, Chat, ChatParticipant and Message models.

Revision ID: 33a9590c62bc
Revises:
Create Date: 2024-03-28 10:23:47.877823

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "33a9590c62bc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM("SAVED_MESSAGES", "DIALOGUE", "GROUP", name="chat_type"),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("password", sa.String(length=256), nullable=False),
        sa.Column("last_online", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.create_table(
        "chat_participant",
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chat_id"], ["chat.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("chat_id", "participant_id"),
    )
    op.create_table(
        "message",
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM("TEXT", "VOICE", "FILE", name="message_type"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("is_edited", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["chat_id"], ["chat.id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "token",
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM("ACCESS", "REFRESH", name="token_type"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type", "user_id", name="unique_token"),
    )
    op.create_index(op.f("ix_token_token"), "token", ["token"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_token_token"), table_name="token")
    op.drop_table("token")
    op.execute("DROP TYPE token_type;")
    op.drop_table("message")
    op.execute("DROP TYPE message_type;")
    op.drop_table("chat_participant")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")
    op.drop_table("chat")
    op.execute("DROP TYPE chat_type;")
