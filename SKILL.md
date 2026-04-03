# SSS (System Status Skill)

## Description
查看系统资源使用情况的技能。提供内存、CPU、磁盘的详细报告，帮助监控系统状态。

## Usage
当用户询问系统资源、性能监控、系统状态等相关问题时使用此技能。

## Capabilities
- **系统概览**: 内存、CPU、磁盘的总体使用情况
- **详细报告**: 各资源详细数据 + Top 5 占用进程
- **异常检测**: 自动识别高占用进程和资源瓶颈
- **优化建议**: 根据当前状态提供建议

## Parameters
此技能不需要参数，直接执行即可。

## Examples
- "系统状态"
- "查看系统状态"
- "检查资源"
- "资源监控"
- "SSS"
- "系统怎么样"

## Implementation
该技能根据操作系统自动选择对应命令：
- **Windows**: `sss.ps1` - PowerShell 脚本
- **Linux**: `sss.sh` - Bash 脚本
- **macOS**: `sss.sh` - Bash 脚本

所有平台统一显示 Top 5 占用最高的进程。

Shell脚本 (`sss.sh`) 支持 `--mode` 参数：
- `memory` - 仅内存检查
- `cpu` - 仅 CPU 检查
- `disk` - 仅磁盘检查
- `all` - 全部检查（默认）

## Output
返回格式化的报告，包括：
- 总体资源统计
- Top 5 进程列表（按资源占用排序）
- 优化建议

## Notes
- **跨平台支持**: Windows / Linux / macOS
- 进程数量限制为 5 条，保持输出简洁
- 输出为纯文本，便于程序捕获和解析
- Python 实现 (`__init__.py`) 使用适配器模式，消除了平台重复代码，更易维护
- Shell 脚本 (`sss.sh`) 支持模式参数，可单独检查某一资源
