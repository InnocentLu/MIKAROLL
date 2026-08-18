from PIL import Image, ImageDraw, ImageFont
import traceback

width, height = 800, 600
bg = Image.new('RGB', (width, height), '#F5F5F7')
draw = ImageDraw.Draw(bg)

arrow_color = '#A0A0A5'
# Draw a minimalist, elegant thin arrow
# Main line
draw.line([(350, 280), (450, 280)], fill=arrow_color, width=3)
# Arrow head (slim, 45 degree angle)
draw.line([(435, 265), (450, 280)], fill=arrow_color, width=3)
draw.line([(435, 295), (450, 280)], fill=arrow_color, width=3)

font = None
paths = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf"
]
for p in paths:
    try:
        font = ImageFont.truetype(p, 28)
        print(f"Successfully loaded font: {p}")
        break
    except Exception as e:
        print(f"Failed to load {p}: {e}")

if font is None:
    font = ImageFont.load_default()
    print("WARNING: Falling back to default font. Chinese will be garbled!")

text = "感谢 sensei 带 Mika 回家 ！"
draw.text((400, 480), text, fill='#999999', font=font, anchor="mm")

bg.save('/Users/tianzhen/Documents/conversion_tool/image/dmg_arrow_bg.png', dpi=(72, 72))
print("Image saved.")
