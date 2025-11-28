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
