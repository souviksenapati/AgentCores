"""Chat Service for Agent Communication"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import uuid
import httpx
import json
import os

from app.models.database import Agent
from app.models.chat import ChatMessage as ChatMessageModel
from app.schemas import ChatMessage, ChatResponse


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-your-key-here")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"

    async def chat_with_agent(
        self, 
        agent_id: str, 
        message: str, 
        user_id: str, 
        tenant_id: str
    ) -> ChatResponse:
        """Chat with an agent using OpenRouter API"""
        
        # Get agent
        agent = self.db.query(Agent).filter(
            Agent.agent_id == agent_id,
            Agent.tenant_id == tenant_id
        ).first()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Save user message
        user_message = ChatMessageModel(
            agent_id=agent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            message=message,
            sender="user"
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)

        # Get agent response from OpenRouter
        try:
            agent_response = await self._get_agent_response(agent, message, user_id)
            
            # Save agent response
            agent_message = ChatMessageModel(
                agent_id=agent_id,
                user_id=user_id,
                tenant_id=tenant_id,
                message=agent_response,
                sender="agent"
            )
            self.db.add(agent_message)
            self.db.commit()
            self.db.refresh(agent_message)

            return ChatResponse(
                message=ChatMessage(
                    id=str(user_message.id),
                    agent_id=agent_id,
                    message=message,
                    sender="user",
                    timestamp=user_message.created_at
                ),
                response=ChatMessage(
                    id=str(agent_message.id),
                    agent_id=agent_id,
                    message=agent_response,
                    sender="agent",
                    timestamp=agent_message.created_at
                )
            )
        except Exception as e:
            # Save error response
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            agent_message = ChatMessageModel(
                agent_id=agent_id,
                user_id=user_id,
                tenant_id=tenant_id,
                message=error_message,
                sender="agent"
            )
            self.db.add(agent_message)
            self.db.commit()
            self.db.refresh(agent_message)

            return ChatResponse(
                message=ChatMessage(
                    id=str(user_message.id),
                    agent_id=agent_id,
                    message=message,
                    sender="user",
                    timestamp=user_message.created_at
                ),
                response=ChatMessage(
                    id=str(agent_message.id),
                    agent_id=agent_id,
                    message=error_message,
                    sender="agent",
                    timestamp=agent_message.created_at
                )
            )

    async def _get_agent_response(self, agent: Agent, message: str, user_id: str) -> str:
        """Get response from OpenRouter API"""
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AgentCores"
        }

        # Get recent chat history for context
        recent_messages = self.db.query(ChatMessageModel).filter(
            ChatMessageModel.agent_id == agent.agent_id,
            ChatMessageModel.user_id == user_id,
            ChatMessageModel.tenant_id == agent.tenant_id
        ).order_by(ChatMessageModel.created_at.desc()).limit(10).all()

        # Build conversation context
        messages = [
            {"role": "system", "content": agent.instructions or "You are a helpful AI assistant."}
        ]
        
        # Add recent messages in chronological order
        for msg in reversed(recent_messages):
            role = "user" if msg.sender == "user" else "assistant"
            messages.append({"role": role, "content": msg.message})
        
        # Add current message
        messages.append({"role": "user", "content": message})

        payload = {
            "model": agent.model or "openrouter/meta-llama/llama-3.2-3b-instruct:free",
            "messages": messages,
            "temperature": agent.temperature or 0.7,
            "max_tokens": agent.max_tokens or 1000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def get_chat_history(
        self, 
        agent_id: str, 
        user_id: str, 
        tenant_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get chat history for an agent"""
        
        messages = self.db.query(ChatMessageModel).filter(
            ChatMessageModel.agent_id == agent_id,
            ChatMessageModel.user_id == user_id,
            ChatMessageModel.tenant_id == tenant_id
        ).order_by(ChatMessageModel.created_at.desc()).limit(limit).all()

        return [msg.to_dict() for msg in reversed(messages)]