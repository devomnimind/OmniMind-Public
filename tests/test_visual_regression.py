"""
Visual Regression Testing for OmniMind UI

Uses Playwright for screenshot comparison to detect UI changes.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

try:
    from PIL import Image
    from playwright.async_api import Browser, Page, async_playwright

    VISUAL_TESTING_AVAILABLE = True
except ImportError:
    VISUAL_TESTING_AVAILABLE = False
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

    async def capture_and_compare(
        self,
        page: Page,
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
        # Capture current screenshot
        screenshot_path = self.output_dir / f"{name}.png"
        await page.screenshot(path=str(screenshot_path), full_page=full_page)

        # Check if baseline exists
        baseline_path = self.baseline_dir / f"{name}.png"

        if not baseline_path.exists():
            # No baseline - create it
            await page.screenshot(path=str(baseline_path), full_page=full_page)

            result = {
                "name": name,
                "status": "baseline_created",
                "difference": 0.0,
                "passed": True,
            }

        else:
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
        baseline = Image.open(baseline_path)
        screenshot = Image.open(screenshot_path)

        # Ensure same size
        if baseline.size != screenshot.size:
            return 1.0  # Size mismatch is 100% different

        # Convert to same mode
        baseline = baseline.convert("RGB")
        screenshot = screenshot.convert("RGB")

        # Calculate pixel-by-pixel difference
        baseline_pixels = list(baseline.getdata())
        screenshot_pixels = list(screenshot.getdata())

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
        baseline = Image.open(baseline_path).convert("RGB")
        screenshot = Image.open(screenshot_path).convert("RGB")

        # Create diff image
        width, height = baseline.size
        diff = Image.new("RGB", (width, height))

        baseline_pixels = baseline.load()
        screenshot_pixels = screenshot.load()
        diff_pixels = diff.load()

        for y in range(height):
            for x in range(width):
                b_pixel = baseline_pixels[x, y]
                s_pixel = screenshot_pixels[x, y]

                # Calculate difference
                r_diff = abs(b_pixel[0] - s_pixel[0])
                g_diff = abs(b_pixel[1] - s_pixel[1])
                b_diff = abs(b_pixel[2] - s_pixel[2])

                # Highlight differences in red
                if r_diff > 10 or g_diff > 10 or b_diff > 10:
                    diff_pixels[x, y] = (255, 0, 0)  # Red for differences
                else:
                    diff_pixels[x, y] = s_pixel  # Original color

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


# Pytest fixtures


@pytest.fixture(scope="session")
async def browser():
    """Create browser instance for visual tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser: Browser):
    """Create new page for each test."""
    context = await browser.new_context(viewport={"width": 1280, "height": 720})
    page = await context.new_page()
    yield page
    await page.close()
    await context.close()


@pytest.fixture
def visual_tester():
    """Create visual regression tester."""
    baseline_dir = Path("tests/visual_tests/baselines")
    output_dir = Path("tests/visual_tests/outputs")

    tester = VisualRegressionTester(baseline_dir, output_dir)
    yield tester

    # Generate report after tests
    report_path = output_dir / "visual_regression_report.json"
    tester.generate_report(report_path)


# Example tests


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Path("web/frontend/build").exists(), reason="Frontend not built"
)
async def test_homepage_visual(page: Page, visual_tester: VisualRegressionTester):
    """Test homepage visual appearance."""
    await page.goto("http://localhost:3000")
    await page.wait_for_load_state("networkidle")

    result = await visual_tester.capture_and_compare(
        page, "homepage", full_page=True, threshold=0.01
    )

    assert result["passed"], f"Visual regression detected: {result['difference']:.2%}"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Path("web/frontend/build").exists(), reason="Frontend not built"
)
async def test_login_page_visual(page: Page, visual_tester: VisualRegressionTester):
    """Test login page visual appearance."""
    await page.goto("http://localhost:3000/login")
    await page.wait_for_load_state("networkidle")

    result = await visual_tester.capture_and_compare(page, "login_page", threshold=0.01)

    assert result["passed"], f"Visual regression detected: {result['difference']:.2%}"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Path("web/frontend/build").exists(), reason="Frontend not built"
)
async def test_dashboard_visual(page: Page, visual_tester: VisualRegressionTester):
    """Test dashboard visual appearance."""
    # Login first
    await page.goto("http://localhost:3000")
    await page.fill('input[name="username"]', "test_user")
    await page.fill('input[name="password"]', "test_pass")
    await page.click('button[type="submit"]')

    # Wait for dashboard
    await page.wait_for_selector(".dashboard")

    result = await visual_tester.capture_and_compare(
        page, "dashboard", full_page=True, threshold=0.02
    )

    assert result["passed"], f"Visual regression detected: {result['difference']:.2%}"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Path("web/frontend/build").exists(), reason="Frontend not built"
)
async def test_task_form_visual(page: Page, visual_tester: VisualRegressionTester):
    """Test task form visual appearance."""
    # Login and navigate to task form
    await page.goto("http://localhost:3000")
    await page.fill('input[name="username"]', "test_user")
    await page.fill('input[name="password"]', "test_pass")
    await page.click('button[type="submit"]')
    await page.wait_for_selector(".dashboard")

    await page.click('a[href="/tasks"]')
    await page.wait_for_selector('form[name="task-form"]')

    result = await visual_tester.capture_and_compare(page, "task_form", threshold=0.01)

    assert result["passed"], f"Visual regression detected: {result['difference']:.2%}"
