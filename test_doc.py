import comtypes.client
import os
import markdown
from pygments.formatters import HtmlFormatter

def test_md_to_html():
    text = "# 测试标题\n\n```python\nprint('hello')\n```\n\n你好，世界！"
    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite'])
    formatter = HtmlFormatter(style='default', cssclass='codehilite')
    pygments_css = formatter.get_style_defs()
    
    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @font-face {{
            font-family: 'msyh';
            src: url('file:///C:/Windows/Fonts/simhei.ttf');
        }}
        body {{
            font-family: 'msyh', sans-serif;
        }}
        {pygments_css}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    with open("test_out.html", "w", encoding="utf-8") as f:
        f.write(html_wrapper)
    print("HTML created")

def test_xhtml2pdf():
    from xhtml2pdf import pisa
    with open("test_out.html", "r", encoding="utf-8") as f:
        source_html = f.read()
    with open("test_out.pdf", "w+b") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file)
    print("PDF created, error:", pisa_status.err)

if __name__ == "__main__":
    test_md_to_html()
    test_xhtml2pdf()
