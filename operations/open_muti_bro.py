import asyncio
import subprocess
import os

def open_muti_browsers(ports, url,):
    base_user_data_dir = r"C:\Users\hallm\AppData\Local\Microsoft\Edge\User Data"
    for i, port in enumerate(ports):
        user_data_dir = os.path.join(base_user_data_dir, f"Profile{i+1}")
        subprocess.Popen([
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",  # Edge 浏览器路径
            f"--remote-debugging-port={port}",  # 不同的调试端口
            f"--user-data-dir={user_data_dir}",  # 独立的用户数据目录
            "--new-window",  # 强制在新的窗口中打开
            url  # 要打开的网页
        ])

async def main():
    ports = [9223, 9224, 9225]  # 示例端口列表
    url = "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate"
    open_muti_browsers(ports, url)

    print("等待浏览器启动...")
    await asyncio.sleep(5)  # 等待5秒以确保浏览器完全启动

if __name__ == "__main__":
    asyncio.run(main())