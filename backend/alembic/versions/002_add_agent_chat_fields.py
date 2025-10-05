"""Add agent chat fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to agents table
    op.add_column(
        "agents",
        sa.Column(
            "model",
            sa.String(200),
            default="openrouter/meta-llama/llama-3.2-3b-instruct:free",
        ),
    )
    op.add_column(
        "agents",
        sa.Column("instructions", sa.Text(), default="You are a helpful AI assistant."),
    )
    op.add_column("agents", sa.Column("temperature", sa.Float(), default=0.7))
    op.add_column("agents", sa.Column("max_tokens", sa.Integer(), default=1000))
    op.add_column("agents", sa.Column("connected_agents", sa.JSON(), default=list))

    # Create chat_messages table
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(50),
            sa.ForeignKey("tenants.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.agent_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sender", sa.String(20), nullable=False),
        sa.Column("metadata", sa.JSON(), default=dict),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for chat_messages
    op.create_index(
        "ix_chat_messages_agent_created", "chat_messages", ["agent_id", "created_at"]
    )
    op.create_index(
        "ix_chat_messages_tenant_agent", "chat_messages", ["tenant_id", "agent_id"]
    )


def downgrade():
    # Drop chat_messages table
    op.drop_table("chat_messages")

    # Remove columns from agents table
    op.drop_column("agents", "connected_agents")
    op.drop_column("agents", "max_tokens")
    op.drop_column("agents", "temperature")
    op.drop_column("agents", "instructions")
    op.drop_column("agents", "model")
