import asyncio
import logging
import os
from playwright.async_api import Browser, Page
from .connect_browser import connect_to_browser_and_page
from .download_page import question_page
from .model import question_page, questionData, provinces
from .send_xchatbot import ask_xchatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def pre_process(page_data:question_page,page: Page,port:int) -> None:
    """Main function to automate paper entry process."""
    # 目标页面URL
    target_url: str = "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate"
    
    logger.info("Starting automation process...")
    
    # 连接到浏览器并获取页面
    logger.info(f"Connecting to browser and navigating to: {target_url}")
    browser: Browser
    page: Page
    browser, page = await connect_to_browser_and_page(target_url, target_title="题库平台", port=port)
    logger.info("Successfully connected to browser")

    await page.reload()
    await asyncio.sleep(1)
    
    # 新建试卷
    logger.info("Creating new paper...")
    await page.locator('button:has-text("新建试卷")').click()
    logger.info("Clicked '新建试卷'")
    
    # 选择OCR录入
    logger.info("Selecting 手工录入 entry method...")
    await page.locator('div.enter-btn:has-text("手工录入")').click()
    logger.info("Clicked '手工录入'")


    logger.info("Uploading PDF file...")
    await upload_pdf(page, page_data)


    logger.info(f"Entering paper name: {page_data.name}")
    await page.get_by_placeholder("请输入试卷名称", exact=True).fill(page_data.name)
    logger.info("Paper name entered successfully")
    await asyncio.sleep(1)
    # 选择学科
    logger.info("Selecting subject...")
    await page.get_by_title("语文") .click()
    logger.info("Clicked subject dropdown")
    await asyncio.sleep(1)
    await page.get_by_role("option", name=page_data.subject, exact=True).click()
    logger.info(f"Selected subject: {page_data.subject}")
    await asyncio.sleep(1)
    # 选择试卷类型
    logger.info("Selecting paper type...")
    await page.get_by_placeholder("选择试卷类型").click()
    logger.info("Opened paper type dropdown")
    await asyncio.sleep(1)
    await page.get_by_text("新东方自研").click()
    logger.info("Selected: 新东方自研")
    await asyncio.sleep(1)
    await page.get_by_title("教辅", exact=True).click()
    logger.info("Selected: 教辅")
    
    # 选择机构
    logger.info("Selecting institution...")
    await page.get_by_text("选择机构").click()
    logger.info("Opened institution dropdown")
    await asyncio.sleep(1)
    await page.get_by_role("option", name="集团").click()
    logger.info("Selected institution: 集团")
    
    # 选择试卷年份
    logger.info("Selecting paper year...")
    await page.get_by_text("选择试卷年份").click()
    logger.info("Opened year dropdown")
 
    await page.get_by_text(str(page_data.year), exact=True).click()
    logger.info(f"Selected year: {page_data.year}")

    
    # 选择年级
    logger.info("Selecting grade...")
    await page.get_by_text("选择年级").click()
    logger.info("Opened grade dropdown")
    await page.get_by_role("option", name=page_data.grade, exact=True).click()
    logger.info(f"Selected grade: {page_data.grade}")

    # 加入市
    logger.info("Selecting province...")
    city = await get_city_from_llm(page_data.name,page=page)
    browser, page = await connect_to_browser_and_page(target_url, target_title="题库平台", port=port)
    if not city == "":
        try:
            await page.get_by_text("添加市").click()
            await page.get_by_text("全国",exact=True).click()
            await page.get_by_text(f"{page_data.province}省",exact=True).click()
            await asyncio.sleep(0.5)
            await page.get_by_text(f"{city.strip("'\"")}",exact=True).first.click()
            await page.get_by_role("button", name="确 认").click()
            
        except Exception as e:
            logger.error(f"Error selecting province: {e}")
        # 保持浏览器打开，便于调试
        await page.get_by_text("去录排").click()
    else:
        try:
            await page.get_by_text("添加省").click()
            await page.get_by_text(f"{page_data.province}",exact=True).click()
            await page.get_by_role("button", name="确 认").click()
            
        except Exception as e:
            logger.error(f"Error selecting province: {e}")
        # 保持浏览器打开，便于调试
        await page.get_by_text("去录排").click()
    await browser.close()
    logger.info("Browser closed")


if __name__ == "__main__":
    asyncio.run(pre_process())


async def get_city_from_llm(paper_name: str,page:Page) -> str:
    return await ask_xchatbot(page=page,message=f"请从试卷名称中提取出城市名称，只需要返回城市名称，格式为'城市'，如果没有包含省份和城市信息，请返回''。试卷名称：{paper_name}.only can be one of the following cities list:{provinces.get("浙江")}.if it is not in the list,return ''.")


async def upload_pdf(page, page_data):
    logger.info("Uploading PDF file...")

    # 构造绝对路径
    partial_path = page_data.name
    file_path = os.path.abspath(f"PDF/{partial_path}.pdf")
    logger.info(f"Selecting file: {file_path}")

    # 直接设置隐藏的 input[type=file]，避免点击事件超时
    await page.set_input_files("input[type=file]", file_path)

    # 验证上传是否成功：通常上传后文件名会显示在页面上
    file_name = f"{partial_path}.pdf"
    try:
        logger.info(f"Verifying upload for {file_name}...")
        # 等待文件名出现，超时时间设置为 5 秒
        await page.wait_for_selector(f"text={file_name}", timeout=5000)
        logger.info(f"Upload successful: {file_name} detected on page.")
    except Exception as e:
        logger.warning(f"Could not verify upload for {file_name}. It might have failed or the UI is different. Error: {e}")

    # 等待页面处理完成
    await asyncio.sleep(2)