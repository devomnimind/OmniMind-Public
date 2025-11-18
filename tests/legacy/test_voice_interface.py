import pytest

from DEVBRAIN_V23.sensory.voice_interface import VoiceInterface


class DummySTT:
    def __init__(self) -> None:
        self.calls: list[bytes] = []

    def transcribe(self, payload: bytes) -> dict:
        self.calls.append(payload)
        return {"text": payload.decode("utf-8") if payload else ""}


class DummyTTS:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, text: str) -> bytes:
        self.calls.append(text)
        return text.encode("utf-8")


@pytest.mark.asyncio
async def test_voice_interface_listen_and_speak() -> None:
    stt = DummySTT()
    tts = DummyTTS()
    recorded: list[bytes] = []
    vi = VoiceInterface(
        stt_client=stt,
        tts_client=tts,
        audio_provider=lambda: b"hi",
        audio_sink=recorded.append,
    )

    text = await vi.listen()
    assert text == "hi"
    await vi.speak("ack")
    assert recorded
    assert vi.metrics.listen_durations
    assert vi.metrics.speak_durations


@pytest.mark.asyncio
async def test_voice_interface_alerts_on_failure() -> None:
    class FailingSTT:
        def transcribe(self, _: bytes) -> dict:
            raise RuntimeError("boom")

    vi = VoiceInterface(stt_client=FailingSTT())

    with pytest.raises(RuntimeError):
        await vi.listen()

    assert vi.alerts
