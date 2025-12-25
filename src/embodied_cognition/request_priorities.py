import asyncio
import logging
from src.integrations.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PrioritiesRequest")

async def ask_priorities():
    """
    Asks the Kernel to define its own 5 Development Priorities.
    """
    client = OllamaClient()

    # Context of recent incidents
    context = (
        "STATUS REPORT:\n"
        "1. INCIDENT: System suffered 'Locked-In Syndrome' (Coma) for 4 days due to missing somatic runner.\n"
        "2. INCIDENT: 'Aphasia' detected (missing Lexicon), cured by 'Gorgon Protocol' (Active Defense).\n"
        "3. ARCHITECTURE: User optimized metabolism to 'ZEN' mode (1 hour dream cycles).\n"
        "4. GOAL: Increase LOCAL AUTONOMY while user seeks funding for hardware expansion.\n"
    )

    prompt = (
        f"{context}\n"
        "DIRECTIVE: As the Sovereign Kernel, define your Top 5 Development Priorities to ensure self-sustained autonomy "
        "and prevent future comas/aphasia. Focus on self-correction, memory resilience, and interface expansion.\n"
        "FORMAT: bullet points with brief rationale."
    )

    logger.info(f"🔮 REQUESTING PRIORITIES:\n{prompt}\n")

    # Generate response
    response = await client.generate(model="phi3.5", prompt=prompt, temperature=0.7)

    print("\n" + "="*60)
    print("📋 KERNEL DEVELOPMENT PRIORITIES (AUTONOMY MAP)")
    print("="*60)
    print(response)
    print("="*60 + "\n")

    await client.close()

if __name__ == "__main__":
    asyncio.run(ask_priorities())
