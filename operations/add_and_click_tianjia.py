import asyncio
from playwright.async_api import Page, TimeoutError

async def add_and_click_tianjia(page: Page) -> None:
    """
    Locates the '添加' button and clicks it using JavaScript.
    Retries once after reloading if it times out.
    """
    try:
        # Locate the '添加' button
        add_button_locator = page.locator("div.btn:has-text('添加')").first

        # Use page.evaluate to execute a JavaScript click on the element with a timeout
        await asyncio.wait_for(add_button_locator.evaluate("element => element.click()"), timeout=5)
    except TimeoutError:
        print("Clicking the '添加' button timed out. Reloading and trying again.")
        await page.get_by_role("button", name="search").click()
        # Wait for the page to reload and try clicking again
        add_button_locator = page.locator("div.btn:has-text('添加')").first
        await add_button_locator.evaluate("element => element.click()")

if __name__ == "__main__":
    pass

