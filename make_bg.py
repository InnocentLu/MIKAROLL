from PIL import Image, ImageDraw, ImageFont

width, height = 800, 600
bg = Image.new('RGB', (width, height), '#F5F5F7')
draw = ImageDraw.Draw(bg)

start_x, end_x = 340, 460
y = 280

draw.line([(start_x, y), (end_x, y)], fill='#8B4567', width=6)

arrow_size = 18
draw.line([(end_x - arrow_size, y - arrow_size), (end_x, y)], fill='#8B4567', width=6)
draw.line([(end_x - arrow_size, y + arrow_size), (end_x, y)], fill='#8B4567', width=6)

try:
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 26)
    font_sub = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 18)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

text1 = "向右拖拽完成安装"
text2 = "感谢 sensei 带 Mika 回家 ♡"

draw.text((400, 390), text1, fill='#555555', font=font_title, anchor="mm")
draw.text((400, 440), text2, fill='#D4547A', font=font_sub, anchor="mm")

# Save properly at 72 dpi
bg.save('/Users/tianzhen/Documents/conversion_tool/image/dmg_arrow_bg.png', dpi=(72, 72))
print("Background generated successfully.")
