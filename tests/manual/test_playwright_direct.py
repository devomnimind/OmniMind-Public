import asyncio

from playwright.async_api import async_playwright


async def test_playwright_direct():
    """Test Playwright directly without pytest fixtures"""
    print("🚀 Starting Playwright...")
    playwright = await async_playwright().start()

    print("🌐 Launching browser...")
    browser = await playwright.chromium.launch(
        headless=True, args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )

    print("📄 Creating page...")
    page = await browser.new_page()

    print("📝 Setting content...")
    await page.set_content("<h1>Test OmniMind</h1><p>Working!</p>")

    print("🔍 Getting title...")
    title = await page.title()
    print(f"Title: '{title}'")

    print("🔍 Getting h1...")
    h1 = await page.locator("h1").text_content()
    print(f"H1: '{h1}'")

    print("✅ Assertions...")
    assert (
        "OmniMind" in title or title == ""
    ), f"Title should contain OmniMind or be empty, got: {title}"
    assert h1 == "Test OmniMind", f"H1 should be 'Test OmniMind', got: {h1}"

    print("🧹 Cleaning up...")
    await page.close()
    await browser.close()
    await playwright.stop()

    print("🎉 Test passed!")
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_playwright_direct())
        print("✅ SUCCESS: Playwright works in this environment!")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
