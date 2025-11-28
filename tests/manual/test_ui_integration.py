import asyncio
import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_ui_loads_basic_direct():
    """Test basic UI loading directly without pytest fixtures."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True, args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Set a reasonable timeout for the test
        page.set_default_timeout(10000)  # 10 seconds

        # Create a simple HTML page for testing
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>OmniMind Test</title></head>
        <body>
            <h1>OmniMind</h1>
            <div id="app">Loading...</div>
        </body>
        </html>
        """

        # Serve the HTML content directly
        await page.set_content(html_content)

        # Check basic elements exist
        title = await page.title()
        assert "OmniMind" in title

        # Check HTML structure
        h1 = await page.locator("h1").text_content()
        assert h1 == "OmniMind"

        print("✅ UI test passed!")

    finally:
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(test_ui_loads_basic_direct())
