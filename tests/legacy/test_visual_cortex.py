import asyncio
from types import SimpleNamespace

import pytest

from DEVBRAIN_V23.sensory.visual_cortex import VisualCortex


class DummyParser:
    def parse(self, _: object) -> list[dict]:
        return [{"label": "Submit", "bbox": (10, 10, 40, 40), "confidence": 0.99}]


class DummyBox:
    def __init__(self) -> None:
        self.xyxy = (5, 5, 20, 20)
        self.cls = "button"
        self.conf = 0.8


class DummyYOLO:
    def __call__(self, _: object) -> list[SimpleNamespace]:
        box = DummyBox()
        return [SimpleNamespace(boxes=[box])]


@pytest.mark.asyncio
async def test_see_screen_records_elements_and_metrics() -> None:
    cortex = VisualCortex(
        parser=DummyParser(), yolo=DummyYOLO(), screenshot_provider=lambda: object()
    )
    summary = await cortex.see_screen()

    assert summary["elements"]
    assert summary["detections"]
    assert cortex.get_performance_summary()["see_screen"] >= 0


@pytest.mark.asyncio
async def test_click_element_hits_handler() -> None:
    captured: list[tuple[int, int]] = []

    async def handler(x: int, y: int) -> None:
        captured.append((x, y))

    cortex = VisualCortex(
        parser=DummyParser(),
        yolo=DummyYOLO(),
        screenshot_provider=lambda: object(),
        click_handler=handler,
    )

    result = await cortex.click_element("Submit")

    assert result["status"] == "clicked"
    assert captured
    assert cortex.get_performance_summary()["click_element"] >= 0


@pytest.mark.asyncio
async def test_click_element_alerts_on_failure() -> None:
    def broken_screen() -> None:
        raise RuntimeError("boom")

    cortex = VisualCortex(
        parser=DummyParser(),
        yolo=DummyYOLO(),
        screenshot_provider=broken_screen,
        click_handler=lambda *_: None,
    )

    result = await cortex.click_element("Submit")

    assert result["status"] == "error"
    assert cortex.error_alerts
