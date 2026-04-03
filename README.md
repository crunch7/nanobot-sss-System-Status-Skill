# nanobot-sss (System Status Skill)

> 检查系统资源使用情况的 nanobot 技能（内存、CPU、磁盘）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![nanobot](https://img.shields.io/badge/powered%20by-nanobot-0078D4.svg)](https://github.com/HKUDS/nanobot)

---

## ✨ 功能

- 📊 **系统概览**: 内存、CPU、磁盘使用情况
- 🔝 **Top 进程**: 列出资源占用最高的 5 个进程
- ⚠️ **异常检测**: 自动识别高占用进程（>500MB）
- 💡 **优化建议**: 根据当前状态提供建议
- 🌐 **跨平台**: Windows / Linux / macOS 全支持
- 🔧 **可配置模式**: 支持单独检查内存/CPU/磁盘

---

## 📦 安装


### 方式 ：手动安装

1. 下载或克隆此仓库
2. 复制 `nanobot-sss-System-Status-Skill`  目录到  `~/.nanobot/workspace/skills/`
3. 重启 nanobot 或开始新对话

---

## 🎯 使用

### 触发短语

- "系统状态"
- "查看系统状态"
- "检查资源"
- "资源监控"
- "SSS"
- "系统怎么样"

### 示例对话

```
用户: 系统状态
助手: [显示内存、CPU、磁盘完整报告，包含 Top 5 进程]

用户: 检查内存
助手: [仅显示内存报告]
```

---

## 🔧 技术细节

### 支持平台

| 平台 | 命令 | 说明 |
|------|------|------|
| **Windows** | PowerShell 脚本 (`sss.ps1`) | 使用 `Get-CimInstance` 和 `Get-Process` |
| **Linux** | Bash 脚本 (`sss.sh`) | 使用 `free`、`top`、`ps`、`df` |
| **macOS** | Bash 脚本 (`sss.sh`) | 使用 `vm_stat`、`top`、`ps`、`df` |

### 输出格式

技能返回结构化的多段报告：

1. **资源概览**: 总容量、已用、可用、使用率
2. **Top 5 进程**: 按资源占用降序排列
3. **异常检测**: 自动标记 >500MB 的进程
4. **优化建议**: 针对当前状态提供建议

### 阈值设置

- **进程警告**: 单进程 >500MB
- **内存使用率**: >70% 提示，>80% 建议检查
- **CPU 使用率**: >80% 建议检查
- **磁盘使用率**: >90% 建议清理

### Shell 脚本参数

```bash
# 显示所有资源（默认）
./sss.sh

# 指定检查模式
./sss.sh --mode memory    # 仅内存
./sss.sh --mode cpu       # 仅 CPU
./sss.sh --mode disk      # 仅磁盘
./sss.sh --mode all       # 全部（默认）
```

### Python 实现改进

`__init__.py` 已重构为**适配器模式**：

- 消除了 Windows/Linux/macOS 三套重复代码
- 使用装饰器注册平台适配器
- 统一的 `run(mode)` 接口
- 更易维护和扩展

---

## 📁 项目结构

```
System Status Skill/
├── SKILL.md          # 技能定义（元数据 + 说明，符合 nanobot 规范）
├── __init__.py       # Python 实现（适配器模式，支持扩展）
├── sss.ps1           # Windows PowerShell 脚本（完整功能）
├── sss.sh            # Linux/macOS Bash 脚本（完整功能 + 参数支持）
├── README.md         # 本文件（GitHub 仓库用）
└── LICENSE           # 许可证文件（MIT）
```

### 文件用途说明

- **SKILL.md**: nanobot 框架读取的技能元数据
- **__init__.py**: 可作为独立Python模块导入，也可直接运行
- **sss.ps1/sss.sh**: 原生脚本，可直接在对应系统执行

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 开启 Pull Request

---

## 📝 更新日志

### v2.0 (2026-04-03)
- 重构 Python 代码为适配器模式，消除平台重复
- Shell 脚本新增 `--mode` 参数，支持内存/CPU/磁盘单独检查
- 统一输出为纯文本，移除所有 ANSI 颜色代码（Agent Skill 友好）
- 修正文档与实际行为不一致（Top 5 进程）
- 提升跨平台一致性和可维护性

---

## 📄 License

MIT License. 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [nanobot](https://github.com/HKUDS/nanobot) - 强大的 AI 助手框架

---

**Made with ❤️ by [Crunch、nanobot]**

---
*Skill ID: sss (System Status Skill)*
