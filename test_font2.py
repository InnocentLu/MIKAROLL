from xhtml2pdf import pisa
import io

html = '''<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
body { font-family: "STSong-Light"; }
</style>
<body>测试中文 STSong-Light</body>
</html>'''

out = io.BytesIO()
pisa.CreatePDF(io.StringIO(html), dest=out)
open('test3.pdf', 'wb').write(out.getvalue())
