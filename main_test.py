"""
main_test.py  ─  Integration smoke-test for MikaRoll (Windows)

Usage:
    python main_test.py

What it does:
  1. Creates a temporary test.md in the project root.
  2. Launches the UI, auto-selects the test file, triggers conversion.
  3. Waits up to 15 s, then closes the window.
  4. Cleans up test.md and any generated output.
"""

import os
import sys
import threading
import tempfile
import shutil

# ── Ensure we always run from the project root (where main.py lives) ─────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

# ── 1. Create a temporary test Markdown file ──────────────────────────────────
TEST_MD = os.path.join(BASE_DIR, "_smoke_test.md")
TEST_OUT_DIR = tempfile.mkdtemp(prefix="mikaroll_test_")

with open(TEST_MD, "w", encoding="utf-8") as f:
    f.write(
        "# MikaRoll 烟雾测试\n\n"
        "这是一个自动生成的测试文件，用于验证程序能否正常启动并转换。\n\n"
        "## 功能列表\n\n"
        "- Markdown 转 PDF\n"
        "- 图片转换\n"
        "- 音频转换\n\n"
        "## 结论\n\n"
        "如果您看到此 PDF，说明 MikaRoll 工作正常！\n"
    )

print(f"[TEST] Created: {TEST_MD}")
print(f"[TEST] Output dir: {TEST_OUT_DIR}")

# ── 2. Import main module (runs top-level code but NOT mainloop) ──────────────
import main  # noqa: E402  (must be after chdir)

# ── 3. Build the CTk root and app ────────────────────────────────────────────
root = main.CTk_DnD()
root.withdraw()

icon_path = main.get_resource_path("image/icon.ico")
if sys.platform == "win32" and os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"[TEST] Icon (non-fatal): {e}")
else:
    print(f"[TEST] icon.ico not found at {icon_path} – skipping.")

app = main.UniversalConverterApp(root)

def on_close():
    try:
        app.anim.cancel_all()
    except Exception:
        pass
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_close)
root.deiconify()

# ── 4. After UI is ready, simulate selecting the test file ───────────────────
def _run_test():
    try:
        app.handle_input_files([TEST_MD])
        app.output_path_var.set(TEST_OUT_DIR)
        app.target_format_var.set(".pdf")
        print("[TEST] Starting conversion…")
        app.start_conversion()
    except Exception as e:
        print(f"[TEST] Error during test: {e}")

# ── 5. Auto-close after 20 s ─────────────────────────────────────────────────
def _auto_close():
    print("[TEST] Timeout reached – closing window.")
    try:
        app.anim.cancel_all()
    except Exception:
        pass
    root.after(0, root.destroy)

root.after(500, _run_test)
root.after(20_000, _auto_close)

# ── 6. Run mainloop ──────────────────────────────────────────────────────────
try:
    root.mainloop()
except KeyboardInterrupt:
    pass

# ── 7. Cleanup ───────────────────────────────────────────────────────────────
print("[TEST] Cleaning up…")
if os.path.exists(TEST_MD):
    os.remove(TEST_MD)
    print(f"[TEST] Removed: {TEST_MD}")

# List any generated files before removing the temp dir
generated = []
for name in os.listdir(TEST_OUT_DIR):
    full = os.path.join(TEST_OUT_DIR, name)
    generated.append(full)
    print(f"[TEST] Generated: {full}")

shutil.rmtree(TEST_OUT_DIR, ignore_errors=True)
print("[TEST] Temp output dir removed.")
print(f"[TEST] Done. Generated {len(generated)} file(s).")
