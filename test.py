import subprocess
import os

def open_edge_window(port, url, user_data_dir):
    subprocess.Popen([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",  # Edge 浏览器路径
        f"--remote-debugging-port={port}",  # 不同的调试端口
        f"--user-data-dir={user_data_dir}",  # 独立的用户数据目录
        "--new-window",  # 强制在新的窗口中打开
        url  # 要打开的网页
    ])

# 创建不同的用户数据目录
base_user_data_dir = r"C:\Users\hallm\AppData\Local\Microsoft\Edge\User Data"

# 启动多个窗口，使用不同的调试端口和用户数据目录
open_edge_window(2001, "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate", os.path.join(base_user_data_dir, "Profile1"))
open_edge_window(2002, "https://tps-tiku.staff.xdf.cn/tasks/questionSetCreate", os.path.join(base_user_data_dir, "Profile2"))
