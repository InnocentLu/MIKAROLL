# 🚀 项目开发文档：Universal Converter (桌面多功能万能格式转换器)

## 1. 项目概述 (Overview)

### 1.1 项目定位
一款专为 Windows 平台打造的**轻量、极速、开箱即用、无隐私泄漏（完全本地离线处理）**的通用桌面文件格式转换器。支持媒体（音视频/图像）与常见文档（PDF、Markdown、Office 系列）之间的双向/交叉格式转换。

### 1.2 核心设计原则
* **极简交互 (Frictionless UX)：** 拖拽即用，自动识别格式并推荐目标格式，两步完成转换。
* **极致性能与轻量化 (High Performance & Low Footprint)：** 采用现代轻量桌面框架，低内存占用，充分榨干多核 CPU / GPU 硬件加速。
* **模块化转换引擎 (Pluggable Engine Pipeline)：** 各格式转换核心解耦，支持底层命令行工具（CLI）与原生二进制插件的按需调用与便携式（Portable）分发。
* **隐私安全 (Privacy First)：** 所有任务 100% 本地运算，绝不上传任何用户文件。

---

## 2. 技术栈选型 (Technology Stack)

| 层次 | 选型 | 理由与说明 |
|---|---|---|
| **桌面运行时 / 宿主** | **Tauri v2 (Rust + Web前端)** | 打包体积仅 ~10MB，内存占用仅 ~30MB（远胜 Electron）；Rust 原生处理进程调用与文件 IO 性能极佳 |
| **前端 UI 框架** | **React 18 / Vue 3 + Tailwind CSS + shadcn/ui** | 现代极简扁平风格，支持 Fluent Design / Mica 毛玻璃效果，组件库完备 |
| **音视频处理核心** | **FFmpeg (Portable static build) + NVENC/QSV/AMF** | 行业标准，支持 GPU 硬件编解码加速 |
| **图像处理核心** | **ImageMagick CLI / Rust `image` crate / libvips** | 极速批量转码、压缩、ICC 配置文件保留 |
| **文档排版与转换** | **Pandoc + Typst + Poppler (pdftoppm)** | Markdown、HTML、Word(docx)、PDF 互转核心 |
| **Office/PPT 重度转换** | **LibreOffice (Headless CLI) / COM Interop (可选)** | 支持 PPTX/PPT/DOCX 转 PDF 及高保真文档渲染 |
| **状态与队列管理** | **Zustand (前端) + Tokio Async Channel (Rust 后端)** | 高并发异步任务队列，支持任务取消、进度监听 |

---

## 3. 核心功能与转换矩阵 (Feature Matrix)

```
                       ┌──────────────┐
                       │  用户拖入文件 │
                       └──────┬───────┘
                              ▼
                   ┌──────────────────────┐
                   │  文件嗅探 & 格式探测  │
                   │ (Magic bytes / MIME) │
                   └──────────┬───────────┘
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   [ 媒体模块 ]          [ 图片模块 ]         [ 文档模块 ]
  (FFmpeg Engine)      (Magick/vips Engine)  (Pandoc/Office)
         │                    │                    │
         ├─ MP4/MKV/MOV/WebM  ├─ JPG/PNG/WebP/AVIF ├─ PDF ➔ Word/Images
         ├─ MP3/AAC/FLAC/WAV  ├─ SVG/ICO/HEIC/RAW  ├─ Markdown ➔ PDF/DOCX/HTML
         └─ 提取音频 / 压制字幕 └─ 批量无损/有损压缩 └─ PPTX ➔ PDF/图片长图
```

### 3.1 媒体转换 (Audio / Video)
* **视频互转：** MP4, MKV, AVI, MOV, WebM, FLV, TS, GIF。
* **音频互转：** MP3, AAC, FLAC, WAV, OGG, M4A, Opus。
* **快捷操作：** 视频一键提取音频、GIF 动图截取与生成、视频分辨率/码率快速压缩（CRF 模式）。

### 3.2 图像转换 (Image Processing)
* **通用格式：** JPG/JPEG, PNG, WebP, AVIF, BMP, TIFF, ICO (多尺寸合并)。
* **特殊/专业格式：** Apple HEIC/HEIF, SVG 栅格化, 常见 RAW 格式预览与转换。
* **批量辅助：** 批量等比缩放、去除 Exif 元数据（隐私脱敏）、画质压缩。

### 3.3 文档转换 (Documents & Presentations)
* **Markdown 专区：**
  * `MD ➔ PDF`（支持 GitHub 风格 CSS、代码高亮、MathJax 数学公式渲染）。
  * `MD ➔ DOCX / HTML / PPTX`。
* **PPT / 演示文稿专区：**
  * `PPT / PPTX ➔ PDF`（保证排版与字体保真度）。
  * `PPT / PPTX ➔ 连续长图 / 分页高清图片集 (PNG/JPG)`。
* **PDF 综合处理：**
  * `PDF ➔ Word (.docx)`。
  * `PDF ➔ 逐页高清图片 (PNG/JPG)`。
  * `PDF 页面合并 / 提取`。
* **电子书/轻量表格：**
  * `EPUB ➔ MOBI / TXT / PDF`。
  * `CSV ➔ Excel (.xlsx) / JSON` 互转。

---

## 4. 系统架构与底层管线 (Architecture & Pipeline)

