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
- 日志文件自动轮转，最多保留100行

## 安装

### 下载软件
- [GitHub Releases](https://github.com/StanleyChanH/github-speed-optimizer/releases)

### 源码安装
1. 克隆本仓库：
   ```bash
   git clone https://github.com/StanleyChanH/github-speed-optimizer.git
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

- 程序仅支持Windows系统
- 修改hosts文件需要管理员权限
- 建议保持程序后台运行以持续优化访问速度
- 日志文件保存在程序目录下，最多保留100行

## 贡献

欢迎提交issue和pull request

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件
