import asyncio
from operations.open_muti_bro import open_muti_browsers
from operations.core import core

async def main() -> None:
    # 定义要使用的端口
    ports = [
        2001,
          2002
        ]
    
    # 为每个端口分配一个要处理的目标URL
    target_urls = [
        "https://zujuan.xkw.com/1p2846173.html",
        "https://zujuan.xkw.com/1p2845777.html",
    ]

    # 确保端口数量和URL数量匹配
    if len(ports) != len(target_urls):
        print("错误：端口数量和URL数量必须一致。")
        return

    # 初始页面，可以是一个空白页或登录后的页面
    initial_url = "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate"
    
    # 启动所有浏览器实例
    # open_muti_browsers(ports, initial_url)
    
    # 为每个端口和URL创建一个并发任务
    tasks = []
    for i, port in enumerate(ports):
        task = core(target_url=target_urls[i], target_title="", port=port)
        tasks.append(task)

    # 并发执行所有core任务
    print(f"为 {len(ports)} 个端口启动并发处理任务...")
    await asyncio.gather(*tasks)
    print("所有任务已完成。")

if __name__ == "__main__":
    asyncio.run(main())

