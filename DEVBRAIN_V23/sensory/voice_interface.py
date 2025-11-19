from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

try:
    import whisper
except ImportError:  # pragma: no cover
    whisper = None

try:
    from TTS.api import TTS
except ImportError:  # pragma: no cover
    TTS = None


class _NullSTT:
    def transcribe(self, *args: Any, **kwargs: Any) -> Dict[str, str]:
        return {"text": ""}


class _NullTTS:
    def __call__(self, text: str, **kwargs: Any) -> bytes:
        return text.encode("utf-8")


@dataclass
class VoiceMetrics:
    listen_durations: List[float]
    speak_durations: List[float]


class VoiceInterface:
    def __init__(
        self,
        stt_client: Optional[Any] = None,
        tts_client: Optional[Any] = None,
        audio_provider: Optional[Callable[[], bytes]] = None,
        audio_sink: Optional[Callable[[bytes], None]] = None,
    ) -> None:
        self._stt = stt_client or self._create_stt()
        self._tts = tts_client or self._create_tts()
        self.audio_provider = audio_provider or (lambda: b"")
        self.audio_sink = audio_sink or (lambda _: None)
        self.metrics = VoiceMetrics(listen_durations=[], speak_durations=[])
        self.alerts: List[str] = []

    def _create_stt(self) -> Any:
        if not whisper:
            return _NullSTT()
        try:
            return whisper.load_model("tiny.en")
        except Exception:  # pragma: no cover
            return _NullSTT()

    def _create_tts(self) -> Any:
        if not TTS:
            return _NullTTS()
        try:
            return TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        except Exception:  # pragma: no cover
            return _NullTTS()

    async def listen(self, audio_path: Optional[str] = None) -> str:
        start = time.perf_counter()
        try:
            if audio_path:
                result = self._stt.transcribe(audio_path)
            else:
                audio_bytes = self.audio_provider()
                result = self._stt.transcribe(audio_bytes)
            return result.get("text", "")
        except Exception as exc:
            self._record_alert(f"listen failure: {exc}")
            raise
        finally:
            self.metrics.listen_durations.append(time.perf_counter() - start)

    async def speak(self, text: str) -> None:
        start = time.perf_counter()
        try:
            output = await self._emit_audio(text)
            self.audio_sink(output)
        except Exception as exc:
            self._record_alert(f"speak failure: {exc}")
            raise
        finally:
            self.metrics.speak_durations.append(time.perf_counter() - start)

    async def _emit_audio(self, text: str) -> bytes:
        if asyncio.iscoroutinefunction(self._tts):
            return await self._tts(text)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._tts, text)

    def _record_alert(self, message: str) -> None:
        self.alerts.append(message)
        if len(self.alerts) > 20:
            self.alerts.pop(0)
