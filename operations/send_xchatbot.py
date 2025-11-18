import json
from playwright.async_api import Page, Route, Response

async def ask_xchatbot(page: Page, message: str) -> str:
    """
    Sends a message to the xchatbot and returns the response text.

    Args:
        page: The Playwright page object.
        message: The message to send.

    Returns:
        The text response from the chatbot.
    """
    request_url = "https://xchatbot.xdf.cn/xz-api/v2/agent/chat"
    payload = {
        "conversationId": "",
        "conversationType": 1,
        "eventType": 1,
        "content": {
            "message": message,
            "modelName": "gpt-5-chat",
            "agentId": "0",
            "fileDescriptorList": [],
            "enableSearch": False
        }
    }

    # Use page.evaluate to send the request from the browser context
    response_text = await page.evaluate(f"""
        async () => {{
            const response = await fetch("{request_url}", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({json.dumps(payload)})
            }});
            return await response.text();
        }}
    """)

    # The response is a stream of server-sent events. We need to parse it.
    last_json = None
    full_text = ""
    for line in response_text.strip().split('\n'):
        if line.startswith('data:'):
            try:
                json_str = line[len('data:'):].strip()
                if json_str:
                    data = json.loads(json_str)
                    last_json = data
                    if 'content' in data and 'text' in data['content'] and data['content']['text']:
                        full_text += data['content']['text']
            except json.JSONDecodeError:
                continue
    
    if last_json and 'content' in last_json:
        last_json['content']['text'] = full_text

    return full_text

if __name__ == "__main__":
    import asyncio
    from playwright.async_api import Browser, Page
    from playwright.async_api import async_playwright

    async def main():
        async with async_playwright() as p:
            port = 2001
            target_url = ""
            target_title = "小智GPT"
            from connect_browser import connect_to_browser_and_page
            # 连接到浏览器并获取页面
            browser: Browser
            page: Page
            browser, page = await connect_to_browser_and_page(target_url,target_title=target_title,port=port)
            response = await ask_xchatbot(page, "Hello, how are you?")
            print(response)
            await browser.close()

    asyncio.run(main())