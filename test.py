from operations.connect_browser import connect_to_browser_and_page
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
async def test_click_city(city: str, port: int, target_url: str) -> None:
    browser: Browser
    page: Page
    browser, page = await connect_to_browser_and_page(target_url= "", target_title="题库平台", port=2001)
    await page.get_by_text(f"三亚市",exact=True).first.click()
    await browser.close()   # Playwright

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_click_city(city="三亚市", port=2001, target_url=""))
       # 等待子进程退出