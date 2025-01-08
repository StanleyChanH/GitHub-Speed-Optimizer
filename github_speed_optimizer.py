import time
import socket
import subprocess
import logging
import ctypes
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
from queue import Queue
import pystray
from PIL import Image
import os
import sys

# 配置
GITHUB_DOMAINS = [
    'github.com',
    'github.global.ssl.fastly.net',
    'assets-cdn.github.com',
    'raw.githubusercontent.com',
    'gist.githubusercontent.com',
    'cloud.githubusercontent.com',
    'camo.githubusercontent.com',
    'avatars0.githubusercontent.com',
    'avatars1.githubusercontent.com',
    'avatars2.githubusercontent.com',
    'avatars3.githubusercontent.com',
    'avatars4.githubusercontent.com',
    'avatars5.githubusercontent.com',
    'avatars6.githubusercontent.com',
    'avatars7.githubusercontent.com',
    'avatars8.githubusercontent.com',
    'favicons.githubusercontent.com',
    'user-images.githubusercontent.com',
    'codeload.github.com',
    'api.github.com',
    'training.github.com',
    'central.github.com',
    'pipelines.actions.githubusercontent.com',
    'media.githubusercontent.com',
    'objects.githubusercontent.com',
    'raw.github.com',
    'copilot-proxy.githubusercontent.com'
]

DEFAULT_HOSTS_PATH = r'C:\Windows\System32\drivers\etc\hosts'
CHECK_INTERVAL = 300  # 检查间隔，单位秒
TIMEOUT = 1  # 延迟检测超时时间

from logging.handlers import RotatingFileHandler

# 日志配置
log_handler = RotatingFileHandler(
    'github_speed_optimizer.log',
    maxBytes=1024*100,  # 100KB
    backupCount=1,
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        log_handler,
        logging.StreamHandler()
    ]
)

def ping_ip(ip, domain, app):
    """使用socket连接检测IP延迟"""
    try:
        # 更新状态为检测中
        app.update_status(domain, "检测中...", ip, "")
        
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 设置超时时间2秒
        
        # 测量TCP连接时间
        start = time.time()
        sock.connect((ip, 80))  # 尝试连接80端口
        latency = (time.time() - start) * 1000  # 计算延迟时间（毫秒）
        sock.close()
        return ip, latency
    except socket.timeout:
        app.update_status(domain, "响应超时", ip, "超时")
        return ip, float('inf')
    except socket.error as e:
        app.update_status(domain, f"连接错误: {str(e)}", ip, "错误")
        return ip, float('inf')
    except Exception as e:
        logging.error(f"Error pinging {ip} for {domain}: {str(e)}")
        return ip, float('inf')

