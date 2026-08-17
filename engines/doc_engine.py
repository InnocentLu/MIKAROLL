import os

def _get_md_html_wrapper(text):
    import markdown
    try:
        from pygments.formatters import HtmlFormatter
        has_pygments = True
    except ImportError:
        has_pygments = False

    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite'])
    
    pygments_css = ""
    if has_pygments:
        formatter = HtmlFormatter(style='default', cssclass='codehilite')
        pygments_css = formatter.get_style_defs()

    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body, h1, h2, h3, p, div, span, pre, code {{
            font-family: "STSong-Light", "MSung-Light", sans-serif !important;
        }}
        body {{
            line-height: 1.6;
            margin: 40px;
        }}
        {pygments_css}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            font-family: Consolas, monospace;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    return html_wrapper

def convert_document(input_path, output_path):
    try:
        in_ext = os.path.splitext(input_path)[1].lower()
        out_ext = os.path.splitext(output_path)[1].lower()
        
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        
        # 1. PPT/PPTX processing
        if in_ext in ['.ppt', '.pptx']:
            import comtypes.client
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            try:
                presentation = powerpoint.Presentations.Open(input_path, WithWindow=False)
                if out_ext == '.pdf':
                    presentation.SaveAs(output_path, 32) # ppSaveAsPDF
                elif out_ext == '.png':
                    presentation.SaveAs(output_path, 18) # ppSaveAsPNG
                elif out_ext == '.jpg':
                    presentation.SaveAs(output_path, 17) # ppSaveAsJPG
                elif out_ext == '.docx':
                    temp_pdf = input_path + ".temp.pdf"
                    presentation.SaveAs(temp_pdf, 32)
                    presentation.Close()
                    presentation = None
                    from pdf2docx import Converter
                    cv = Converter(temp_pdf)
                    cv.convert(output_path)
                    cv.close()
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
            finally:
                if 'presentation' in locals() and presentation is not None:
                    presentation.Close()
                powerpoint.Quit()
                
        # 2. Word processing (.doc / .docx)
        elif in_ext in ['.doc', '.docx']:
            import comtypes.client
            word = comtypes.client.CreateObject('Word.Application')
            try:
                word.Visible = False
                doc = word.Documents.Open(input_path)
                if out_ext == '.pdf':
                    doc.SaveAs(output_path, FileFormat=17) # wdFormatPDF
                elif out_ext in ['.txt', '.md']:
                    doc.SaveAs(output_path, FileFormat=7, Encoding=65001) # wdFormatEncodedText UTF-8
                doc.Close()
            finally:
                word.Quit()
                        
        # 3. PDF processing
        elif in_ext == '.pdf':
            if out_ext == '.docx':
                from pdf2docx import Converter
                cv = Converter(input_path)
                cv.convert(output_path)
                cv.close()
            elif out_ext in ['.png', '.jpg']:
                import fitz
                doc = fitz.open(input_path)
                base, ext = os.path.splitext(output_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=300)
                    out_name = f"{base}_page{page_num+1}{ext}"
                    pix.save(out_name)
                doc.close()
            elif out_ext == '.txt':
                import fitz
                doc = fitz.open(input_path)
                with open(output_path, 'w', encoding='utf-8') as f:
                    for page in doc:
                        f.write(page.get_text())
                doc.close()
                
        # 4. Markdown processing
        elif in_ext in ['.md', '.markdown']:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if out_ext == '.txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
            elif out_ext == '.html':
                html_wrapper = _get_md_html_wrapper(text)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_wrapper)
            elif out_ext == '.pdf':
                html_wrapper = _get_md_html_wrapper(text)
                from xhtml2pdf import pisa
                with open(output_path, "w+b") as result_file:
                    pisa_status = pisa.CreatePDF(html_wrapper, dest=result_file)
                if pisa_status.err:
                    return False, "xhtml2pdf failed to create PDF."
            elif out_ext == '.docx':
                temp_html = input_path + ".temp.html"
                html_wrapper = _get_md_html_wrapper(text)
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_wrapper)
                
                import comtypes.client
                word = comtypes.client.CreateObject('Word.Application')
                try:
                    word.Visible = False
                    doc = word.Documents.Open(os.path.abspath(temp_html))
                    doc.SaveAs(output_path, FileFormat=16) # wdFormatDocumentDefault
                    doc.Close()
                finally:
                    word.Quit()
                    if os.path.exists(temp_html):
                        try:
                            os.remove(temp_html)
                        except:
                            pass
        
        return True, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)
