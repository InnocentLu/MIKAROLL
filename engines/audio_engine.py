import os
import subprocess
import tempfile
import sys
import shutil
import traceback

try:
    # Add engines to sys.path if not there
    engines_dir = os.path.dirname(os.path.abspath(__file__))
    if engines_dir not in sys.path:
        sys.path.insert(0, engines_dir)
    from qmc_decrypt import decrypt_qmc_file
    HAS_QMC_DECRYPT = True
except ImportError:
    HAS_QMC_DECRYPT = False

def sniff_ext(data):
    if data.startswith(b'fLaC'): return 'flac'
    if data.startswith(b'OggS'): return 'ogg'
    if data.startswith(b'ID3') or data.startswith(b'\xff\xfb') or data.startswith(b'\xff\xf2') or data.startswith(b'\xff\xf3'): return 'mp3'
    if data.startswith(b'\x00\x00\x00 ftypM4A') or data.startswith(b'\x00\x00\x00\x18ftypM4A'): return 'm4a'
    if data.startswith(b'\x00\x00\x00 ftypdash'): return 'm4a' # typical qq music m4a
    return 'flac' # fallback

def convert_audio_video(input_path, output_path):
    """
    Converts audio and extracts audio from video using FFmpeg.
    Intercepts and decrypts QQ Music encrypted files first.
    """
    temp_file_path = None
    
    # 清理路径可能带有的多余引号，并转为绝对路径以防万一
    input_path = os.path.abspath(str(input_path).strip('"\''))
    output_path = os.path.abspath(str(output_path).strip('"\''))
    
    # 前置检查 FFmpeg 环境
    ffmpeg_cmd = "ffmpeg"
    local_ffmpeg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin', 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    if os.path.exists(local_ffmpeg):
        ffmpeg_cmd = local_ffmpeg
    elif not shutil.which("ffmpeg"):
        return False, "系统未安装 FFmpeg，请先安装配置，或将其放置在 bin 目录下。"

    if not os.path.exists(input_path):
        return False, f"找不到输入文件: {input_path}"

    try:
        _, out_target_ext = os.path.splitext(output_path)
        out_target_ext = out_target_ext.lower().lstrip('.')

        # Check if it's a QMC encrypted file
        _, in_ext = os.path.splitext(input_path)
        in_ext = in_ext.lower()
        if in_ext in ['.mflac', '.mflac0', '.mgg', '.mgg0', '.mggl', '.mgg1', '.qmcflac', '.qmcogg', '.qmc0', '.qmc2', '.qmc3', '.qmc4', '.qmc6', '.qmc8']:
            if not HAS_QMC_DECRYPT:
                return False, "QQ Music decryption module (qmc_decrypt.py) is missing in engines directory."
            
            with open(input_path, 'rb') as f:
                data = f.read()
                
            try:
                out_bytes, out_ext, logs = decrypt_qmc_file(data, ext_hint=in_ext[1:])
            except Exception as e:
                traceback.print_exc()
                return False, f"DRM 解密失败: {e}"
                
            # 优化：如果解密后的无损格式，恰好是用户请求的目标格式，直接输出保存，跳过 FFmpeg 转码！
            if out_ext.lower() == out_target_ext:
                with open(output_path, 'wb') as tf:
                    tf.write(out_bytes)
                return True, None

            # Create a temporary decrypted file
            temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=f'.{out_ext}')
            with os.fdopen(temp_file_fd, 'wb') as tf:
                tf.write(out_bytes)
                
            input_path = temp_file_path # Override input path for ffmpeg
            
        kwargs = {}
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = startupinfo
        
        # 使用列表传递参数，彻底杜绝空格引发的路径截断问题
        command = [ffmpeg_cmd, '-y', '-i', input_path]
        
        # Determine output format and add specific flags if needed
        ext = out_target_ext
        if ext == 'mp3':
            command.extend(['-q:a', '2'])
        elif ext == 'gif':
            # Simple gif conversion, can be optimized with palettes
            command.extend(['-vf', 'fps=10,scale=320:-1:flags=lanczos'])
            
        command.append(output_path)
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        _, stderr = process.communicate()
        
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
                
        if process.returncode != 0:
            return False, stderr.decode('utf-8', errors='ignore')
        return True, None
    except Exception as e:
        traceback.print_exc()
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        return False, f"转换过程中发生未捕获的错误: {str(e)}"
