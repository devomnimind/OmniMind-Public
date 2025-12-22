import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.llm_router import WatsonXProvider, LLMConfig, LLMProvider, LLMModelTier

load_dotenv()


async def test_watsonx():
    print("Testing WatsonXProvider...")
    provider = WatsonXProvider()

    if not provider.is_available():
        print("❌ WatsonX Provider reports NOT available")
        return

    print("✅ WatsonX Provider is available")

    config = LLMConfig(
        provider=LLMProvider.WATSONX,
        model_name="meta-llama/llama-3-3-70b-instruct",
        max_tokens=60,
        temperature=0.7,
    )

    print("Invoking generation...")
    response = await provider.invoke("Explain quantum entanglement briefly.", config)

    if response.success:
        print(f"✅ Success! Latency: {response.latency_ms}ms")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Failed: {response.error}")


if __name__ == "__main__":
    asyncio.run(test_watsonx())
