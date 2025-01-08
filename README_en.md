# GitHub Speed Optimizer

![Application Icon](./icon.png)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Windows desktop application for optimizing GitHub access speed by automatically detecting and updating the fastest GitHub IP addresses to the hosts file, solving the problems of slow GitHub access and inaccessibility.

**Please give it a star if you find it useful**

## Features

- Multi-threaded automatic detection of the best IP for GitHub related domains
- Real-time display of detection status and latency for each domain
- Customizable hosts file path
- Support for minimizing to system tray
- Automatic scheduled detection and updates
- Graphical user interface
- Log file rotation with maximum 100 lines retained

## Installation

### Source Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/github-speed-optimizer.git
   cd github-speed-optimizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python github_speed_optimizer.py
   ```

## Usage

1. After launching the application, click the "Start" button to begin detection
2. The application will automatically detect and update the hosts file
3. Click the "Minimize" button to minimize the application to system tray
4. Right-click the system tray icon to choose "Show" or "Exit"

## Notes

- Requires administrator privileges to run
- Modifying hosts file requires administrator privileges
- Recommended to keep the application running in background for continuous speed optimization
- Log files are saved in the application directory with maximum 100 lines retained

## Contributing

Welcome to submit issues and pull requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
