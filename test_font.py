from xhtml2pdf import pisa
import io

html1 = '''<html>
<style>
@font-face {
    font-family: 'test1';
    src: url('file:///C:/Windows/Fonts/simhei.ttf');
}
body { font-family: 'test1'; }
</style>
<body>测试 file scheme</body>
</html>'''

html2 = '''<html>
<style>
@font-face {
    font-family: 'test2';
    src: url('C:/Windows/Fonts/simhei.ttf');
}
body { font-family: 'test2'; }
</style>
<body>测试 pure path</body>
</html>'''

out1 = io.BytesIO()
pisa.CreatePDF(io.StringIO(html1), dest=out1)
open('test1.pdf', 'wb').write(out1.getvalue())

out2 = io.BytesIO()
pisa.CreatePDF(io.StringIO(html2), dest=out2)
open('test2.pdf', 'wb').write(out2.getvalue())
