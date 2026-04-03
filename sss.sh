#!/bin/bash

# System Status Skill (SSS) - Linux/macOS Shell Script
# 查看系统资源使用情况（内存、CPU、磁盘）

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认模式
MODE="all"

# 解析参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --mode|-m)
            MODE="${2:-all}"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--mode MODE]"
            echo "Modes:"
            echo "  all      - 显示所有资源信息（默认）"
            echo "  memory  - 仅内存"
            echo "  cpu     - 仅 CPU"
            echo "  disk    - 仅磁盘"
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# 获取系统类型
is_macos() {
    [[ "$OSTYPE" == "darwin"* ]]
}

# ========== 内存检查 ==========

check_memory() {
    echo -e "${CYAN}=== Memory Usage Report ===${NC}"

    if is_macos; then
        # macOS: 使用 vm_stat
        TOTAL_PAGES=$(vm_stat | grep "Pages free:" | awk '{print $3}' | tr -d '.')
        ACTIVE_PAGES=$(vm_stat | grep "Pages active:" | awk '{print $3}' | tr -d '.')
        INACTIVE_PAGES=$(vm_stat | grep "Pages inactive:" | awk '{print $3}' | tr -d '.')
        WIRING_PAGES=$(vm_stat | grep "Pages wired down:" | awk '{print $4}' | tr -d '.')
        TOTAL_BYTES=$(( (TOTAL_PAGES + ACTIVE_PAGES + INACTIVE_PAGES + WIRING_PAGES) * 4096 ))
        TOTAL_GB=$(echo "scale=2; $TOTAL_BYTES / 1024 / 1024 / 1024" | bc)

        # 计算已用（粗略估算）
        USED_PAGES=$(( ACTIVE_PAGES + INACTIVE_PAGES + WIRING_PAGES ))
        USED_BYTES=$(( USED_PAGES * 4096 ))
        USED_GB=$(echo "scale=2; $USED_BYTES / 1024 / 1024 / 1024" | bc)
        FREE_GB=$(echo "scale=2; $TOTAL_GB - $USED_GB" | bc)
        USAGE_PCT=$(echo "scale=2; ($USED_GB / $TOTAL_GB) * 100" | bc)
    else
        # Linux: 使用 free
        MEM_INFO=$(free -b 2>/dev/null || free -k 2>/dev/null)
        if echo "$MEM_INFO" | grep -q "Mem:"; then
            TOTAL_BYTES=$(echo "$MEM_INFO" | awk '/Mem:/ {print $2}')
            USED_BYTES=$(echo "$MEM_INFO" | awk '/Mem:/ {print $3}')
            FREE_BYTES=$(echo "$MEM_INFO" | awk '/Mem:/ {print $7}')
            # 转换为GB
            UNIT="B"
            if [[ $TOTAL_BYTES -gt 1073741824 ]]; then
                UNIT="GB"
                TOTAL_GB=$(echo "scale=2; $TOTAL_BYTES / 1024 / 1024 / 1024" | bc)
                USED_GB=$(echo "scale=2; $USED_BYTES / 1024 / 1024 / 1024" | bc)
                FREE_GB=$(echo "scale=2; $FREE_BYTES / 1024 / 1024 / 1024" | bc)
            elif [[ $TOTAL_BYTES -gt 1048576 ]]; then
                UNIT="MB"
                TOTAL_GB=$(echo "scale=2; $TOTAL_BYTES / 1024 / 1024" | bc)
                USED_GB=$(echo "scale=2; $USED_BYTES / 1024 / 1024" | bc)
                FREE_GB=$(echo "scale=2; $FREE_BYTES / 1024 / 1024" | bc)
            else
                TOTAL_GB="$TOTAL_BYTES"
                USED_GB="$USED_BYTES"
                FREE_GB="$FREE_BYTES"
            fi
            USAGE_PCT=$(echo "scale=2; ($USED_BYTES / $TOTAL_BYTES) * 100" | bc)
        else
            echo "无法获取内存信息"
            return 1
        fi
    fi

    echo ""
    echo "Total Memory: $TOTAL_GB GB"
    echo "Used: $USED_GB GB"
    echo "Available: $FREE_GB GB"

    # 设置颜色
    USAGE_INT=$(echo "$USAGE_PCT" | cut -d'.' -f1)
    if [ "$USAGE_INT" -gt 80 ]; then
        echo -e "Usage: ${RED}$USAGE_PCT %${NC}"
    elif [ "$USAGE_INT" -gt 70 ]; then
        echo -e "Usage: ${YELLOW}$USAGE_PCT %${NC}"
    else
        echo -e "Usage: ${GREEN}$USAGE_PCT %${NC}"
    fi

    echo ""
    echo -e "${CYAN}=== Top 5 Memory Processes ===${NC}"

    if is_macos; then
        # macOS
        ps aux -r -o pid,user,%mem,vsz,rss,comm | head -n 6
    else
        ps aux --sort=-%mem | head -n 6
    fi

    echo ""
    echo -e "${CYAN}=== Anomaly Detection ===${NC}"
    HIGH_MEM_COUNT=0
    if is_macos; then
        ps aux | awk '$10 > 500000 {print $11 ": " $10/1024 " MB"; HIGH_MEM_COUNT++}'
    else
        ps aux | awk '$4 > 500 {print $11 ": " $4/1024 " MB"; HIGH_MEM_COUNT++}'
    fi

    if [ "$HIGH_MEM_COUNT" -eq 0 ]; then
        echo -e "${GREEN}No single process using >500MB${NC}"
    fi

    echo ""
    echo -e "${CYAN}=== Suggestions ===${NC}"
    echo "1. If memory usage >80%, close unnecessary programs"
    echo "2. Check for unknown processes"
    echo "3. Use system monitor for details (htop, top, Activity Monitor)"
    echo "4. Restart to free memory"
}

