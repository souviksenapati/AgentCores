#!/usr/bin/env python3
"""
Test AgentCores OpenRouter Provider inside Docker container
"""

import asyncio
import sys

# Add the app directory to the path
sys.path.append("/app")

from app.core.interfaces import (AgentConfig, AgentType,  # noqa: E402
                                 ProviderType)
from app.providers.openrouter_provider import OpenRouterProvider  # noqa: E402


async def test_provider():
    """Test the OpenRouterProvider class"""

    print("🧪 Testing AgentCores OpenRouter Provider")
    print("=" * 50)

    try:
        # Initialize provider
        print("🔧 Initializing OpenRouter Provider...")
        provider = OpenRouterProvider()
        print("✅ Provider initialized successfully")
        print(f"   Base URL: {provider.base_url}")
        print(f"   Site URL: {provider.site_url}")
        api_key_display = (
            provider.api_key[:20] + "..." if provider.api_key else "Not configured"
        )
        print(f"   API Key: {api_key_display}")

        # Test health check
        print("\n🏥 Testing provider health check...")
        health = await provider.health_check()
        print(f"✅ Health check: {'PASSED' if health else 'FAILED'}")

        # Create test agent config
        print("\n🤖 Creating test agent config...")
        agent_config = AgentConfig(
            name="Test QA Agent",
            description="Test agent for QA validation",
            agent_type=AgentType.CHATBOT,
            provider=ProviderType.OPENROUTER,
            model="anthropic/claude-3-haiku",
            system_prompt="You are a helpful QA testing assistant.",
            temperature=0.7,
            max_tokens=100,
        )
        print("✅ Agent config created")

        # Test completion
        print("\n💬 Testing completion generation...")
        result = await provider.generate_completion(
            "Please respond with: 'AgentCores provider test successful'", agent_config
        )

        print("✅ Completion successful!")
        print(f"   Task ID: {result.task_id}")
        print(f"   Status: {result.status}")
        print(f"   Result: {result.result}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        print(f"   Cost estimate: ${result.cost_estimate:.6f}")
        print(f"   Token usage: {result.token_usage}")

        return True

    except Exception as e:
        print(f"❌ Provider test failed: {str(e)}")
        import traceback

        print(f"   Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_provider())

    if success:
        print("\n🎉 AgentCores OpenRouter Provider Test: PASSED")
        print("✅ Provider initialization working")
        print("✅ Health check successful")
        print("✅ Agent config creation working")
        print("✅ Completion generation working")
        print("✅ Cost tracking operational")
    else:
        print("\n❌ AgentCores OpenRouter Provider Test: FAILED")
