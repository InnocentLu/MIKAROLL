# MikaRoll - Universal Converter (Windows Edition) 🪪

![MikaRoll](image/icon.jpg)

**MikaRoll** 是一款专为 Windows 打造的现代化、全能型本地格式转换工具。拥有极致的极速冷启动架构（<0.3秒响应）和精美的二次元看板娘 GUI（基于 CustomTkinter），支持包括文档、图片、音视频在内的主流格式无缝转换。

## ✨ 核心特性

- **⚡ 工业级极速冷启动**：
  采用现代化的按需代理加载 (Dynamic Lazy Import) 与渐进式骨架屏渲染 (Progressive UI Hydration)，取消了一切顶层重型阻塞，搭配 Per-Monitor V2 DPI 感知，实现双击即开的顺滑体验。
- **📄 文档转换 (Doc Engine)**：
  内置 Playwright 强力内核驱动的 Markdown 转 PDF / HTML，支持精准的相对/绝对路径本地图片 Base64 极速内嵌，不碎图。完美兼容 Docx, PPTX 等日常文档。
- **🖼️ 图像转换 (Image Engine)**：
  支持海量图片互转，完美兼容原生 HEIF/AVIF 苹果与现代格式解码。
- **🎵 音视频解析 (Media Engine)**：
  自动化音频/视频封装抽取，甚至支持特定加密格式的自动解密流水线。
- **📦 极致分发体系**：
  摒弃传统 Onefile 解压惩罚，采用 PyInstaller Onedir 配合 Inno Setup 固实压缩 (LZMA2) 方案，提供完美的桌面快捷方式及系统集成安装向导。

## 🚀 下载与安装

请前往右侧的 **[Releases](../../releases)** 专栏，下载最新版本的 `MikaRoll_v2.0_Setup.exe` 安装包。
- 采用绿色单文件安装器，双击即可无脑安装。
- 安装完毕后，桌面会自动生成 `MikaRoll` 快捷方式。

## 🛠️ 开发与构建 (Build from Source)

如果你想要在本地二次开发或者自行编译最新版本：

1. **环境准备**：
   建议使用 Conda 配合 Python 3.12+ (原生支持 Tcl/Tk 9.0)：
   ```bash
   pip install -r requirements.txt
   ```
2. **调试运行**：
   ```bash
   python main.py
   ```
3. **一键构建极速单目录版 (Onedir)**：
   我们提供了全自动化的构建脚本 `build.py`，它会自动嗅探 Conda 环境的 Tcl/Tk DLL，禁用 UPX，并开启字节码极致优化。
   ```bash
   python build.py
   ```
4. **生成 Inno Setup 安装包**：
   - 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)
   - 右键点击根目录的 `setup.iss`，选择 **Compile** 即可在 Output 目录生成对应的 `.exe` 安装向导。

## 📜 许可证 (License)

MIT License.
