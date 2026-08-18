#!/bin/bash
# ──────────────────────────────────────────────
#  MikaRoll DMG Builder
#  使用 create-dmg 构建带自定义背景的安装镜像
# ──────────────────────────────────────────────
set -e

APP_NAME="MikaRoll"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"
DMG_DIR="dist"
VOLUME_NAME="${APP_NAME} Setup"
BG_IMG="image/dmg_arrow_bg.png"
ICON_PATH="image/icon.ico"

# 检查 .app 是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 找不到 ${APP_PATH}，请先运行 PyInstaller 打包。"
    exit 1
fi

# 检查 create-dmg 是否已安装
if ! command -v create-dmg &> /dev/null; then
    echo "📦 正在通过 Homebrew 安装 create-dmg..."
    brew install create-dmg
fi

echo "📦 正在注入 Playwright Chromium 内核..."
cp -R ~/Library/Caches/ms-playwright "$APP_PATH/Contents/MacOS/"

# 清理旧 DMG
rm -f "${DMG_DIR}/${DMG_NAME}"

echo "🎨 正在构建极简指引版 DMG 安装镜像..."

create-dmg \
    --volname "${VOLUME_NAME}" \
    --volicon "${ICON_PATH}" \
    --background "${BG_IMG}" \
    --window-pos 200 120 \
    --window-size 540 380 \
    --icon-size 110 \
    --icon "${APP_NAME}.app" 140 190 \
    --app-drop-link 400 190 \
    --text-size 14 \
    --no-internet-enable \
    "${DMG_DIR}/${DMG_NAME}" \
    "${APP_PATH}"

echo ""
echo "✅ DMG 构建完成: ${DMG_DIR}/${DMG_NAME}"
echo "🌸 感谢 sensei 把 Mika 带回家！"
