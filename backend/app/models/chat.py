import uuid

from sqlalchemy import JSON, Column, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.database import Base, TenantMixin, TimestampMixin


class ChatMessage(Base, TenantMixin, TimestampMixin):
    """Chat message model for agent conversations"""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    sender = Column(String(20), nullable=False)  # 'user' or 'agent'
    message_metadata = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent")
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("ix_chat_messages_agent_created", "agent_id", "created_at"),
        Index("ix_chat_messages_tenant_agent", "tenant_id", "agent_id"),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "agent_id": str(self.agent_id),
            "user_id": str(self.user_id),
            "message": self.message,
            "sender": self.sender,
            "timestamp": self.created_at.isoformat(),
            "metadata": self.message_metadata,
        }
