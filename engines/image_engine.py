import os
from PIL import Image
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

try:
    import pillow_avif
except ImportError:
    pass

def convert_image(input_path, output_path):
    """
    Converts an image using Pillow.
    Handles mode conversions (like RGBA to RGB for JPEG).
    """
    try:
        with Image.open(input_path) as img:
            # Force load to catch decode errors early
            img.load()
            
            _, ext = os.path.splitext(output_path)
            ext = ext.lower()
            
            if ext in ['.jpg', '.jpeg']:
                if img.mode in ('RGBA', 'P', 'LA'):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode in ('RGBA', 'LA'):
                        bg.paste(img, mask=img.split()[-1])
                    else:
                        bg.paste(img)
                    img = bg
            
            if ext == '.ico':
                # Generate multiple icon sizes
                icon_sizes = [(16,16), (32, 32), (48, 48), (64,64), (128, 128), (256, 256)]
                img.save(output_path, sizes=icon_sizes)
            else:
                img.save(output_path)
            return True, None
    except Exception as e:
        # Fallback to FFmpeg
        try:
            from engines.audio_engine import convert_audio_video
            success, ffmpeg_err = convert_audio_video(input_path, output_path)
            if success:
                return True, None
            else:
                return False, f"Pillow 报错 ({str(e)})，且 FFmpeg 降级转换也失败 ({ffmpeg_err})"
        except ImportError:
            return False, f"Pillow 报错: {str(e)}"