# ========== CPU 检查 ==========

check_cpu() {
    echo -e "${CYAN}=== CPU Usage Report ===${NC}"

    if is_macos; then
        # macOS: 使用 top
        result=$(top -l 1 2>/dev/null | grep -E 'CPU usage|Cpu' | head -1)
        echo "$result"

        # 获取核心数
        CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "Unknown")
    else
        # Linux: 使用 top 或 /proc/stat
        result=$(top -bn1 2>/dev/null | grep -E '%Cpu(s)' | head -1 || cat /proc/stat | head -1)
        echo "$result"

        # 获取核心数
        CORES=$(nproc 2>/dev/null || grep -c '^processor' /proc/cpuinfo 2>/dev/null || echo "Unknown")
    fi

    echo ""
    echo "Logical Cores: $CORES"
    echo ""

    echo -e "${CYAN}=== Top 5 CPU Processes ===${NC}"

    if is_macos; then
        ps aux -r -o pid,user,%cpu,comm | head -n 6
    else
        ps aux --sort=-%cpu | head -n 6
    fi

    echo ""
    echo -e "${CYAN}=== Suggestions ===${NC}"
    echo "1. If CPU usage >80%, check for runaway processes"
    echo "2. Use 'top' or 'htop' to identify high CPU processes"
    echo "3. Consider upgrading CPU if consistently high"
    echo "4. Check for malware or background tasks"
}

# ========== 磁盘检查 ==========

check_disk() {
    echo -e "${CYAN}=== Disk Usage Report ===${NC}"

    if df -h 2>/dev/null | head -1 >/dev/null; then
        df -h
    else
        echo "无法获取磁盘信息"
        return 1
    fi

    echo ""
    echo -e "${CYAN}=== Suggestions ===${NC}"
    echo "1. Clean up temporary files if disk >90%"
    echo "2. Move large files to external storage"
    echo "3. Use 'du -sh *' to find large directories"
    echo "4. Consider adding more storage"
}

# ========== 主程序 ==========

case "$MODE" in
    all)
        check_memory
        echo ""
        check_cpu
        echo ""
        check_disk
        ;;
    memory)
        check_memory
        ;;
    cpu)
        check_cpu
        ;;
    disk)
        check_disk
        ;;
    *)
        echo "Invalid mode: $MODE"
        echo "Valid modes: all, memory, cpu, disk"
        exit 1
        ;;
esac