### 4.1 目录结构规划
```text
UniversalConverter/
├── src-tauri/                  # Rust 后端核心
│   ├── Cargo.toml
│   ├── binaries/               # 第三方便携二进制工具 (按需下发或内置)
│   │   ├── ffmpeg.exe
│   │   ├── pandoc.exe
│   │   └── pdftoppm.exe
│   └── src/
│       ├── main.rs             # 应用程序入口
│       ├── engine/             # 转换管道核心
│       │   ├── media.rs        # FFmpeg 参数组装与进程执行
│       │   ├── image.rs        # 图像处理管道
│       │   ├── document.rs     # Pandoc / PDF 处理管道
│       │   └── runner.rs       # 统一 CLI 进程拉起与标准流进度解析 (stdout/stderr)
│       └── queue/              # 多任务并发控制与资源调度
│           └── worker.rs
├── src/                        # 前端 (React / Vue)
│   ├── components/
│   │   ├── DropZone.tsx        # 拖拽投放区
│   │   ├── TaskQueue.tsx       # 任务列表与进度条
│   │   ├── SettingsModal.tsx   # 输出路径、线程数、硬件加速配置
│   │   └── PresetSelector.tsx  # 目标格式/预设参数选择器
│   ├── stores/                 # 全局状态 (Zustand / Pinia)
│   ├── hooks/                  # Tauri IPC 事件监听封装
│   └── App.tsx
├── package.json
└── tauri.conf.json
```

### 4.2 核心执行机制 (Process Runner & Progress Parsing)
1. **任务分发：** 前端通过 Tauri IPC 调用 `invoke("convert_task", { task_payload })`。
2. **命令组装：** Rust 层根据输入输出格式匹配最佳预设管线（例如视频压制拼接 `-c:v libx264 -crf 23 -c:a aac`）。
3. **异步子进程监控：** Rust 以异步非阻塞方式启动 `tokio::process::Command`，管道接管 `stderr`。
4. **进度回调：** 正则解析 FFmpeg/Pandoc 输出的进度信息（如 `time=00:01:23.45`），通过 `app_handle.emit_all("task-progress", ...)` 实时向前端广播转换进度百分比。
5. **错误捕获：** 遇到非 0 退出代码时截取尾部 1KB 错误日志返回前端，展示友好错误提示。

---

## 5. UI/UX 详细交互规范 (User Interface)

* **默认视图（空闲态）：**
  * 居中展示极简拖拽框（支持单文件、多文件、整个文件夹拖拽）。
  * 底部显示快捷预设标签（如 `转为 MP4 (H.264)`、`提取为 MP3`、`MD 转 PDF`、`PPT 转长图`）。
* **工作视图（任务态）：**
  * 列表卡片式展示任务，包含：文件名、源格式图标、目标格式下拉菜单、转换预设（高质量/平衡/极速）、进度条、状态（排队中/转换中/成功/失败）、打开所在文件夹按钮。
  * 顶部支持一键“全部开始”、“统一设置目标格式”、“一键清空”。
* **设置中心：**
  * 默认输出目录（源文件同目录 / 自定义目录）。
  * 并发任务上限（根据 CPU 逻辑核心数默认设为 $N/2$ 或 $N-1$）。
  * GPU 编解码开关（自动探测 NVIDIA CUDA / Intel QSV / AMD AMF）。

---

## 6. Antigravity 分阶段实施指令 (Implementation Plan)

请按照以下阶段依序进行代码实现：

```
[Phase 1: 脚手架与基础 IPC] ➔ [Phase 2: 任务队列与前端 UI] ➔ [Phase 3: 转换核心对接] ➔ [Phase 4: 优化与打包]
```

### Phase 1: 项目初始化与底层 CLI 执行器
* 初始化 Tauri v2 + React (TypeScript) + Tailwind CSS 工程。
* 编写 Rust 端统一的 `CommandRunner` 模块，封装子进程拉起、PID 追踪、优雅终止（Kill Process）及流式输出进度抓取逻辑。

### Phase 2: 前端基础交互构建
* 实现全局支持的文件拖拽区域 (`DropZone`)，支持从系统资源管理器直接拖入多格式文件。
* 构建任务状态管理 Store，支持添加、删除、重试、批量修改目标格式。
* 构建具有 Windows 11 Fluent 风格的响应式现代化界面。

### Phase 3: 转换适配器逐项实现
* **适配器 A (Media):** 对接 FFmpeg，实现常见视频/音频格式双向转换与音频提取。
* **适配器 B (Image):** 实现常见图片格式转换、质量调节与 ICO 生成。
* **适配器 C (Document):** 对接 Pandoc 与 Poppler，实现 Markdown 转 PDF/Docx 及 PDF 转图片。
* **适配器 D (PPT):** 实现 PPT/PPTX 转 PDF/图片集的自动化调用管线。

### Phase 4: 异常处理、性能优化与打包
* 加入硬件加速（NVENC/QSV）探测逻辑。
* 完善便携依赖检查机制（若系统未安装 FFmpeg/Pandoc，提示用户一键自动下载或直接打包进 app 内置 bin 目录）。
* 构建最终 Windows x64 便携版 (.exe) 与安装包 (.msi)。

---

## 7. 交付要求与验收标准 (Acceptance Criteria)

1. **零崩溃率：** 面对损坏文件或不支持的格式，能优雅捕获并提示，不影响队列其他任务。
2. **低资源占用：** 闲置时内存消耗小于 50MB，无 CPU 异常占用。
3. **操作简便：** 任意支持的文件拖入后，不超过 2 次点击即可启动转换并成功输出。
