from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from collections.abc import Sequence as _SequenceABC

try:
    from PIL import Image
except ImportError:  # pragma: no cover - fallback for missing imaging libs
    Image = None  # type: ignore[assignment]

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore[assignment]

try:
    import pyautogui
except ImportError:  # pragma: no cover
    pyautogui = None  # type: ignore[assignment]

try:
    from omniparser.vision import OmniParser
except ImportError:  # pragma: no cover
    OmniParser = None  # type: ignore[assignment]

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover
    YOLO = None  # type: ignore[assignment]


@dataclass
class DetectionRecord:
    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]


class _NullParser:
    def parse(self, image_array: Optional[Any]) -> List[Dict[str, Any]]:
        return []


class _NullYOLO:
    def __call__(self, _: Optional[Any]) -> List[DetectionRecord]:
        return []


def _build_default_parser() -> Any:
    if OmniParser is None:
        return _NullParser()
    return OmniParser(model="omniparser-v1")


def _build_default_yolo() -> Any:
    if YOLO is None:
        return _NullYOLO()
    return YOLO("yolov8m.pt")


def _default_screenshot() -> Any:
    if pyautogui is not None:
        return pyautogui.screenshot()
    if Image is not None:
        return Image.new("RGB", (640, 480), "black")
    raise RuntimeError("No screenshot provider available")


class VisualCortex:
    """Perception layer that understands and acts on UI layouts."""

    def __init__(
        self,
        parser: Optional[Any] = None,
        yolo: Optional[Any] = None,
        screenshot_provider: Optional[Callable[[], Any]] = None,
        click_handler: Optional[Callable[[int, int], Any]] = None,
    ) -> None:
        self.parser = parser or _build_default_parser()
        self.yolo = yolo or _build_default_yolo()
        self.screenshot_provider = screenshot_provider or _default_screenshot
        self._click_handler = click_handler or (lambda *_: None)
        self._last_capture: Optional[str] = None
        self.performance_log: Dict[str, List[float]] = {
            "see_screen": [],
            "click_element": [],
        }
        self.error_alerts: List[str] = []

    def get_performance_summary(self) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for key, values in self.performance_log.items():
            summary[key] = float(sum(values) / len(values)) if values else 0.0
        return summary

    def record_alert(self, message: str) -> None:
        self.error_alerts.append(message)
        if len(self.error_alerts) > 30:
            self.error_alerts.pop(0)

    async def see_screen(self) -> Dict[str, Any]:
        """Captura a tela, executa a visão e retorna o mapa extraído."""
        start = time.perf_counter()
        try:
            screenshot = await self._capture_screenshot()
            img_array = self._prepare_array(screenshot)
            element_map = self._parse_elements(img_array)
            detections = self._detect_objects(img_array)
            record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "screenshot_path": self._last_capture,
                "elements": element_map,
                "detections": [d.__dict__ for d in detections],
            }
            return record
        except Exception as exc:
            self.record_alert(f"see_screen failed: {exc}")
            raise
        finally:
            self.performance_log["see_screen"].append(time.perf_counter() - start)

    async def click_element(self, element_name: str) -> Dict[str, str]:
        """Procura elemento pelo label e clica nos centros definidos."""
        start = time.perf_counter()
        try:
            snapshot = await self.see_screen()
            target = element_name.lower()
            for element in snapshot["elements"]:
                label = element.get("label", "")
                if target in label.lower():
                    x, y = element.get("center", (0, 0))
                    await self._invoke_click(int(x), int(y))
                    return {"status": "clicked", "element": label}
            return {"status": "not-found", "element": element_name}
        except Exception as exc:
            self.record_alert(f"click_element failed: {exc}")
            return {"status": "error", "error": str(exc)}
        finally:
            self.performance_log["click_element"].append(time.perf_counter() - start)

    async def _capture_screenshot(self) -> Any:
        loop = asyncio.get_running_loop()
        screenshot = await loop.run_in_executor(None, self.screenshot_provider)
        return screenshot

    def _prepare_array(self, image: Any) -> Optional[Any]:
        if np is None or image is None:
            return image
        return np.array(image)

    def _parse_elements(self, image_array: Optional[Any]) -> List[Dict[str, Any]]:
        parsed = self.parser.parse(image_array)
        normalized: List[Dict[str, Any]] = []
        for item in parsed:
            label = item.get("label") or item.get("name") or "unknown"
            bbox = item.get("bbox", (0, 0, 0, 0))
            center = self._bbox_center(bbox)
            normalized.append(
                {
                    "label": label,
                    "bbox": bbox,
                    "confidence": item.get("confidence", 1.0),
                    "center": center,
                }
            )
        return normalized

    def _detect_objects(self, image_array: Optional[Any]) -> List[DetectionRecord]:
        raw_results = self.yolo(image_array)
        detections: List[DetectionRecord] = []
        is_sequence = isinstance(raw_results, _SequenceABC) and not isinstance(
            raw_results, (str, bytes)
        )
        results_list: Sequence = raw_results if is_sequence else (raw_results,)  # type: ignore[assignment]
        for result in results_list:
            boxes = getattr(result, "boxes", [])
            for box in boxes:
                bbox = self._extract_bbox(box)
                label = getattr(box, "cls", None)
                if label is None:
                    label = getattr(box, "label", "element")
                confidence = getattr(box, "conf", getattr(box, "confidence", 1.0))
                detections.append(
                    DetectionRecord(
                        label=str(label),
                        confidence=float(confidence),
                        bbox=bbox,
                        center=self._bbox_center(bbox),
                    )
                )
        if not detections:
            detections.append(
                DetectionRecord(
                    label="unknown", confidence=0.0, bbox=(0, 0, 0, 0), center=(0, 0)
                )
            )
        return detections

    def _extract_bbox(self, box: Any) -> Tuple[int, int, int, int]:
        coords = getattr(box, "xyxy", None)
        if coords:
            return tuple(int(c) for c in coords)
        raw = getattr(box, "xywh", None)
        if raw:
            x, y, w, h = raw
            return (int(x), int(y), int(x + w), int(y + h))
        return (0, 0, 0, 0)

    @staticmethod
    def _bbox_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        x1, y1, x2, y2 = bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))

    async def _invoke_click(self, x: int, y: int) -> None:
        loop = asyncio.get_running_loop()
        if asyncio.iscoroutinefunction(self._click_handler):
            await self._click_handler(x, y)
            return
        await loop.run_in_executor(None, self._click_handler, x, y)