def get_best_ip(domain, app):
    """获取指定域名的最佳IP"""
    try:
        # 获取所有IP地址
        ips = set(socket.gethostbyname_ex(domain)[2])
        results = []
        result_queue = Queue()
        threads = []
        
        # 创建并启动线程
        for ip in ips:
            thread = threading.Thread(
                target=lambda ip=ip: result_queue.put(ping_ip(ip, domain, app)),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        # 收集结果
        while not result_queue.empty():
            ip, latency = result_queue.get()
            if latency != float('inf'):
                results.append((ip, latency))
        
        # 返回延迟最低的IP，如果没有有效结果则返回None
        if results:
            return min(results, key=lambda x: x[1])
        return None  # 没有有效IP时返回None
    except Exception as e:
        logging.error(f"Error getting best IP for {domain}: {str(e)}")
        return None

def update_hosts(domain, ip, hosts_path, app=None):
    """更新hosts文件"""
    try:
        # 读取现有hosts内容
        existing_lines = []
        if os.path.exists(hosts_path):
            with open(hosts_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip()  # 保留行尾空白
                    if not line or line.startswith('#'):
                        # 保留注释和空行
                        existing_lines.append(line)
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        current_ip = parts[0]
                        hostnames = parts[1:]
                        # 只保留非GitHub相关的条目
                        if not any(d in GITHUB_DOMAINS for d in hostnames):
                            existing_lines.append(line)
        
        # 收集GitHub域名和最佳IP的映射
        github_entries = []
        for github_domain in GITHUB_DOMAINS:
            # 获取该域名的最佳IP
            best_ip_result = get_best_ip(github_domain, app)
            if best_ip_result:
                best_ip, latency = best_ip_result
                # 只写入有效IP（延迟不为无穷大）
                if latency != float('inf'):
                    github_entries.append((best_ip, github_domain))
                else:
                    logging.warning(f"No valid IP found for {github_domain}")
            else:
                logging.warning(f"Failed to get IP for {github_domain}")
        
        # 直接写入hosts文件
        with open(hosts_path, 'w', encoding='utf-8', newline='\r\n') as f:
            # 写入原有内容
            for line in existing_lines:
                # 跳过已有的GitHub优化注释
                if not line.startswith("# GitHub Speed Optimizer"):
                    f.write(line + "\n")
            
            # 写入新的GitHub优化注释
            if github_entries:
                f.write("# GitHub Speed Optimizer - Updated at " + 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            
            # 写入GitHub域名和最佳IP，每个域名单独一行
            for ip_address, domain in github_entries:
                f.write(f"{ip_address} {domain}\n")
            
            # 确保文件以空行结尾
            f.write("\n")
        
        logging.info(f"Successfully updated hosts: {ip} {domain}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating hosts file: {str(e)}")
        return False

class GitHubSpeedOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Speed Optimizer")
        self.root.geometry("850x600")
        # 设置窗口图标
        try:
            # 打包后路径
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, "icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            # 开发环境路径
            base_path = os.path.dirname(__file__)
            icon_path = os.path.join(base_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态显示区域
        self.status_frame = ttk.LabelFrame(self.main_frame, text="检测状态")
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格显示状态
        columns = ("domain", "status", "best_ip", "latency")
        self.tree = ttk.Treeview(self.status_frame, columns=columns, show="headings")
        
        # 设置列宽
        self.tree.column("domain", width=200, anchor=tk.W)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("best_ip", width=200, anchor=tk.W)
        self.tree.column("latency", width=100, anchor=tk.CENTER)
        
        # 设置列标题
        self.tree.heading("domain", text="域名")
        self.tree.heading("status", text="状态")
        self.tree.heading("best_ip", text="最佳IP")
        self.tree.heading("latency", text="延迟(ms)")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 初始化状态数据
        self.status_data = {}
        for domain in GITHUB_DOMAINS:
            self.status_data[domain] = {
                "status": "等待检测",
                "best_ip": "",
                "latency": 0
            }
            self.tree.insert("", "end", values=(
                domain,
                "等待检测",
                "",
                ""
            ))
        
        # 控制面板 - 第一行
        self.control_frame_top = ttk.Frame(self.main_frame)
        self.control_frame_top.pack(fill=tk.X, pady=(10, 5))
        
        # Hosts文件路径设置
        self.hosts_frame = ttk.LabelFrame(self.control_frame_top, text="Hosts文件路径")
        self.hosts_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.hosts_path_var = tk.StringVar(value=DEFAULT_HOSTS_PATH)
        self.hosts_entry = ttk.Entry(self.hosts_frame, 
                                   textvariable=self.hosts_path_var)
        self.hosts_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 间隔时间设置
        self.interval_frame = ttk.LabelFrame(self.control_frame_top, text="检测间隔（秒）")
        self.interval_frame.pack(side=tk.LEFT, padx=5)
        
        self.interval_var = tk.IntVar(value=CHECK_INTERVAL)
        self.interval_entry = ttk.Entry(self.interval_frame, 
                                      textvariable=self.interval_var,
                                      width=5)
        self.interval_entry.pack(side=tk.LEFT, padx=5)
        
        # 控制面板 - 第二行
        self.control_frame_bottom = ttk.Frame(self.main_frame)
        self.control_frame_bottom.pack(fill=tk.X, pady=(5, 10))
        
        # 控制按钮和进度条容器
        self.button_frame = ttk.Frame(self.control_frame_bottom)
        self.button_frame.pack(fill=tk.X, expand=True, padx=10)
        
        # 按钮容器
        self.button_container = ttk.Frame(self.button_frame)
        self.button_container.pack(side=tk.LEFT, padx=(0, 10))
        
        # 第一行按钮
        self.button_row1 = ttk.Frame(self.button_container)
        self.button_row1.pack(side=tk.TOP, pady=2)
        
        self.start_button = ttk.Button(self.button_row1, text="开始", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.button_row1, text="停止", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.minimize_button = ttk.Button(self.button_row1, text="后台运行", command=self.minimize_to_tray)
        self.minimize_button.pack(side=tk.LEFT, padx=5)
        
        # 状态显示标签
        self.status_label = ttk.Label(self.button_container, text="等待检测", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.button_frame,
                                      mode='determinate',
                                      maximum=len(GITHUB_DOMAINS))
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.running = False
        self.worker_queue = Queue()
        self.workers = []
        
    def start(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="检测中...", foreground="blue")
        self.run_optimizer()
        
    def stop(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="已停止", foreground="red")
        
    def minimize_to_tray(self):
        """最小化到系统托盘"""
        self.root.withdraw()  # 隐藏主窗口
        self.create_tray_icon()  # 创建托盘图标
        
    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建托盘图标
        try:
            # 打包后路径
            base_path = sys._MEIPASS
        except Exception:
            # 开发环境路径
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icon.ico")
        image = Image.open(icon_path)
        menu = (
            pystray.MenuItem('显示', self.restore_window),
            pystray.MenuItem('退出', self.quit_app)
        )
        self.tray_icon = pystray.Icon("github_speed_optimizer", image, "GitHub Speed Optimizer", menu)
        
        # 启动托盘图标
        self.tray_icon.run_detached()
        
    def restore_window(self, icon=None, item=None):
        """从托盘恢复窗口"""
        self.tray_icon.stop()
        self.root.deiconify()
        
    def quit_app(self, icon=None, item=None):
        """退出程序"""
        self.running = False
        self.tray_icon.stop()
        self.root.quit()
        
    def run_optimizer(self):
        if not self.running:
            return
            
        # 更新状态为检测中
        self.status_label.config(text="检测中...", foreground="blue")
        self.progress['value'] = 0
        self.progress['maximum'] = len(GITHUB_DOMAINS)
        
        # 清空上次结果
        for domain in GITHUB_DOMAINS:
            self.update_status(domain, "等待检测", "", "")
            
        # 创建并启动工作线程
        self.workers = []
        for domain in GITHUB_DOMAINS:
            if not self.running:
                break
                
            worker = threading.Thread(
                target=self.check_domain,
                args=(domain,),
                daemon=True
            )
            self.workers.append(worker)
            worker.start()
            
        # 启动结果处理线程
        self.result_thread = threading.Thread(
            target=self.process_results,
            daemon=True
        )
        self.result_thread.start()
        
    def process_results(self):
        """处理检测结果"""
        start_time = time.time()
        timeout = 30  # 最多等待30秒
        
        while self.running and any(w.is_alive() for w in self.workers):
            # 检查超时
            if time.time() - start_time > timeout:
                logging.warning("检测超时，强制终止线程")
                for worker in self.workers:
                    if worker.is_alive():
                        try:
                            worker.join(0.1)  # 尝试优雅地结束线程
                        except Exception as e:
                            logging.error(f"终止线程时出错: {str(e)}")
                break
                
            time.sleep(0.1)
            self.root.update()
            
        if self.running:
            # 清理线程
            self.workers = []
            
            # 设置下次检测
            self.status_label.config(text="等待下次检测", foreground="gray")
            interval = self.interval_var.get() * 1000
            self.root.after(interval, self.run_optimizer)
                
    def check_domain(self, domain):
        """单独检测一个域名"""
        # 更新状态为检测中
        self.update_status(domain, "检测中...", "", "")
        result = get_best_ip(domain, self)
        if result:
            ip, latency = result
            # 更新hosts文件
            update_hosts(domain, ip, self.hosts_path_var.get(), self)
            # 更新状态为完成
            self.update_status(domain, "完成", ip, latency)
            # 更新进度条
            self.root.after(0, lambda: self.progress.step(1))
            return result
        else:
            # 更新状态为失败
            self.update_status(domain, "失败", "", "")
            # 更新进度条
            self.root.after(0, lambda: self.progress.step(1))
            return None
                
    def update_status(self, domain, status, best_ip, latency):
        item_id = self.tree.get_children()[GITHUB_DOMAINS.index(domain)]
        
        # 设置状态颜色
        status_color = "black"
        if status == "响应超时":
            status_color = "red"
        elif isinstance(latency, (int, float)):
            if latency < 100:
                status_color = "green"
            elif latency < 300:
                status_color = "orange"
            else:
                status_color = "red"
                
        self.tree.item(item_id, values=(
            domain,
            status,
            best_ip,
            f"{latency:.2f}ms" if isinstance(latency, (int, float)) else str(latency)
        ))
        
        self.tree.tag_configure(status_color, foreground=status_color)
        self.tree.item(item_id, tags=(status_color,))
        
        self.status_data[domain] = {
            "status": status,
            "best_ip": best_ip,
            "latency": latency
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubSpeedOptimizerApp(root)
    root.mainloop()
