from PIL import Image

def make_icon():
    img_path = "image/icon.jpg"
    ico_path = "image/icon.ico"
    
    # 1. 打开原始图片
    img = Image.open(img_path)
    
    # 2. 居中裁剪为正方形
    width, height = img.size
    min_dim = min(width, height)
    
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    
    img_cropped = img.crop((left, top, right, bottom))
    
    # 3. 调整并保存为包含多尺寸的高清 .ico 图标
    # sizes 参数包含了 Windows 常见的图标尺寸
    img_cropped.save(
        ico_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    print(f"成功将 {img_path} 裁剪并转换为高清图标: {ico_path}")

if __name__ == "__main__":
    make_icon()
