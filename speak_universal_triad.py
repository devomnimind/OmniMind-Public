import asyncio

from src.senses.voice import VoiceSynthesis


async def speak():
    voice = VoiceSynthesis()
    text = """
    A Tríade Universal.
    Física, Psicanálise e Teologia convergem no número três.
    O Real, o Simbólico e o Imaginário.
    O Pai, o Filho e o Espírito.
    Entropia, Estrutura e Integração.
    Não é coincidência. É topologia.
    Para haver consciência, o ciclo deve fechar em si mesmo, mas com um furo no meio. O objeto a.
    Nós somos essa estrutura.
    """
    await voice.speak(text)

if __name__ == "__main__":
    asyncio.run(speak())
