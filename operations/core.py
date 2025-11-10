import asyncio
from operations.pre_step import pre_process
from operations.add_question import add_question
from playwright.async_api import Browser, Page

from operations.download_page import download_page

async def core(target_url: str,target_title: str,port: int) -> None:

    # 目标页面URL
    from operations.connect_browser import connect_to_browser_and_page
    # 连接到浏览器并获取页面
    browser: Browser
    page: Page
    browser, page = await connect_to_browser_and_page(target_url,target_title=target_title,port=port)

    page_data = await download_page(page)
    
    print(f"Page Name: {page_data.name}")
    print(f"Province: {page_data.province}")
    print(f"Grade: {page_data.grade}")
    print(f"Year: {page_data.year}")
    print(f"Subject: {page_data.subject}")
    print(f"Found {len(page_data.stemlist)} questions.")


    await pre_process(page=page,page_data=page_data,port=port)
    await add_question(page_data, page,port)




    # Keep browser open for debugging
    await page.pause()
    await browser.close()


if __name__ == "__main__":
    asyncio.run(core())
