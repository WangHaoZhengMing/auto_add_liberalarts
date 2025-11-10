import asyncio
from playwright.async_api import Page

async def add_and_click_tianjia(page: Page) -> None:
    """
    Locates the '添加' button and clicks it using JavaScript.
    """
    # Locate the '添加' button
    add_button_locator = page.locator("div.btn:has-text('添加')").first

    # Use page.evaluate to execute a JavaScript click on the element
    await add_button_locator.evaluate("element => element.click()")

if __name__ == "__main__":
    asyncio.run(add_and_click_tianjia())

