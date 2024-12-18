# Comprehensive System Diagnostics Automation

This repository contains a GitHub Actions workflow designed to automatically gather comprehensive system information from GitHub Actions runners. It collects various system diagnostics, including CPU, memory, disk usage, network, and GPU details, and generates detailed reports for monitoring, troubleshooting, and performance analysis.

## Purpose
The goal of this project is to automate the collection of system data on GitHub Actions runners. This includes monitoring resources such as CPU, memory, disk, network interfaces, and hardware components. The collected information can help with:

- Proactive system health checks for CI/CD pipelines.
- Diagnosing system issues that could affect the performance of jobs.
- Automating performance and resource usage monitoring.

## Features
- **System Identification**: OS version, kernel, architecture, hostname.
- **CPU Details**: Model, cores, frequency, flags.
- **Memory Information**: Total, used, available RAM and swap usage.
- **Disk Usage**: Partition details, mount points, free/used space.
- **Network Interfaces**: IP addresses, MAC addresses.
- **GPU Details**: Memory usage and GPU specs.
- **System Sensors**: Temperature readings and hardware sensor data.
- **Battery Information**: Battery status and remaining power (if applicable).
- **Network Speed Test**: Bandwidth tests (download, upload, ping).
- **System Load**: Current system load and running processes.
- **Running Services**: List of active services on the system.
- **Hardware Details**: Detailed hardware info using tools like `lspci`, `lsusb`, `dmidecode`.

## Workflow
The GitHub Actions workflow is triggered on `push`, `pull_request`, or manually (`workflow_dispatch`). Upon execution, it collects detailed system data and stores the results in both JSON and TXT formats. The generated reports are then uploaded as artifacts for easy download and analysis.

## Prerequisites
This project requires GitHub Actions with access to a Linux-based runner (Ubuntu). The following tools are installed on the runner during the workflow:

- `python3`, `pip`
- `psutil`, `GPUtil`, `py-cpuinfo`, `speedtest-cli`, `netifaces`, `distro`, `wmi`
- `sysstat`, `stress`, `nmap`, `lshw`, `hdparm`, `smartmontools`, `lm-sensors`, `dmidecode`, and more system diagnostic tools.

## Setup

1. **Fork or Clone the Repository**:
   Fork or clone this repository to your GitHub account to use or modify the workflow.

2. **Workflow Trigger**:
   - The workflow will run on `push` or `pull_request` events to the `main` branch.
   - You can also manually trigger the workflow using GitHub's "Run workflow" option.

3. **Run Workflow**:
   - When triggered, the workflow will automatically install necessary dependencies, run the system diagnostics, and generate reports.
   - The resulting files will be available as GitHub artifacts after the workflow completes.

## Example Output

After running the workflow, you will find the following files in the artifact:

- `system_info.json`: A machine-readable JSON file containing all the collected system data.
- `system_info.txt`: A human-readable text file with the same data formatted for easy inspection.

Additionally, the following diagnostic files will be created:

- `network_diagnostics.txt`: Network-related information such as interfaces, routes, and ports.
- `process_tree.txt`: A hierarchical list of running processes.
- `performance_metrics.txt`: System performance data (e.g., CPU and memory usage).
- `security_scan.txt`: A basic security scan of open ports and services using `nmap`.

## Usage

1. **Trigger the Workflow**:
   - The workflow runs automatically on every push to `main` or when a pull request is made.
   - You can also manually trigger it via the GitHub UI under "Actions".

2. **Download the Artifacts**:
   - After the workflow completes, go to the "Actions" tab of your repository, select the latest workflow run, and download the generated artifact files (JSON, TXT, and diagnostic reports).

3. **Analyze the Results**:
   - Open the JSON or TXT reports to analyze system information.
   - Use the network, process, and performance diagnostics to identify any potential issues.

## Customization
Feel free to customize the workflow to:
- **Add more system checks** or **remove unnecessary steps** based on your needs.
- **Schedule regular runs** for automated monitoring of your CI/CD environment.
- **Integrate with external monitoring tools** to trigger alerts based on specific thresholds (e.g., CPU usage > 90%).

## Contributing
If you have suggestions, bug fixes, or improvements, feel free to create a pull request. Contributions are welcome!

## License
This project is licensed under the MIT License.

---

## Credits
- **GitHub Actions**: CI/CD platform used to automate the workflow.
- **Python Libraries**: `psutil`, `GPUtil`, `py-cpuinfo`, `speedtest-cli`, `netifaces` for gathering system data.
- **System Tools**: Various Linux tools like `lshw`, `nmap`, `dmidecode`, etc., used for detailed hardware and system diagnostics.

