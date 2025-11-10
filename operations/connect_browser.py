from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio


async def connect_to_browser_and_page(target_url: str,target_title: str) -> tuple[Browser, Page]:
    """
    连接到现有的浏览器实例并找到指定URL的页面
    
    Args:
        target_url: 目标页面的URL
        
    Returns:
        tuple[Browser, Page]: 浏览器实例和页面对象
        
    Raises:
        RuntimeError: 如果未找到指定URL的页面
    """
    print("连接到题库平台调试界面...")
    
    p = await async_playwright().start()
    
    # 连接到现有的浏览器实例
    browser: Browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    
    context: BrowserContext = browser.contexts[0]
    page: Page = None

    # 查找具有特定标题的页面
    if target_title:
        for p in context.pages:
            if target_title in await p.title():
                page = p
                print(f"已连接到现有页面: {await page.title()}")
                break
    # 如果通过标题没有找到页面，并且提供了URL，则按URL查找
    if not page and target_url:
        for p in context.pages:
            if target_url in p.url:
                page = p
                print(f"已连接到现有页面: {p.url}")
                break

    # 如果两种方式都找不到页面，则抛出错误
    if not page:
        if target_url:
            raise RuntimeError(f"未找到URL为 '{target_url}' 的页面。请确保页面已在浏览器中打开。")
        elif target_title:
            raise RuntimeError(f"未找到标题为 '{target_title}' 的页面。请确保页面已在浏览器中打开。")
        else:
            raise RuntimeError("未提供URL或标题，无法找到页面。")

    await page.bring_to_front()
    print(f"页面标题: {await page.title()}")
    
    # 等待页面稳定
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)
    
    # 获取页面基本信息
    title: str = await page.title()
    print(f"页面标题: {title}")
    print(f"当前URL: {page.url}")
    
    return browser, page
