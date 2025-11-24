import asyncio
from .pre_step import pre_process
from .add_question import add_question
from playwright.async_api import Browser, Page
import aiohttp
from urllib.parse import quote
from .download_page import download_page
from .ask_llm import ask_llm
import os

async def core(target_url: str,target_title: str,port: int) -> None:

    # 目标页面URL
    from .connect_browser import connect_to_browser_and_page
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

    if not await check_paper_exists(page, target_title):
        print("Paper does not exist. Proceeding with entry...")
        await pre_process(page=page,page_data=page_data,port=port)
        await add_question(page_data, page,port)

        

    else:
        print("Paper already exists. Skipping entry.")
        # Keep browser open for debugging
        await page.pause()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(core())


async def check_paper_exists(page: Page, paper_title: str) -> bool:
    encoded_paper_name = quote(paper_title)
    check_url = f"https://tps-tiku-api.staff.xdf.cn/paper/check/paperName?paperName={encoded_paper_name}&operationType=1&paperId="
    try:
        # Use page's context to make the request, bypassing CORS issues.
        api_response = await page.context.request.get(check_url)
        data = await api_response.json()
        print(data)
        if data.get("data", {}).get("repeated"):
            log_file_path = os.path.join(os.path.dirname(__file__), '..', 'other', '重复.txt')
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(paper_title + '\n')
            return True
    except Exception as e:
        print(f"API request failed for '{paper_title}': {e}")
    return False