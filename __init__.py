# System Status Skill (SSS)
# 查看系统资源使用情况（跨平台）

import platform
import subprocess
import sys
from pathlib import Path

# 平台适配器映射
PLATFORM_ADAPTERS = {}

def register_adapter(platform_name):
    """装饰器：注册平台适配器"""
    def decorator(func):
        PLATFORM_ADAPTERS[platform_name] = func
        return func
    return decorator

def get_adapter():
    """获取当前平台的适配器"""
    system = platform.system().lower()
    if system in PLATFORM_ADAPTERS:
        return PLATFORM_ADAPTERS[system], system
    return None, system

def run(mode="all"):
    """
    执行系统资源检查

    Args:
        mode: 检查模式
            - "all": 显示所有信息（内存+CPU+磁盘）
            - "memory": 仅内存
            - "cpu": 仅 CPU
            - "disk": 仅磁盘

    Returns:
        str: 格式化报告
    """
    adapter, system = get_adapter()
    if adapter is None:
        return f"不支持的操作系统: {platform.system()}"

    try:
        if mode == "memory":
            return adapter.check_memory()
        elif mode == "cpu":
            return adapter.check_cpu()
        elif mode == "disk":
            return adapter.check_disk()
        else:  # mode == "all"
            parts = []
            mem = adapter.check_memory()
            cpu = adapter.check_cpu()
            disk = adapter.check_disk()
            parts.append(mem)
            parts.append("\n\n")
            parts.append(cpu)
            parts.append("\n\n")
            parts.append(disk)
            return ''.join(parts)
    except Exception as e:
        return f"执行失败: {str(e)}"

def run_cpu():
    """执行 CPU 检查"""
    adapter, system = get_adapter()
    if adapter is None:
        return f"不支持的操作系统: {platform.system()}"
    try:
        return adapter.check_cpu()
    except Exception as e:
        return f"执行失败: {str(e)}"

def run_disk():
    """执行磁盘检查"""
    adapter, system = get_adapter()
    if adapter is None:
        return f"不支持的操作系统: {platform.system()}"
    try:
        return adapter.check_disk()
    except Exception as e:
        return f"执行失败: {str(e)}"


# ========== Windows 适配器 ==========

