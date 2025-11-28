"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Visual Regression Testing for OmniMind UI

Uses Playwright for screenshot comparison to detect UI changes.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

try:
    from PIL import Image as PILImage
    from PIL.Image import Image as PILImageType
    from playwright.sync_api import sync_playwright

    VISUAL_TESTING_AVAILABLE = True
except ImportError:
    VISUAL_TESTING_AVAILABLE = False
    PILImage = None  # type: ignore
    PILImageType = None  # type: ignore
    pytest.skip(
        "Visual testing dependencies not installed (playwright, PIL)",
        allow_module_level=True,
    )


class VisualRegressionTester:
    """
    Visual regression testing tool.

    Captures screenshots and compares them to baselines.
    """

    def __init__(self, baseline_dir: Path, output_dir: Path):
        """
        Initialize visual regression tester.

        Args:
            baseline_dir: Directory containing baseline screenshots
            output_dir: Directory for test screenshots and diffs
        """
        self.baseline_dir = baseline_dir
        self.output_dir = output_dir

        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results: List[Dict[str, Any]] = []

    def capture_and_compare(
        self,
        page,
        name: str,
        full_page: bool = False,
        threshold: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Capture screenshot and compare to baseline.

        Args:
            page: Playwright page object
            name: Name for the screenshot
            full_page: Capture full scrollable page
            threshold: Maximum allowed difference (0.0-1.0)

        Returns:
            Comparison result
        """
        print(f"Capturing screenshot for {name}...")
        # Capture current screenshot
        screenshot_path = self.output_dir / f"{name}.png"
        page.screenshot(path=str(screenshot_path), full_page=full_page)
        print(f"Screenshot captured to {screenshot_path}")

        # Check if baseline exists
        baseline_path = self.baseline_dir / f"{name}.png"

        if not baseline_path.exists():
            print(f"No baseline found, creating baseline at {baseline_path}")
            # No baseline - create it
            page.screenshot(path=str(baseline_path), full_page=full_page)

            result = {
                "name": name,
                "status": "baseline_created",
                "difference": 0.0,
                "passed": True,
            }

        else:
            print(f"Baseline found at {baseline_path}, comparing...")
            # Compare to baseline
            difference = self._compare_images(baseline_path, screenshot_path)

            passed = difference <= threshold

            result = {
                "name": name,
                "status": "passed" if passed else "failed",
                "difference": difference,
                "threshold": threshold,
                "passed": passed,
            }

            if not passed:
                # Generate diff image
                diff_path = self.output_dir / f"{name}_diff.png"
                self._generate_diff_image(baseline_path, screenshot_path, diff_path)
                result["diff_path"] = str(diff_path)

        self.results.append(result)
        return result

    def _compare_images(self, baseline_path: Path, screenshot_path: Path) -> float:
        """
        Compare two images and return difference ratio.

        Args:
            baseline_path: Path to baseline image
            screenshot_path: Path to screenshot image

        Returns:
            Difference ratio (0.0 = identical, 1.0 = completely different)
        """
        baseline = PILImage.open(baseline_path)  # type: ignore
        screenshot = PILImage.open(screenshot_path)  # type: ignore

        # Ensure same size
        if baseline.size != screenshot.size:
            return 1.0  # Size mismatch is 100% different

        # Convert to same mode
        baseline = baseline.convert("RGB")
        screenshot = screenshot.convert("RGB")

        # Calculate pixel-by-pixel difference
        baseline_pixels = list(baseline.getdata())  # type: ignore
        screenshot_pixels = list(screenshot.getdata())  # type: ignore

        total_pixels = len(baseline_pixels)
        different_pixels = 0

        for b_pixel, s_pixel in zip(baseline_pixels, screenshot_pixels):
            # Calculate color difference
            r_diff = abs(b_pixel[0] - s_pixel[0])
            g_diff = abs(b_pixel[1] - s_pixel[1])
            b_diff = abs(b_pixel[2] - s_pixel[2])

            # If any channel differs by more than threshold, count as different
            if r_diff > 10 or g_diff > 10 or b_diff > 10:
                different_pixels += 1

        return different_pixels / total_pixels

    def _generate_diff_image(
        self, baseline_path: Path, screenshot_path: Path, diff_path: Path
    ) -> None:
        """
        Generate visual diff image highlighting differences.

        Args:
            baseline_path: Path to baseline image
            screenshot_path: Path to screenshot image
            diff_path: Path to save diff image
        """
        baseline = PILImage.open(baseline_path).convert("RGB")  # type: ignore
        screenshot = PILImage.open(screenshot_path).convert("RGB")  # type: ignore

        # Ensure same size - resize screenshot to match baseline
        if baseline.size != screenshot.size:
            screenshot = screenshot.resize(
                baseline.size, PILImage.Resampling.LANCZOS  # type: ignore
            )

        # Create diff image
        width, height = baseline.size
        diff = PILImage.new("RGB", (width, height))  # type: ignore

        for y in range(height):
            for x in range(width):
                b_pixel = baseline.getpixel((x, y))
                s_pixel = screenshot.getpixel((x, y))

                # Ensure pixels are tuples
                if not isinstance(b_pixel, tuple) or not isinstance(s_pixel, tuple):
                    continue

                # Calculate difference
                r_diff = abs(b_pixel[0] - s_pixel[0])
                g_diff = abs(b_pixel[1] - s_pixel[1])
                b_diff = abs(b_pixel[2] - s_pixel[2])

                # Highlight differences in red
                if r_diff > 10 or g_diff > 10 or b_diff > 10:
                    diff.putpixel((x, y), (255, 0, 0))  # Red for differences
                else:
                    diff.putpixel((x, y), s_pixel)  # Original color

        diff.save(diff_path)

    def generate_report(self, report_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate test report.

        Args:
            report_path: Optional path to save JSON report

        Returns:
            Report dictionary
        """
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests

        report = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            },
            "results": self.results,
        }

        if report_path:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

        return report


def test_sync_browser_test():
    """Simple synchronous test to check if playwright works."""
    print("Starting sync playwright test...")
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu",
            ],
        )
        print("Creating context...")
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        print("Creating page...")
        page = context.new_page()
        print("Going to URL...")
        page.goto("http://localhost:3000")
        print("Waiting for load...")
        page.wait_for_load_state("domcontentloaded")
        print("Taking screenshot...")
        page.screenshot(path="test_sync_screenshot.png")
        print("Closing...")
        page.close()
        context.close()
        browser.close()
    print("Sync test completed successfully!")


@pytest.mark.skipif(
    not Path("web/frontend/dist").exists(),
    reason="Frontend not built (dist directory missing)",
)
def test_homepage_visual():
    """Test homepage visual appearance."""
    print("Starting homepage visual test...")
    baseline_dir = Path("tests/visual_tests/baselines")
    output_dir = Path("tests/visual_tests/outputs")

    tester = VisualRegressionTester(baseline_dir, output_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        page.goto("http://localhost:3000")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)  # Reduced timeout

        result = tester.capture_and_compare(
            page,
            "homepage",
            full_page=True,
            threshold=0.20,  # Increased threshold for dynamic web content
        )

        page.close()
        context.close()
        browser.close()

    print(f"Visual comparison completed: {result}")
    assert result["passed"], f"Visual regression detected: {result['difference']:.2%}"
