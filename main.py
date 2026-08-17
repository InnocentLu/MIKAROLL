import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageSequence

import sys

def get_resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境与 PyInstaller 打包环境 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

import json

def get_data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    config_path = os.path.join(get_data_dir(), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_config(key, value):
    config_path = os.path.join(get_data_dir(), "config.json")
    cfg = load_config()
    cfg[key] = value
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    class TkinterDnD:
        class Tk(tk.Tk): pass

from engines.image_engine import convert_image
from engines.audio_engine import convert_audio_video
from engines.doc_engine import convert_document
from utils.helpers import get_unique_filename

CONVERSION_MAP = {
    '.pptx': ['.pdf', '.docx', '.png', '.jpg'],
    '.ppt': ['.pdf', '.docx', '.png', '.jpg'],
    '.docx': ['.pdf', '.md', '.txt'],
    '.doc': ['.pdf', '.md', '.txt'],
    '.pdf': ['.docx', '.png', '.jpg', '.txt'],
    '.md': ['.pdf', '.docx', '.html', '.txt'],
    '.markdown': ['.pdf', '.docx', '.html', '.txt'],
    '.jpg': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.jpeg': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.png': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.webp': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.bmp': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.tiff': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.ico': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.avif': ['.png', '.jpg', '.webp', '.bmp', '.ico'],
    '.mp3': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.wav': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.flac': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.aac': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.ogg': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.m4a': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.mflac': ['.flac', '.mp3', '.wav', '.aac', '.ogg'],
    '.mflac0': ['.flac', '.mp3', '.wav', '.aac', '.ogg'],
    '.mgg': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.mgg0': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.mgg1': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.mggl': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.qmcflac': ['.flac', '.mp3', '.wav', '.aac', '.ogg'],
    '.qmcogg': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.qmc0': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.qmc2': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.qmc3': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    '.qmc4': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.qmc6': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.qmc8': ['.ogg', '.mp3', '.wav', '.flac', '.aac'],
    '.mp4': ['.mp3', '.wav', '.gif', '.mp4'],
    '.mkv': ['.mp3', '.wav', '.gif', '.mp4'],
    '.avi': ['.mp3', '.wav', '.gif', '.mp4'],
    '.mov': ['.mp3', '.wav', '.gif', '.mp4'],
}

THEMES = {
    "浅紫": {
        "mode": "light",
        "bg": "#F3F0FF",
        "frame_bg": "#E8E1FF",
        "btn_primary": "#9B82F3",
        "text": "#3D2B8E"
    },
    "少女粉": {
        "mode": "light",
        "bg": "#FFF0F5",
        "frame_bg": "#FFE4E1",
        "btn_primary": "#FF9FB3",
        "text": "#4A4A4A"
    },
    "浅绿": {
        "mode": "light",
        "bg": "#F0FFF0",
        "frame_bg": "#E8F5E9",
        "btn_primary": "#81C784",
        "text": "#2E7D32"
    },
    "淡蓝": {
        "mode": "light",
        "bg": "#F0F8FF",
        "frame_bg": "#E3F2FD",
        "btn_primary": "#64B5F6",
        "text": "#1565C0"
    }
}

if HAS_DND:
    class CTk_DnD(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class CTk_DnD(ctk.CTk):
        pass


# ─────────────────────────────────────────────
#  工具函数：hex 颜色插值
# ─────────────────────────────────────────────
# Tkinter named-gray → hex lookup table
_GRAY_HEX = {
    'gray14': '#242424',
    'gray17': '#2b2b2b',
    'gray22': '#383838',
    'gray25': '#404040',
    'gray50': '#808080',
    'gray90': '#e5e5e5',
}

def _normalize_color(c: str) -> str:
    """把 'grayXX' 形式规范化为 hex，其他 hex 直接返回"""
    c = c.strip()
    if c in _GRAY_HEX:
        return _GRAY_HEX[c]
    if c.startswith('gray'):
        try:
            v = int(float(c[4:]) / 100 * 255)
            return _rgb_to_hex(v, v, v)
        except Exception:
            return '#c8c8c8'
    return c

def _hex_to_rgb(hex_color: str):
    """将 '#RRGGBB' 或 'grayXX' 转为 (r,g,b)"""
    hex_color = _normalize_color(hex_color)
    hx = hex_color.lstrip('#')
    if len(hx) == 3:
        hx = ''.join(c*2 for c in hx)
    try:
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (128, 128, 128)

def _rgb_to_hex(r, g, b):
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def _lerp_color(c1: str, c2: str, t: float) -> str:
    """在两个颜色之间线性插值，t ∈ [0,1]"""
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

def _adjust_color(hex_color, amount=10):
    hex_color = hex_color.lstrip('#')
    if hex_color.startswith('gray') or len(hex_color) < 6:
        return '#888888'
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, min(255, r + amount))
    g = max(0, min(255, g + amount))
    b = max(0, min(255, b + amount))
    return f'#{r:02x}{g:02x}{b:02x}'


# ─────────────────────────────────────────────
#  AnimationManager：统一管理所有动画
# ─────────────────────────────────────────────
class AnimationManager:
    """
    集中管理 Tkinter after() 定时动画，避免多处 after_cancel 遗漏导致的内存泄漏。
    """
    def __init__(self, root):
        self.root = root
        self._tasks = {}          # name -> after_id
        self._bindings = {}       # widget -> (enter_id, leave_id)

    def cancel(self, name):
        if name in self._tasks:
            try:
                self.root.after_cancel(self._tasks[name])
            except Exception:
                pass
            del self._tasks[name]

    def cancel_all(self):
        for name in list(self._tasks.keys()):
            self.cancel(name)

    def schedule(self, name, delay_ms, callback):
        self.cancel(name)
        aid = self.root.after(delay_ms, callback)
        self._tasks[name] = aid

    # ── 1. 卡片悬停浮起 ──────────────────────────────────
    def hover_float(self, widget, color_getter, steps=8, interval=15):
        """
        绑定卡片悬停渐变效果。
        color_getter: 调用时返回 (base_color, hover_color) 元组的函数。
        每次动画执行时动态读取当前主题颜色，避免题色固化导致的错乱。
        """
        state = {'t': 0.0, 'direction': 0}

        def _animate():
            d = state['direction']
            if d == 0:
                return
            t = max(0.0, min(1.0, state['t'] + d / steps))
            state['t'] = t
            try:
                base, hover = color_getter()
                widget.configure(fg_color=_lerp_color(base, hover, t))
            except Exception:
                return
            if (d == 1 and t < 1.0) or (d == -1 and t > 0.0):
                self.schedule(f'hover_{id(widget)}', interval, _animate)

        def _on_enter(e):
            # 只有当鼠标真正进入卡片内部（而非子控件之间移动）时才触发
            if e.widget == widget or str(e.widget).startswith(str(widget)):
                state['direction'] = 1
                _animate()

        def _on_leave(e):
            # 只有鼠标真正离开整个卡片范围时才触发还原
            try:
                x, y = e.x_root, e.y_root
                wx = widget.winfo_rootx()
                wy = widget.winfo_rooty()
                ww = widget.winfo_width()
                wh = widget.winfo_height()
                if not (wx <= x < wx + ww and wy <= y < wy + wh):
                    state['direction'] = -1
                    _animate()
            except Exception:
                state['direction'] = -1
                _animate()

        return _on_enter, _on_leave

    def _bind_children(self, widget, event, callback):
        for child in widget.winfo_children():
            try:
                child.bind(event, callback, add='+')
            except Exception:
                pass
            self._bind_children(child, event, callback)

    # ── 2. 按钮呼吸光晕 ──────────────────────────────────
    def start_pulse(self, widget, color1: str, color2: str, period_ms=1200):
        """让按钮颜色在 color1 ↔ color2 间缓慢呼吸"""
        self.cancel('pulse')
        import math
        start_time = [0]
        import time
        start_time[0] = time.time()

        def _pulse():
            elapsed = time.time() - start_time[0]
            t = (math.sin(elapsed * 2 * math.pi / (period_ms / 1000)) + 1) / 2
            try:
                widget.configure(fg_color=_lerp_color(color1, color2, t))
            except Exception:
                return
            self.schedule('pulse', 30, _pulse)

        _pulse()

    def stop_pulse(self, widget, restore_color: str):
        self.cancel('pulse')
        try:
            widget.configure(fg_color=restore_color)
        except Exception:
            pass

    # ── 3. 拖入/选择闪光反馈 ──────────────────────────────
    def flash_widget(self, widget, flash_color: str, base_color: str, flashes=2, duration=120):
        """快速闪烁 widget 背景色"""
        self.cancel('flash')
        seq = ([flash_color, base_color] * flashes)
        idx = [0]

        def _next():
            if idx[0] >= len(seq):
                try:
                    widget.configure(fg_color=base_color)
                except Exception:
                    pass
                return
            try:
                widget.configure(fg_color=seq[idx[0]])
            except Exception:
                return
            idx[0] += 1
            self.schedule('flash', duration, _next)

        _next()

    # ── 4. 打字机状态文字 ──────────────────────────────────
    def typewriter(self, var: tk.StringVar, full_text: str, delay_ms=25):
        """逐字显示 full_text 到 StringVar"""
        self.cancel('typewriter')
        var.set('')
        chars = [0]

        def _type():
            n = chars[0]
            if n <= len(full_text):
                var.set(full_text[:n])
                chars[0] = n + 1
                self.schedule('typewriter', delay_ms, _type)

        _type()

    # ── 5. 主题背景颜色渐变过渡 ──────────────────────────────
    def fade_bg(self, widget, from_color: str, to_color: str, steps=16, interval=18, attr='fg_color'):
        """在 steps 帧内将 widget 的背景色从 from_color 渐变到 to_color"""
        self.cancel(f'fade_{id(widget)}')
        step = [0]

        def _fade():
            s = step[0]
            if s > steps:
                return
            t = s / steps
            color = _lerp_color(from_color, to_color, t)
            try:
                if attr == 'fg_color':
                    widget.configure(fg_color=color)
                else:
                    widget.configure(**{attr: color})
            except Exception:
                return
            step[0] += 1
            self.schedule(f'fade_{id(widget)}', interval, _fade)

        _fade()


# ─────────────────────────────────────────────
#  MascotManager
# ─────────────────────────────────────────────
class MascotManager:
    def __init__(self, parent_widget, size=(300, 360)):
        self.parent = parent_widget
        self.size = size
        self.frames = []
        self.start_img = None
        self.down_img = None
        self.gif_delay = 50
        
        self.is_doing = False
        self.frame_idx = 0
        self.timer_id = None
        
        self.label = ctk.CTkLabel(self.parent, text="看板娘图片缺失\n(请在image文件夹放start/doing/down)", font=ctk.CTkFont(size=14))
        self.label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self._load_images()
        self.show_start()
        
    def _get_proportional_size(self, img_size):
        orig_w, orig_h = img_size
        max_w, max_h = self.size
        ratio = min(max_w / orig_w, max_h / orig_h)
        return (int(orig_w * ratio), int(orig_h * ratio))

    def _load_images(self):
        try:
            start_png = get_resource_path("image/start.png")
            start_jpg = get_resource_path("image/start.jpg")
            if os.path.exists(start_png):
                img = Image.open(start_png)
                self.start_img = ctk.CTkImage(light_image=img, dark_image=img, size=self._get_proportional_size(img.size))
            elif os.path.exists(start_jpg):
                img = Image.open(start_jpg)
                self.start_img = ctk.CTkImage(light_image=img, dark_image=img, size=self._get_proportional_size(img.size))
                
            down_jpg = get_resource_path("image/down.jpg")
            if os.path.exists(down_jpg):
                img = Image.open(down_jpg)
                self.down_img = ctk.CTkImage(light_image=img, dark_image=img, size=self._get_proportional_size(img.size))
                
            doing_gif = get_resource_path("image/doing.gif")
            doing_jpg = get_resource_path("image/doing.jpg")
            doing_png = get_resource_path("image/doing.png")
            if os.path.exists(doing_gif):
                gif = Image.open(doing_gif)
                self.gif_delay = gif.info.get('duration', 50) or 50
                target_sz = self._get_proportional_size(gif.size)
                for frame in ImageSequence.Iterator(gif):
                    frame_img = frame.copy().convert("RGBA")
                    self.frames.append(ctk.CTkImage(light_image=frame_img, dark_image=frame_img, size=target_sz))
            elif os.path.exists(doing_jpg):
                img = Image.open(doing_jpg)
                self.frames.append(ctk.CTkImage(light_image=img, dark_image=img, size=self._get_proportional_size(img.size)))
            elif os.path.exists(doing_png):
                img = Image.open(doing_png)
                self.frames.append(ctk.CTkImage(light_image=img, dark_image=img, size=self._get_proportional_size(img.size)))
        except Exception as e:
            print(f"Mascot load error: {e}")

    def show_start(self):
        self.is_doing = False
        self._cancel_timer()
        if self.start_img:
            self.label.configure(image=self.start_img, text="")
            
    def show_down(self):
        self.is_doing = False
        self._cancel_timer()
        if self.down_img:
            self.label.configure(image=self.down_img, text="")
            
    def start_doing(self):
        self.is_doing = True
        self.frame_idx = 0
        if self.frames:
            self._animate_loop()

    def _animate_loop(self):
        if not self.is_doing or not self.frames:
            return
        self.label.configure(image=self.frames[self.frame_idx], text="")
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.timer_id = self.parent.after(self.gif_delay, self._animate_loop)
        
    def _cancel_timer(self):
        if self.timer_id is not None:
            self.parent.after_cancel(self.timer_id)
            self.timer_id = None


# ─────────────────────────────────────────────
#  主应用
# ─────────────────────────────────────────────
class UniversalConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MikaRoll - Universal Converter")
        self.root.geometry("980x680")
        self.root.minsize(850, 600)
        
        ctk.set_default_color_theme("blue")
        
        # 动画管理器
        self.anim = AnimationManager(root)
        
        self.card_frames = []
        self.primary_buttons = []
        self.secondary_buttons = []
        self.labels = []

        # ── 顶部栏 ──────────────────────────────
        top_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        top_frame.pack(fill=tk.X, padx=25, pady=(15, 0))
        
        title_lbl = ctk.CTkLabel(top_frame, text="MikaRoll", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.pack(side=tk.LEFT)
        self.labels.append(title_lbl)
        
        self.theme_combo = ctk.CTkOptionMenu(
            top_frame,
            values=list(THEMES.keys()),
            command=self.on_theme_change,
            width=130,
            height=34,
            corner_radius=10,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            dropdown_font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        )
        self.theme_combo.pack(side=tk.RIGHT)
        
        theme_lbl = ctk.CTkLabel(top_frame, text="视觉主题: ", font=ctk.CTkFont(weight="bold"))
        theme_lbl.pack(side=tk.RIGHT, padx=(0, 10))
        self.labels.append(theme_lbl)

        # ── 中部双栏 ─────────────────────────────
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(15, 25))

        left_pane = ctk.CTkFrame(self.main_frame, fg_color="transparent", width=460)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        # ── Step 1: 导入文件 ──
        self.drop_area = ctk.CTkFrame(left_pane, corner_radius=15)
        self.drop_area.pack(fill=tk.X, pady=(0, 15))
        self.card_frames.append(self.drop_area)

        lbl1 = ctk.CTkLabel(self.drop_area, text="第一步: 导入文件 (支持拖拽)", font=ctk.CTkFont(weight="bold"))
        lbl1.pack(anchor=tk.W, padx=15, pady=(15, 5))
        self.labels.append(lbl1)

        row1 = ctk.CTkFrame(self.drop_area, fg_color="transparent")
        row1.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.input_path_var = tk.StringVar()
        self.input_entry = ctk.CTkEntry(row1, textvariable=self.input_path_var, height=35)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.input_entry.bind('<KeyRelease>', self.on_input_change)

        self.browse_input_btn = ctk.CTkButton(
            row1, text="浏览...", command=self.browse_input, width=80, height=35,
            fg_color="transparent", border_width=2
        )
        self.browse_input_btn.pack(side=tk.RIGHT)
        self.secondary_buttons.append(self.browse_input_btn)

        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        else:
            warn_lbl = ctk.CTkLabel(self.drop_area, text="提示: 未检测到 tkinterdnd2，无法支持拖拽", text_color="#E57373")
            warn_lbl.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # ── Step 2: 目标格式 ──
        format_frame = ctk.CTkFrame(left_pane, corner_radius=15)
        format_frame.pack(fill=tk.X, pady=(0, 15))
        self.card_frames.append(format_frame)

        lbl2 = ctk.CTkLabel(format_frame, text="第二步: 选择目标格式", font=ctk.CTkFont(weight="bold"))
        lbl2.pack(anchor=tk.W, padx=15, pady=(15, 5))
        self.labels.append(lbl2)

        row2 = ctk.CTkFrame(format_frame, fg_color="transparent")
        row2.pack(fill=tk.X, padx=15, pady=(0, 15))

        lbl_to = ctk.CTkLabel(row2, text="转换为:")
        lbl_to.pack(side=tk.LEFT, padx=(0, 10))
        self.labels.append(lbl_to)

        self.target_format_var = tk.StringVar(value="请先选择源文件")
        self.format_combo = ctk.CTkOptionMenu(
            row2, variable=self.target_format_var,
            values=["请先选择源文件"],
            width=150, height=35,
            corner_radius=10,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            dropdown_font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        )
        self.format_combo.pack(side=tk.LEFT)

        # ── Step 3: 输出设置 ──
        dir_frame = ctk.CTkFrame(left_pane, corner_radius=15)
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        self.card_frames.append(dir_frame)

        lbl3 = ctk.CTkLabel(dir_frame, text="第三步: 输出设置", font=ctk.CTkFont(weight="bold"))
        lbl3.pack(anchor=tk.W, padx=15, pady=(15, 5))
        self.labels.append(lbl3)

        row3 = ctk.CTkFrame(dir_frame, fg_color="transparent")
        row3.pack(fill=tk.X, padx=15, pady=(0, 10))

        lbl_out = ctk.CTkLabel(row3, text="输出目录:")
        lbl_out.pack(side=tk.LEFT, padx=(0, 10))
        self.labels.append(lbl_out)

        self.output_path_var = tk.StringVar()
        self.output_entry = ctk.CTkEntry(row3, textvariable=self.output_path_var, height=35)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        self.browse_out_btn = ctk.CTkButton(
            row3, text="更改...", command=self.browse_output, width=80, height=35,
            fg_color="transparent", border_width=2
        )
        self.browse_out_btn.pack(side=tk.RIGHT)
        self.secondary_buttons.append(self.browse_out_btn)

        self.filename_mode_var = tk.StringVar(value="keep")
        self.keep_rb = ctk.CTkRadioButton(
            dir_frame, text="保持原文件名",
            variable=self.filename_mode_var, value="keep",
            command=self.on_filename_mode_change
        )
        self.keep_rb.pack(anchor=tk.W, padx=15, pady=(0, 10))

        row4 = ctk.CTkFrame(dir_frame, fg_color="transparent")
        row4.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.custom_rb = ctk.CTkRadioButton(
            row4, text="自定义文件名",
            variable=self.filename_mode_var, value="custom",
            command=self.on_filename_mode_change
        )
        self.custom_rb.pack(side=tk.LEFT, padx=(0, 15))

        self.custom_filename_var = tk.StringVar()
        self.custom_filename_entry = ctk.CTkEntry(row4, textvariable=self.custom_filename_var, height=35, state='disabled')
        self.custom_filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.open_folder_btn = ctk.CTkButton(
            left_pane, text="打开输出文件夹",
            command=self.open_output_folder, height=45,
            fg_color="transparent", border_width=2
        )
        self.secondary_buttons.append(self.open_folder_btn)

        # ── 右栏：看板娘 + 状态区 ──
        right_pane = ctk.CTkFrame(self.main_frame, corner_radius=15, width=400)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right_pane.pack_propagate(False)
        self.card_frames.append(right_pane)

        mascot_frame = ctk.CTkFrame(right_pane, fg_color="transparent")
        mascot_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.mascot_mgr = MascotManager(mascot_frame, size=(340, 420))

        bottom_right = ctk.CTkFrame(right_pane, fg_color="transparent")
        bottom_right.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)

        self.status_var = tk.StringVar(value="就绪：等待导入文件")
        self.status_label = ctk.CTkLabel(
            bottom_right, textvariable=self.status_var,
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=350, justify="left"
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        self.labels.append(self.status_label)

        self.progress_bar = ctk.CTkProgressBar(bottom_right, height=12, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))

        self.convert_btn = ctk.CTkButton(
            bottom_right, text="开 始 转 换",
            font=ctk.CTkFont(weight="bold", size=18),
            command=self.start_conversion, height=55
        )
        self.convert_btn.pack(fill=tk.X)
        self.primary_buttons.append(self.convert_btn)

        self._is_breathing = False

        # ── 应用初始主题 ──
        saved_theme = load_config().get("theme", "淡蓝")
        if saved_theme not in THEMES:
            saved_theme = "淡蓝"
        self.theme_combo.set(saved_theme)
        self._current_theme = saved_theme
        self.on_theme_change(saved_theme, animate=False)

    # ─────────────────────────────────────────────
    #  主题应用
    # ─────────────────────────────────────────────
    def on_theme_change(self, theme_name, animate=True):
        save_config("theme", theme_name)
        cfg = THEMES[theme_name]

        old_theme = getattr(self, '_current_theme', theme_name)
        old_cfg   = THEMES.get(old_theme, cfg)
        self._current_theme = theme_name

        # 所有主题均为浅色模式，统一 set_appearance_mode
        ctk.set_appearance_mode(cfg['mode'])

        bg           = cfg['bg']
        frame_bg     = cfg['frame_bg']
        btn_primary  = cfg['btn_primary']
        text_color   = cfg['text']
        btn_hover    = _adjust_color(btn_primary, -20)
        border_color = btn_primary

        # 背景丝滑渐变（同为浅色模式，无跨模式重绘干扰）
        if animate and old_theme != theme_name:
            old_bg    = old_cfg['bg']
            old_frame = old_cfg['frame_bg']
            self.anim.fade_bg(self.root, old_bg,    bg,       steps=22, interval=14)
            for frame in self.card_frames:
                self.anim.fade_bg(frame,  old_frame, frame_bg, steps=22, interval=14)
        else:
            self.root.configure(fg_color=bg)
            for frame in self.card_frames:
                frame.configure(fg_color=frame_bg)

        btn_hover_secondary = _adjust_color(frame_bg, -25)   # 比卡片背景明显暗一档
        for btn in self.primary_buttons:
            btn.configure(fg_color=btn_primary, text_color='#ffffff', hover_color=btn_hover)
        for btn in self.secondary_buttons:
            btn.configure(fg_color='transparent', text_color=text_color,
                          border_color=border_color, hover_color=btn_hover_secondary)
        for lbl in self.labels:
            lbl.configure(text_color=text_color)

        self.progress_bar.configure(progress_color=btn_primary)
        self.keep_rb.configure(fg_color=btn_primary, text_color=text_color)
        self.custom_rb.configure(fg_color=btn_primary, text_color=text_color)

        # 下拉菜单完整主题适配（含弹出层颜色）
        dropdown_bg    = _adjust_color(bg, -8)        # 弹窗背景比主背景略深
        dropdown_hover = _adjust_color(btn_primary, 20)  # 悬停选中色偏亮
        for combo in (self.format_combo, self.theme_combo):
            combo.configure(
                fg_color=bg,
                button_color=btn_primary,
                button_hover_color=btn_hover,
                text_color=text_color,
                dropdown_fg_color=dropdown_bg,
                dropdown_hover_color=dropdown_hover,
                dropdown_text_color=text_color,
            )

        self._bind_card_hover(frame_bg)

        if not self._is_breathing:
            glow_color = _adjust_color(btn_primary, 30)
            self.anim.start_pulse(self.convert_btn, btn_primary, glow_color, period_ms=2000)

    def _bind_card_hover(self, frame_bg):
        """为左侧卡片绑定悬停浮起效果。
        只在首次调用时绑定事件，此后仅更新颜色读取函数就当可。
        """
        if not hasattr(self, '_hover_bound_cards'):
            self._hover_bound_cards = set()

        for frame in self.card_frames[:-1]:
            if id(frame) not in self._hover_bound_cards:
                # 当前主题颜色读取函数（闭包动态读取，不固化）
                def make_getter(f=frame):
                    def _getter():
                        c = THEMES[self._current_theme]
                        base  = c['frame_bg']
                        hover = _adjust_color(c['frame_bg'], -14)
                        return base, hover
                    return _getter

                enter_cb, leave_cb = self.anim.hover_float(frame, make_getter(frame))
                frame.bind('<Enter>', enter_cb)
                frame.bind('<Leave>', leave_cb)
                self._hover_bound_cards.add(id(frame))

    def _adjust_color(self, hex_color, amount=10):
        return _adjust_color(hex_color, amount)

    # ─────────────────────────────────────────────
    #  UI 状态切换
    # ─────────────────────────────────────────────
    def toggle_ui_state(self, disabled=False):
        state = 'disabled' if disabled else 'normal'
        self.input_entry.configure(state=state)
        self.browse_input_btn.configure(state=state)
        self.format_combo.configure(state=state)
        self.output_entry.configure(state=state)
        self.browse_out_btn.configure(state=state)
        self.keep_rb.configure(state=state)
        self.custom_rb.configure(state=state)
        self.convert_btn.configure(state=state)

        if disabled:
            self.custom_filename_entry.configure(state='disabled')
        else:
            if self.filename_mode_var.get() == "custom":
                self.custom_filename_entry.configure(state='normal')
            else:
                self.custom_filename_entry.configure(state='disabled')

    # ─────────────────────────────────────────────
    #  文件处理
    # ─────────────────────────────────────────────
    def browse_input(self):
        filenames = filedialog.askopenfilenames(title="选择要转换的文件")
        if filenames:
            self.handle_input_files(list(filenames))

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        valid_files = [f for f in files if os.path.isfile(f)]
        if valid_files:
            self.handle_input_files(valid_files)

    def handle_input_files(self, filepaths):
        exts = set()
        for fp in filepaths:
            _, fname = os.path.split(fp)
            clean = re.sub(r'@[^.]+', '', fname)
            _, ext = os.path.splitext(clean)
            exts.add(ext.lower())

        self.current_input_files = filepaths
        if len(filepaths) == 1:
            self.input_path_var.set(filepaths[0])
        else:
            self.input_path_var.set(f"已选择 {len(filepaths)} 个文件")

        self.update_formats_and_output(filepaths[0], is_batch=(len(filepaths) > 1))

        if not self.mascot_mgr.is_doing:
            self.mascot_mgr.show_start()

        # 拖入/选择闪光反馈
        cfg = THEMES[self._current_theme]
        if cfg["mode"] == "dark":
            base = "gray17"
            flash_c = "#2a6db5"
        else:
            base = cfg["frame_bg"]
            flash_c = _adjust_color(cfg["btn_primary"], 30)
        self.anim.flash_widget(self.drop_area, flash_c, base, flashes=2, duration=100)

    def on_input_change(self, event=None):
        filepath = self.input_path_var.get()
        if os.path.isfile(filepath):
            self.current_input_files = [filepath]
            self.update_formats_and_output(filepath, is_batch=False)

    def browse_output(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path_var.set(directory)

    def on_filename_mode_change(self):
        if self.filename_mode_var.get() == "custom":
            self.custom_filename_entry.configure(state='normal')
            if not self.custom_filename_var.get():
                filepath = self.input_path_var.get()
                if filepath:
                    _, filename = os.path.split(filepath)
                    clean_name = re.sub(r'@[^.]+', '', filename)
                    name, _ = os.path.splitext(clean_name)
                    self.custom_filename_var.set(name)
        else:
            self.custom_filename_var.set("")
            self.custom_filename_entry.configure(state='disabled')

    def update_formats_and_output(self, filepath, is_batch=False):
        _, filename = os.path.split(filepath)
        clean_name = re.sub(r'@[^.]+', '', filename)
        _, ext = os.path.splitext(clean_name)
        ext = ext.lower()

        allowed_formats = CONVERSION_MAP.get(ext, [])
        if allowed_formats:
            self.format_combo.configure(values=allowed_formats)
            self.target_format_var.set(allowed_formats[0])
            # 打字机状态提示
            self.anim.typewriter(self.status_var, f"就绪：识别到文件 ({ext})，可开始转换", delay_ms=20)
            self.status_label.configure(text_color="#81C784" if self._current_theme != "午夜黑" else "#66BB6A")
        else:
            self.format_combo.configure(values=["暂不支持该格式"])
            self.target_format_var.set("暂不支持该格式")
            self.anim.typewriter(self.status_var, "警告：不支持的文件格式", delay_ms=30)
            self.status_label.configure(text_color="#E57373")

        if not self.output_path_var.get():
            self.output_path_var.set(os.path.dirname(filepath))

        name, _ = os.path.splitext(clean_name)
        if is_batch:
            self.filename_mode_var.set("keep")
            self.custom_rb.configure(state='disabled')
            self.custom_filename_entry.configure(state='disabled')
            self.custom_filename_var.set("批量转换已锁定为原名")
        else:
            self.custom_rb.configure(state='normal')
            if self.filename_mode_var.get() == "custom":
                self.custom_filename_entry.configure(state='normal')
            else:
                self.custom_filename_entry.configure(state='disabled')
            self.custom_filename_var.set(name)

    # ─────────────────────────────────────────────
    #  旧版呼吸灯（转换中状态标签用）
    # ─────────────────────────────────────────────
    def start_breathing(self):
        self._is_breathing = True
        # 停止按钮呼吸
        self.anim.cancel('pulse')
        self._breath_state = 0
        self._breath_loop()

    def _breath_loop(self):
        if not self._is_breathing:
            return
        theme = self._current_theme
        if theme == "午夜黑":
            c1, c2 = "#1f538d", "gray90"
        else:
            c1, c2 = THEMES[theme]["btn_primary"], THEMES[theme]["text"]

        if self._breath_state == 0:
            self.status_label.configure(text_color=c1)
            self._breath_state = 1
        else:
            self.status_label.configure(text_color=c2)
            self._breath_state = 0

        self._breathe_id = self.root.after(800, self._breath_loop)

    def stop_breathing(self):
        self._is_breathing = False
        if hasattr(self, '_breathe_id'):
            self.root.after_cancel(self._breathe_id)

        theme = self._current_theme
        cfg   = THEMES[theme]
        self.status_label.configure(text_color=cfg['text'])

        btn_primary = cfg['btn_primary']
        glow_color  = _adjust_color(btn_primary, 30)
        self.anim.start_pulse(self.convert_btn, btn_primary, glow_color, period_ms=2000)

    # ─────────────────────────────────────────────
    #  转换流程
    # ─────────────────────────────────────────────
    def start_conversion(self):
        if not hasattr(self, 'current_input_files') or not self.current_input_files:
            manual_file = self.input_path_var.get()
            if os.path.isfile(manual_file):
                self.current_input_files = [manual_file]
            else:
                self.anim.typewriter(self.status_var, "错误：请选择有效的输入文件！", delay_ms=18)
                self.status_label.configure(text_color="#E57373")
                return

        output_dir = self.output_path_var.get()
        target_ext = self.target_format_var.get()

        if not os.path.isdir(output_dir):
            self.anim.typewriter(self.status_var, "错误：请选择有效的输出目录！", delay_ms=18)
            self.status_label.configure(text_color="#E57373")
            return

        if target_ext in ("暂不支持该格式", "请先选择源文件", ""):
            self.anim.typewriter(self.status_var, "错误：无效的目标格式！", delay_ms=18)
            self.status_label.configure(text_color="#E57373")
            return

        self.toggle_ui_state(disabled=True)
        self.open_folder_btn.pack_forget()
        self.convert_btn.configure(text="转 换 中 ...")
        self.anim.typewriter(self.status_var, "正在转换中，请稍候...", delay_ms=22)

        self.start_breathing()
        self.mascot_mgr.start_doing()

        total_files = len(self.current_input_files)
        if total_files == 1:
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start()
        else:
            self.progress_bar.configure(mode='determinate')
            self.progress_bar.set(0)

        custom_name = self.custom_filename_var.get().strip()
        use_custom = (self.filename_mode_var.get() == "custom" and custom_name)

        thread = threading.Thread(
            target=self._process_conversion_thread,
            args=(self.current_input_files, output_dir, target_ext, custom_name, use_custom)
        )
        thread.daemon = True
        thread.start()

    def _process_conversion_thread(self, input_files, output_dir, target_ext, custom_name, use_custom):
        success_count = 0
        total = len(input_files)
        errors = []
        last_output = None

        if total > 1:
            use_custom = False

        image_exts = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.ico', '.avif']
        audio_video_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.mp4', '.mkv', '.avi', '.mov',
                            '.mflac', '.mflac0', '.mgg', '.mgg0', '.mggl', '.mgg1',
                            '.qmcflac', '.qmcogg', '.qmc0', '.qmc2', '.qmc3', '.qmc4', '.qmc6', '.qmc8']
        doc_exts = ['.pptx', '.ppt', '.docx', '.doc', '.pdf', '.md', '.markdown']

        for idx, input_file in enumerate(input_files):
            if total > 1:
                pct = idx / total
                self.root.after(0, self.update_batch_progress, f"正在转换 ({idx+1}/{total}) - {int(pct*100)}%", pct)

            _, filename = os.path.split(input_file)
            clean_name = re.sub(r'@[^.]+', '', filename)
            orig_name, _ = os.path.splitext(clean_name)
            _, in_ext = os.path.splitext(clean_name)
            in_ext = in_ext.lower()

            name_to_use = custom_name if use_custom else orig_name
            expected_output = os.path.join(output_dir, f"{name_to_use}{target_ext}")
            final_output = get_unique_filename(expected_output)

            if in_ext in image_exts:
                success, error_msg = convert_image(input_file, final_output)
            elif in_ext in audio_video_exts:
                success, error_msg = convert_audio_video(input_file, final_output)
            elif in_ext in doc_exts:
                success, error_msg = convert_document(input_file, final_output)
            else:
                success = False
                error_msg = "未找到对应的转换引擎。"

            if success:
                success_count += 1
                last_output = final_output
            else:
                errors.append(f"{filename}: {error_msg}")

        if total > 1:
            self.root.after(0, self.update_batch_progress, "转换收尾中...", 1.0)
            import time
            time.sleep(0.3)

        self.root.after(0, self._on_conversion_complete, success_count, total, last_output, errors)

    def update_batch_progress(self, msg, val):
        self.status_var.set(msg)
        self.progress_bar.set(val)

    def _on_conversion_complete(self, success_count, total, last_output, errors):
        self.stop_breathing()
        self.toggle_ui_state(disabled=False)
        self.convert_btn.configure(text="再 次 转 换")

        if success_count > 0:
            self.mascot_mgr.show_down()
        else:
            self.mascot_mgr.show_start()

        if total == 1:
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')

        self.progress_bar.set(1.0)
        self.last_output_file = last_output

        if success_count > 0:
            if errors:
                self.anim.typewriter(self.status_var, f"部分完成: 成功 {success_count}/{total}。有错误产生。", delay_ms=18)
                self.status_label.configure(text_color="#FFB74D")
                error_details = "\n".join(errors)
                messagebox.showwarning("部分文件转换失败", f"部分文件转换失败，以下是详细错误日志：\n\n{error_details}")
            else:
                self.anim.typewriter(self.status_var, "mika已经全部吃完啦！", delay_ms=35)
                self.status_label.configure(text_color="#81C784" if self._current_theme != "午夜黑" else "#66BB6A")
            self.open_folder_btn.pack(side=tk.TOP, pady=10)
        else:
            self.progress_bar.set(0)
            self.anim.typewriter(self.status_var, "所有文件转换失败，请查看弹窗日志。", delay_ms=18)
            self.status_label.configure(text_color="#E57373")
            error_details = "\n".join(errors) if errors else '未知错误'
            messagebox.showerror("转换失败", f"转换失败，详细错误堆栈如下：\n\n{error_details}")

    def open_output_folder(self):
        if hasattr(self, 'last_output_file') and self.last_output_file and os.path.exists(self.last_output_file):
            path = os.path.normpath(self.last_output_file)
            if os.path.isdir(path):
                os.startfile(path)
            else:
                import subprocess
                subprocess.Popen(f'explorer /select,"{path}"')
        else:
            out_dir = self.output_path_var.get()
            if out_dir and os.path.exists(out_dir):
                os.startfile(out_dir)


# ─────────────────────────────────────────────
#  入口
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import ctypes
    try:
        myappid = 'mikaroll.converter.desktop.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    root = CTk_DnD()

    icon_path = get_resource_path("image/icon.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Icon load error: {e}")

    app = UniversalConverterApp(root)
    root.mainloop()