@register_adapter("windows")
class WindowsAdapter:
    @staticmethod
    def check_memory():
        output = []
        output.append("=== Memory Usage Report ===")
        output.append("")

        try:
            # 获取内存总体信息
            result = subprocess.run(
                ["powershell", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object @{Name='TotalGB';Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{Name='FreeGB';Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}"],
                capture_output=True, text=True
            )
            output.append(result.stdout)

            # 计算使用率
            result2 = subprocess.run(
                ["powershell", "-Command", "$os=Get-CimInstance Win32_OperatingSystem; $used=[math]::Round(($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/$os.TotalVisibleMemorySize*100,2); Write-Output \"Usage: $used %\""],
                capture_output=True, text=True
            )
            output.append(result2.stdout)
        except Exception as e:
            output.append(f"无法获取内存信息: {e}")

        output.append("")
        output.append("=== Top 5 Memory Processes ===")
        output.append("")

        try:
            # 获取前5个内存占用最高的进程
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process | Sort-Object WS -Descending | Select-Object -First 5 @{Name='Process';Expression={$_.Name}}, @{Name='Memory(MB)';Expression={[math]::Round($_.WS/1MB,2)}} | Format-Table -AutoSize"],
                capture_output=True, text=True
            )
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取进程信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. If memory usage >80%, close unnecessary programs")
        output.append("2. Check for unknown processes")
        output.append("3. Use Task Manager for details")
        output.append("4. Restart to free memory")

        return '\n'.join(output)

    @staticmethod
    def check_cpu():
        output = []
        output.append("=== CPU Usage Report ===")
        output.append("")

        try:
            # 获取 CPU 负载（平均值）
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object Average"],
                capture_output=True, text=True
            )
            output.append("CPU Load Average:")
            output.append(result.stdout)

            # 获取 CPU 核心数
            result2 = subprocess.run(
                ["powershell", "-Command", "(Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors"],
                capture_output=True, text=True
            )
            output.append(f"Logical Cores: {result2.stdout.strip()}")

            output.append("")
            output.append("=== Top 5 CPU Processes ===")
            output.append("")

            # 获取 CPU 占用最高的进程
            result3 = subprocess.run(
                ["powershell", "-Command", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 @{Name='Process';Expression={$_.Name}}, @{Name='CPU(s)';Expression={$_.CPU}} | Format-Table -AutoSize"],
                capture_output=True, text=True
            )
            output.append(result3.stdout)
        except Exception as e:
            output.append(f"无法获取 CPU 信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. If CPU usage >80%, check for runaway processes")
        output.append("2. Use Task Manager to identify high CPU processes")
        output.append("3. Consider upgrading CPU if consistently high")
        output.append("4. Check for malware or background tasks")

        return '\n'.join(output)

    @staticmethod
    def check_disk():
        output = []
        output.append("=== Disk Usage Report ===")
        output.append("")

        try:
            # 获取所有磁盘分区信息
            result = subprocess.run(
                ["powershell", "-Command", "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Size(GB)';Expression={[math]::Round($_.Used/1GB,2)}}, @{Name='Free(GB)';Expression={[math]::Round($_.Free/1GB,2)}}, @{Name='Used(%)';Expression={[math]::Round(($_.Used/($_.Used+$_.Free))*100,2)}} | Format-Table -AutoSize"],
                capture_output=True, text=True
            )
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取磁盘信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. Clean up temporary files if disk >90%")
        output.append("2. Move large files to external storage")
        output.append("3. Use Disk Cleanup tool")
        output.append("4. Consider adding more storage")

        return '\n'.join(output)


# ========== Linux 适配器 ==========

@register_adapter("linux")
class LinuxAdapter:
    @staticmethod
    def check_memory():
        output = []

        output.append("=== Memory Usage Report ===")
        output.append("")

        try:
            result = subprocess.run(["free", "-h"], capture_output=True, text=True)
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取内存信息: {e}")

        output.append("")
        output.append("=== Top 5 Memory Processes ===")
        output.append("")

        try:
            result = subprocess.run(
                ["ps", "aux", "--sort=-%mem"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            # 取前 6 行（表头 + 5 个进程）
            top_processes = lines[:6]
            output.extend(top_processes)
        except Exception as e:
            output.append(f"无法获取进程信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. Use 'free -h' for detailed memory info")
        output.append("2. Use 'top' or 'htop' for real-time monitoring")
        output.append("3. Check for memory leaks with 'ps aux --sort=-%mem'")
        output.append("4. Consider adding swap space if needed")

        return '\n'.join(output)

    @staticmethod
    def check_cpu():
        output = []
        output.append("=== CPU Usage Report ===")
        output.append("")

        try:
            # 使用 top 获取 CPU 负载
            result = subprocess.run(["top", "-bn1"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            # 提取 CPU 使用率信息
            for line in lines:
                if '%Cpu(s)' in line:
                    output.append("CPU Usage:")
                    output.append(line.strip())
                    break

            # 获取核心数
            result2 = subprocess.run(["nproc"], capture_output=True, text=True)
            output.append(f"\nLogical Cores: {result2.stdout.strip()}")

            output.append("")
            output.append("=== Top 5 CPU Processes ===")
            output.append("")

            # 获取 CPU 占用最高的进程
            result3 = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"],
                capture_output=True,
                text=True
            )
            lines = result3.stdout.split('\n')
            top_processes = lines[:6]
            output.extend(top_processes)
        except Exception as e:
            output.append(f"无法获取 CPU 信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. If CPU usage >80%, check for runaway processes")
        output.append("2. Use 'top' or 'htop' to identify high CPU processes")
        output.append("3. Consider upgrading CPU if consistently high")
        output.append("4. Check for malware or background tasks")

        return '\n'.join(output)

    @staticmethod
    def check_disk():
        output = []
        output.append("=== Disk Usage Report ===")
        output.append("")

        try:
            result = subprocess.run(["df", "-h"], capture_output=True, text=True)
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取磁盘信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. Clean up temporary files if disk >90%")
        output.append("2. Move large files to external storage")
        output.append("3. Use 'du -sh *' to find large directories")
        output.append("4. Consider adding more storage")

        return '\n'.join(output)


# ========== macOS 适配器 ==========

@register_adapter("darwin")
class MacOSAdapter:
    @staticmethod
    def check_memory():
        output = []

        output.append("=== Memory Usage Report ===")
        output.append("")

        try:
            result = subprocess.run(["vm_stat"], capture_output=True, text=True)
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取内存信息: {e}")

        output.append("")
        output.append("=== Top 5 Memory Processes ===")
        output.append("")

        try:
            result = subprocess.run(
                ["ps", "aux", "-r", "-o", "pid,user,%mem,vsz,rss,comm"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            # 取前 6 行（表头 + 5 个进程）
            top_processes = lines[:6]
            output.extend(top_processes)
        except Exception as e:
            output.append(f"无法获取进程信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. Use 'top -l 1' for summary")
        output.append("2. Use 'Activity Monitor' for GUI")
        output.append("3. Check 'vm_stat' for detailed page statistics")
        output.append("4. Consider 'purge' command to free memory")

        return '\n'.join(output)

    @staticmethod
    def check_cpu():
        output = []
        output.append("=== CPU Usage Report ===")
        output.append("")

        try:
            # 使用 top 获取 CPU 信息
            result = subprocess.run(["top", "-l 1"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'CPU usage' in line or 'Cpu' in line:
                    output.append(line.strip())
                    break

            # 获取核心数
            result2 = subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True)
            output.append(f"\nLogical Cores: {result2.stdout.strip()}")

            output.append("")
            output.append("=== Top 5 CPU Processes ===")
            output.append("")

            result3 = subprocess.run(
                ["ps", "aux", "-r", "-o", "pid,user,%cpu,comm"],
                capture_output=True,
                text=True
            )
            lines = result3.stdout.split('\n')
            top_processes = lines[:6]
            output.extend(top_processes)
        except Exception as e:
            output.append(f"无法获取 CPU 信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. If CPU usage >80%, check for runaway processes")
        output.append("2. Use 'top' or 'Activity Monitor' to identify high CPU processes")
        output.append("3. Consider upgrading CPU if consistently high")
        output.append("4. Check for malware or background tasks")

        return '\n'.join(output)

    @staticmethod
    def check_disk():
        output = []
        output.append("=== Disk Usage Report ===")
        output.append("")

        try:
            result = subprocess.run(["df", "-h"], capture_output=True, text=True)
            output.append(result.stdout)
        except Exception as e:
            output.append(f"无法获取磁盘信息: {e}")

        output.append("")
        output.append("=== Suggestions ===")
        output.append("1. Clean up temporary files if disk >90%")
        output.append("2. Move large files to external storage")
        output.append("3. Use 'du -sh *' to find large directories")
        output.append("4. Consider adding more storage")

        return '\n'.join(output)


if __name__ == "__main__":
    print(run())
