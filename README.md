# MikaRoll (macOS 版)

专为 macOS 打造的高颜值通用文档转换工具，支持 PPT/Markdown 转 PDF 等格式，内置高质量排版引擎，支持公式渲染与自动预览。

## 核心特性
* **原生拖拽转换与极简工作流**：支持将文件直接拖入窗口进行极速转换。
* **Markdown 矢量数学公式（KaTeX/MathJax）高保真渲染**：彻底告别字符乱码，完美支持学术排版。
* **专属 Mika 视觉主题与彩蛋交互**：令人赏心悦目的粉紫色渐变 UI 与温馨的初次启动彩蛋。
* **独立打包与开箱即用支持**：提供 DMG 安装包，内置完整的 Playwright/Chromium 渲染内核，告别繁琐的环境配置。

## 安装与使用指南

### 方式一：使用 DMG 安装（推荐）
1. 在 [Releases](https://github.com/InnocentLu/MIKAROLL/releases) 页面下载最新的 `MikaRoll.dmg`。
2. 双击打开 DMG 镜像。
3. 将左侧的 `MikaRoll.app` 图标拖拽到右侧的 `Applications` 文件夹即可完成安装。
4. 在启动台（Launchpad）或应用程序文件夹中点击 `MikaRoll` 启动（首次启动有特别彩蛋！）。

### 方式二：通过 Conda 源码运行
1. 克隆本仓库源码：
   ```bash
   git clone -b macos-release https://github.com/InnocentLu/MIKAROLL.git
   cd MIKAROLL
   ```
2. 创建并激活 Conda 环境：
   ```bash
   conda create -n mikaroll python=3.10
   conda activate mikaroll
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. 运行主程序：
   ```bash
   python main.py
   ```

## 开发与打包指南

如果你想自行编译生成 `.app` 和 `.dmg` 安装包，请按照以下步骤操作：

### 1. 构建 .app
项目使用 PyInstaller 进行应用程序打包，核心配置文件为 `MikaRoll_mac.spec`：
```bash
pyinstaller MikaRoll_mac.spec --clean
```
打包成功后，生成的 `MikaRoll.app` 会位于 `dist/` 目录下。

### 2. 构建 .dmg
确保你已经安装了 `create-dmg`（可通过 `brew install create-dmg` 安装）。然后在项目根目录运行定制的打包脚本：
```bash
./build_dmg.sh
```
该脚本会自动：
- 注入 Playwright 的 Chromium 内核以确保独立运行
- 构建原生的拖拽式 DMG 界面（纯色底版+居中箭头指引）
最终产物将输出在 `dist/MikaRoll.dmg`。
