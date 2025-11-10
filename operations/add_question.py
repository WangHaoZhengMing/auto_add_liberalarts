import asyncio
from asyncio.log import logger
import os
from anyio import sleep
from playwright.async_api import Browser, Page
from operations.add_and_click_tianjia import add_and_click_tianjia
from operations.connect_browser import connect_to_browser_and_page
from operations.download_page import question_page
from operations.model import questionData
import json
from typing import Any, Dict, List, Optional
from playwright.async_api import Response

async def add_question(page_data: question_page,page: Page,port:int) -> None:
    """Main function to automate paper entry process."""
    target_title: str = "题库平台 | 录排中心"
    
    logger.info("Starting automation process...")
    
    # 连接到浏览器并获取页面
    logger.info(f"Connecting to browser and navigating to: {target_title}")
    browser: Browser
    page: Page
    browser, page = await connect_to_browser_and_page(target_url="", target_title=target_title,port=port)
    logger.info("Successfully connected to browser")

    # 监听network数据包 text-search .request method post .get it's data list. and then similar_questions = data list.
    similar_questions_json: str = ""
    similar_question_class: Optional[Dict[str, Any]] = None

    async def on_response(response: Response) -> None:
        nonlocal similar_questions_json, similar_question_class
        # Log details for all responses to help with debugging
        logger.info(f"Response URL: {response.url}, Method: {response.request.method}, Status: {response.status}")
        if "text-search" in response.url and response.request.method == "POST":
            try:
                if response.ok:
                    # Store the raw JSON string from the response text.
                    similar_questions_json = await response.text()
                    # The user did not provide the JSON structure, so we cannot define a specific dataclass.
                    # We will parse the JSON into a generic Python object (dictionaries and lists).
                    similar_question_class = json.loads(similar_questions_json)
                    logger.info(f"Successfully intercepted and stored raw JSON string from {response.url}")
                else:
                    logger.error(f"Request to {response.url} failed with status {response.status}")
            except Exception as e:
                logger.error(f"Error processing response from {response.url}: {e}")

    page.on("response", on_response)

    logger.info("Network listener is active. Waiting for requests to 'text-search'...")

    await page.get_by_text("搜题添加").click()

    for i in range(len(page_data.stemlist)):
        stem_item: questionData = page_data.stemlist[i]
        # Clear the list for the current question before searching
        stem_item.origin_from_our_bank = []
        await page.get_by_placeholder("请输入题目ID或题目文本进行查询").fill(stem_item.stem)
        
        logger.info(f"Searching for question: {stem_item.stem}")
        try:
            # Use expect_response to wait for the search request to complete
            async with page.expect_response(lambda response: "text-search" in response.url and response.request.method == "POST", timeout=30000) as response_info:
                await page.get_by_role("button", name="search").click()
                response_value: Response = await response_info.value
                await sleep(0.5)
                logger.info(f"Search response received. Status: {response_value.status}")

            # After the response is received, the on_response handler has already processed it.
            # Give a moment for the UI to update.
            await page.wait_for_timeout(1000)

        except Exception as e:
            logger.error(f"Did not receive search response or an error occurred: {e}")
            logger.info("Pausing for debugging.")
        
        if similar_question_class and 'data' in similar_question_class:
            datas: List[Dict[str, Any]] = similar_question_class['data']
            for data_item in datas:
                source_name = data_item.get('sourceName')
                if source_name:
                    # Split the source_name string by comma to get a list of names
                    source_names_list = source_name.split(',')
                    # Add this list as an inner list to origin_from_our_bank
                    page_data.stemlist[i].origin_from_our_bank.append(source_names_list)
                    
        else:
            logger.warning("Could not find 'data' in the response or the response was not captured.")

        await add_and_click_tianjia(page)


    # 将 page_data 对象的内容保存为 JSON 文件
    output_dir = "detail"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{page_data.name}_full.json")
    file_path2 = os.path.join(output_dir, f"{page_data.name}core.json")
    # 将自定义对象序列化为JSON.
    # 类似于 Rust 的 Display/Debug trait，我们可以定义一个方法来控制对象的序列化表示。
    # 在 Python 中，这通常通过为 json.dump 提供一个 default 函数或编码器来实现。
    def default_serializer(obj):
        """A default JSON serializer for custom objects."""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, ensure_ascii=False, indent=4, default=default_serializer)
    
    logger.info(f"Successfully saved data to {file_path}")

    core_data = []
    for item in page_data.stemlist:
        first_origin = item.origin_from_our_bank[0] if item.origin_from_our_bank else None
        core_data.append({
            "origin": item.origin,
            "origin_from_our_bank": first_origin
        })

    with open(file_path2, 'w', encoding='utf-8') as f:
        json.dump(core_data, f, ensure_ascii=False, indent=4)

    logger.info(f"Successfully saved core data to {file_path2}")


    # 保持浏览器打开，便于调试
    await page.pause()
    await browser.close()
    logger.info("Browser closed")


if __name__ == "__main__":
    asyncio.run(add_question())
