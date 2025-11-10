import asyncio
from operations.model import muti_thread_config
from operations.open_muti_bro import open_muti_browsers
from operations.core import core
from operations.connect_browser import connect_to_browser_and_page

async def main() -> None:
    config = await muti_thread_config.create(
        ports=[2001, 2002],
        zujvanwang_catalogue_url="https://zujuan.xkw.com/czyw/shijuan/bk/t26a310000")


    # 初始页面，可以是一个空白页或登录后的页面
    # initial_url = "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate"
    # 启动所有浏览器实例
    # open_muti_browsers(ports, initial_url)
    
    # 为每个端口和URL创建一个并发任务
    tasks = []
    # Use the minimum of the number of ports and the number of URLs found
    num_tasks = min(len(config.ports), len(config.zujvanwang_questions_urls))
    for i in range(num_tasks):
        port = config.ports[i]
        task = core(target_url=config.zujvanwang_questions_urls[i], target_title="", port=port)
        tasks.append(task)

    # 并发执行所有core任务
    if tasks:
        print(f"为 {len(tasks)} 个端口启动并发处理任务...")
        await asyncio.gather(*tasks)
        print("所有任务已完成。")
    else:
        print("没有要处理的任务。")

if __name__ == "__main__":
    asyncio.run(main())

