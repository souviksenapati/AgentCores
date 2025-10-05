"""
OpenRouter AI Provider with enterprise features.
Built for MVP, designed for enterprise scale.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.core.interfaces import (
    AgentConfig,
    AIProviderInterface,
    ProviderType,
    TaskResult,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class OpenRouterProvider(AIProviderInterface):
    """
    OpenRouter AI Provider with enterprise resilience.

    Current: Basic OpenRouter integration
    Future: Multi-model orchestration with intelligent routing
    """

    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "https://agentcores.com")
        self.site_name = os.getenv("OPENROUTER_SITE_NAME", "AgentCores")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        # Enterprise configuration
        self.timeout = 300  # 5 minutes default timeout
        self.max_retries = 3
        self.rate_limit = {"requests_per_minute": 1000, "tokens_per_minute": 100000}

        # Model pricing (future: dynamic pricing from API)
        self.model_pricing = {
            "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
            "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "openai/gpt-4": {"input": 0.03, "output": 0.06},
            "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
            # Add more models as needed
        }

        # Initialize HTTP client with enterprise settings
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            },
        )

    async def generate_completion(
        self, prompt: str, config: AgentConfig, context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Generate AI completion with enterprise monitoring.

        Current: Basic completion
        Future: Complex prompt engineering, caching, optimization
        """
        task_id = context.get("task_id", "unknown") if context else "unknown"
        started_at = datetime.utcnow()

        try:
            # Prepare request payload (future: prompt optimization)
            payload = {
                "model": config.model,
                "messages": [
                    {"role": "system", "content": config.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "stream": False,  # Future: streaming support
                # Enterprise metadata
                "metadata": {
                    "agent_id": context.get("agent_id") if context else None,
                    "task_id": task_id,
                    "tenant_id": context.get("tenant_id") if context else None,
                },
            }

            # Execute with retry logic (enterprise resilience)
            response_data = await self._execute_with_retry(payload)

            # Parse response
            completed_at = datetime.utcnow()
            execution_time_ms = int((completed_at - started_at).total_seconds() * 1000)

            # Extract content and usage
            message = response_data["choices"][0]["message"]["content"]
            usage = response_data.get("usage", {})

            # Calculate cost (enterprise cost tracking)
            cost_estimate = self._calculate_cost(config.model, usage)

            # Log for enterprise analytics
            logger.info(
                f"OpenRouter completion successful: {task_id}, "
                f"tokens: {usage}, cost: ${cost_estimate:.4f}"
            )

            return TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result=message,
                started_at=started_at,
                completed_at=completed_at,
                execution_time_ms=execution_time_ms,
                token_usage={
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                cost_estimate=cost_estimate,
            )

        except Exception as e:
            completed_at = datetime.utcnow()
            execution_time_ms = int((completed_at - started_at).total_seconds() * 1000)
            logger.error(f"OpenRouter completion failed: {task_id} - {str(e)}")

            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result=None,
                error_message=str(e),
                started_at=started_at,
                completed_at=completed_at,
                execution_time_ms=execution_time_ms,
                token_usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                cost_estimate=0.0,
            )

    async def validate_config(self, config: AgentConfig) -> bool:
        """
        Validate OpenRouter-specific configuration.

        Current: Basic validation
        Future: Model capability validation, quota checks
        """
        try:
            # Check if model is supported
            if config.model not in self.model_pricing:
                logger.warning(
                    f"Model {config.model} not in pricing table, proceeding anyway"
                )

            # Validate temperature range
            if not 0.0 <= config.temperature <= 2.0:
                raise ValueError(
                    f"Temperature must be between 0.0 and 2.0, got {config.temperature}"
                )

            # Validate max_tokens
            if config.max_tokens <= 0 or config.max_tokens > 32000:
                raise ValueError(
                    f"max_tokens must be between 1 and 32000, got {config.max_tokens}"
                )

            # Future: Model-specific validation
            # Future: Quota validation
            # Future: Rate limit validation

            return True

        except Exception as e:
            logger.error(f"Config validation failed: {str(e)}")
            return False

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get model capabilities and pricing.

        Current: Static model info
        Future: Dynamic model discovery from OpenRouter API
        """
        base_info = {
            "provider": "openrouter",
            "model": model,
            "pricing": self.model_pricing.get(model, {"input": 0.001, "output": 0.002}),
            "capabilities": ["completion", "chat"],
            "context_length": 32000,  # Default, varies by model
            "supported_features": ["temperature", "max_tokens", "system_messages"],
        }

        # Model-specific information
        model_specific = {
            "anthropic/claude-3-haiku": {
                "context_length": 200000,
                "description": "Fast, cost-effective model for simple tasks",
                "use_cases": [
                    "customer service",
                    "content moderation",
                    "data extraction",
                ],
            },
            "anthropic/claude-3-sonnet": {
                "context_length": 200000,
                "description": "Balanced model for complex reasoning",
                "use_cases": ["analysis", "writing", "coding", "research"],
            },
            "anthropic/claude-3-opus": {
                "context_length": 200000,
                "description": "Most capable model for complex tasks",
                "use_cases": [
                    "advanced reasoning",
                    "creative writing",
                    "complex analysis",
                ],
            },
            "openai/gpt-4": {
                "context_length": 8192,
                "description": "Advanced reasoning and problem-solving",
                "use_cases": ["complex reasoning", "code generation", "analysis"],
            },
            "openai/gpt-4-turbo": {
                "context_length": 128000,
                "description": "Fast GPT-4 with large context window",
                "use_cases": [
                    "document analysis",
                    "long conversations",
                    "complex tasks",
                ],
            },
        }

        if model in model_specific:
            base_info.update(model_specific[model])

        return base_info

    async def health_check(self) -> bool:
        """
        Provider health check for enterprise monitoring.

        Current: Simple API check
        Future: Comprehensive health metrics
        """
        try:
            # Simple health check with minimal request
            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": "Health check"}],
                "max_tokens": 10,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    json=payload,
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"OpenRouter health check failed: {str(e)}")
            return False

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.

        Current: Static list
        Future: Dynamic model discovery with capabilities
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                )

                if response.status_code == 200:
                    models_data = response.json()
                    return list(models_data.get("data", []))

        except Exception as e:
            logger.error(f"Failed to fetch models: {str(e)}")

        # Fallback to static list
        return [
            {
                "id": "anthropic/claude-3-haiku",
                "name": "Claude 3 Haiku",
                "description": "Fast, cost-effective model",
                "pricing": self.model_pricing.get("anthropic/claude-3-haiku"),
            },
            {
                "id": "anthropic/claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "description": "Balanced performance model",
                "pricing": self.model_pricing.get("anthropic/claude-3-sonnet"),
            },
            {
                "id": "openai/gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Fast GPT-4 with large context",
                "pricing": self.model_pricing.get("openai/gpt-4-turbo"),
            },
        ]

    # Private methods for enterprise functionality

    async def _execute_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request with enterprise retry logic.

        Current: Exponential backoff
        Future: Circuit breaker, jitter, provider fallback
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions", json=payload
                )

                if response.status_code == 200:
                    return dict(response.json())
                elif response.status_code == 429:
                    # Rate limit - exponential backoff
                    wait_time = (2**attempt) + (time.time() % 1)  # Add jitter
                    logger.warning(f"Rate limited, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Other HTTP errors
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    raise Exception(error_msg)

            except httpx.TimeoutException:
                last_exception = Exception(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                    continue
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                    continue

        raise last_exception or Exception("Max retries exceeded")

    def _calculate_cost(self, model: str, usage: Dict[str, Any]) -> float:
        """
        Calculate cost based on token usage.

        Current: Simple pricing calculation
        Future: Dynamic pricing, volume discounts, cost optimization
        """
        if model not in self.model_pricing:
            # Default pricing if model not found
            input_cost = 0.001
            output_cost = 0.002
        else:
            pricing = self.model_pricing[model]
            input_cost = pricing["input"]
            output_cost = pricing["output"]

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        total_cost = (input_tokens * input_cost / 1000) + (
            output_tokens * output_cost / 1000
        )
        return float(round(total_cost, 6))

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()


# Enterprise Provider Factory
class ProviderFactory:
    """
    Factory for creating AI providers.
    Future: Auto-discovery, health-based selection, cost optimization
    """

    @staticmethod
    def create_provider(provider_type: ProviderType) -> AIProviderInterface:
        """Create provider instance based on type"""
        providers = {
            ProviderType.OPENROUTER: OpenRouterProvider,
            # Future providers:
            # ProviderType.OPENAI: OpenAIProvider,
            # ProviderType.ANTHROPIC: AnthropicProvider,
            # ProviderType.AZURE_OPENAI: AzureOpenAIProvider,
        }

        if provider_type not in providers:
            raise ValueError(f"Provider {provider_type} not supported")

        return providers[provider_type]()

    @staticmethod
    def get_supported_providers() -> List[ProviderType]:
        """Get list of supported providers"""
        return [ProviderType.OPENROUTER]  # Will expand

    @staticmethod
    async def health_check_all() -> Dict[ProviderType, bool]:
        """Health check all providers for enterprise monitoring"""
        results = {}
        for provider_type in ProviderFactory.get_supported_providers():
            try:
                provider = ProviderFactory.create_provider(provider_type)
                results[provider_type] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider_type}: {str(e)}")
                results[provider_type] = False

        return results
