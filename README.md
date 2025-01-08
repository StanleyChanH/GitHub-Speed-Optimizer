# GitHub Speed Optimizer

![Application Icon](./icon.png)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个用于优化GitHub访问速度的Windows桌面应用程序，通过自动检测并更新最快的GitHub IP地址到hosts文件，解决GitHub访问速度慢、无法访问的问题。
**点个Star支持一下吧**

## 功能特性

- 多线程自动检测GitHub相关域名的最佳IP
- 实时显示每个域名的检测状态和延迟
- 支持自定义hosts文件路径
- 支持最小化到系统托盘
- 自动定时检测更新
- 图形化界面操作

## 安装

### 下载安装包

**注意防火墙是否阻止了EXE运行**

- 在release页面下载最新版安装包
- 双击运行GitHubSpeedOptimizer.exe
- 点击"开始"按钮开始检测
   - 程序会自动检测最佳IP并更新hosts文件
   - 点击"后台运行"按钮将程序最小化到系统托盘

### 源码安装
1. 克隆本仓库：
   ```bash
   git clone https://github.com/yourusername/github-speed-optimizer.git
   cd github-speed-optimizer
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python github_speed_optimizer.py
   ```

## 使用说明

1. 启动程序后，点击"开始"按钮开始检测
2. 程序会自动检测并更新hosts文件
3. 可以点击"最小化"按钮将程序最小化到系统托盘
4. 在系统托盘图标上右键可以选择"显示"或"退出"

## 注意事项

- 需要以管理员权限运行程序
- 修改hosts文件需要管理员权限
- 建议保持程序后台运行以持续优化访问速度

## 贡献

欢迎提交issue和pull request

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件
