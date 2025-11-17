import asyncio
from operations.model import muti_thread_config
from operations.core import core



async def main() -> None:
    config = await muti_thread_config.create(
        ports=[
            2001, 
            2002,2003,2004,2005,2006,2007,2008,2009
            ],
        zujvanwang_catalogue_url="https://zujuan.xkw.com/czls/shijuan/bk/t29p6")

    
    # 为每个端口和URL创建一个并发任务
    tasks = []
    
    valid_papers = [paper for paper in config.zujvanwang_papers if paper.get('url') and paper.get('url').startswith("http")]
    

    # Use the minimum of the number of ports and the number of valid URLs found
    num_tasks = min(len(config.ports), len(valid_papers))
    if num_tasks > 0:
        tasks = []
        for i in range(num_tasks):
            port = config.ports[i]
            paper_info = valid_papers[i]
            task = core(target_url=paper_info['url'], target_title=paper_info['title'], port=port)
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

