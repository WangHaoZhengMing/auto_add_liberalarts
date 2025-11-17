import asyncio
from operations.model import muti_thread_config
from operations.core import core

async def main() -> None:
    config = await muti_thread_config.create(
        ports=[2001, 2002,2003,2004,2005,2006,2007,2008,2009],
        zujvanwang_catalogue_url="https://zujuan.xkw.com/czyy/shijuan/bk/a310000")

    
    # 为每个端口和URL创建一个并发任务
    tasks = []
    # Filter out invalid URLs
    print("找到的题目页面URL列表:{config.zujvanwang_questions_urls}")


# https://tps-tiku-api.staff.xdf.cn/paper/check/paperName?paperName=%E8%BF%99%E9%87%8C%E6%94%BE%E8%AF%95%E5%8D%B7%E5%90%8D&operationType=1&paperId=
# i want you to test if the testpaper is exist in our bank. post a request with the paper name to the above url. if the response show that the paper is exist, then we can skip this paper.and print the paper name to ./重复.txt



    valid_urls = [url for url in config.zujvanwang_questions_urls if url.startswith("http")]
    
    # Use the minimum of the number of ports and the number of valid URLs found
    num_tasks = min(len(config.ports), len(valid_urls))
    for i in range(num_tasks):
        port = config.ports[i]
        task = core(target_url=valid_urls[i], target_title="", port=port)
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

