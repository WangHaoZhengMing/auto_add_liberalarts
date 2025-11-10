import asyncio
from operations.pre_step import pre_process
from operations.add_question import add_question
from playwright.async_api import Browser, Page

from operations.download_page import download_page

async def main() -> None:

    # 目标页面URL
    target_url: str = "https://zujuan.xkw.com/1p2614592.html"
    from operations.connect_browser import connect_to_browser_and_page
    # 连接到浏览器并获取页面
    browser: Browser
    page: Page
    browser, page = await connect_to_browser_and_page(target_url,target_title="")

    page_data = await download_page(page)
    
    print(f"Page Name: {page_data.name}")
    print(f"Province: {page_data.province}")
    print(f"Grade: {page_data.grade}")
    print(f"Year: {page_data.year}")
    print(f"Subject: {page_data.subject}")
    print(f"Found {len(page_data.stemlist)} questions.")


    await pre_process(page=page,page_data=page_data)
    await add_question(page_data, page)




    # Keep browser open for debugging
    await page.pause()
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
