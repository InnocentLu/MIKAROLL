import os
import sys

with open("engines/doc_engine.py", "r", encoding="utf-8") as f:
    content = f.read()

import tempfile

def replace_block(content, start_str, end_str, new_code):
    start_idx = content.find(start_str)
    if start_idx == -1:
        print(f"Start str not found:\n{start_str}")
        sys.exit(1)
    end_idx = content.find(end_str, start_idx)
    if end_idx == -1:
        print(f"End str not found:\n{end_str}")
        sys.exit(1)
    end_idx += len(end_str)
    return content[:start_idx] + new_code + content[end_idx:]

ppt_orig = """        # 1. PPT/PPTX processing
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
                powerpoint.Quit()"""

ppt_new = """        # 1. PPT/PPTX processing
        if in_ext in ['.ppt', '.pptx']:
            if os.name == 'nt':
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
            else:
                import subprocess, tempfile, shutil
                import sys
                soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice" if sys.platform == 'darwin' else "soffice"
                if not os.path.exists(soffice_path) and not shutil.which("soffice"):
                     raise Exception("LibreOffice not found. Please install LibreOffice for Mac.")
                if not os.path.exists(soffice_path): soffice_path = "soffice"
                
                temp_dir = tempfile.mkdtemp()
                cmd = [soffice_path, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode != 0:
                     shutil.rmtree(temp_dir, ignore_errors=True)
                     raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                temp_pdf = os.path.join(temp_dir, base_name + ".pdf")
                
                if out_ext == '.pdf':
                     shutil.move(temp_pdf, output_path)
                elif out_ext in ['.png', '.jpg']:
                     import fitz
                     doc = fitz.open(temp_pdf)
                     base, ext = os.path.splitext(output_path)
                     for page_num in range(len(doc)):
                         page = doc.load_page(page_num)
                         pix = page.get_pixmap(dpi=300)
                         out_name = f"{base}_page{page_num+1}{ext}"
                         pix.save(out_name)
                     doc.close()
                elif out_ext == '.docx':
                     from pdf2docx import Converter
                     cv = Converter(temp_pdf)
                     cv.convert(output_path)
                     cv.close()
                shutil.rmtree(temp_dir, ignore_errors=True)"""

content = replace_block(content, ppt_orig, "powerpoint.Quit()", ppt_new)

doc_orig = """        # 2. Word processing (.doc / .docx)
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
                word.Quit()"""

doc_new = """        # 2. Word processing (.doc / .docx)
        elif in_ext in ['.doc', '.docx']:
            if os.name == 'nt':
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
            else:
                import subprocess, tempfile, shutil
                import sys
                soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice" if sys.platform == 'darwin' else "soffice"
                if not os.path.exists(soffice_path) and not shutil.which("soffice"):
                     raise Exception("LibreOffice not found. Please install LibreOffice for Mac.")
                if not os.path.exists(soffice_path): soffice_path = "soffice"
                
                temp_dir = tempfile.mkdtemp()
                
                if out_ext == '.pdf':
                     cmd = [soffice_path, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path]
                     res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     if res.returncode != 0:
                          shutil.rmtree(temp_dir, ignore_errors=True)
                          raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                     base_name = os.path.splitext(os.path.basename(input_path))[0]
                     shutil.move(os.path.join(temp_dir, base_name + ".pdf"), output_path)
                elif out_ext in ['.txt', '.md']:
                     cmd = [soffice_path, "--headless", "--convert-to", "txt:Text (encoded):UTF8", "--outdir", temp_dir, input_path]
                     res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     if res.returncode != 0:
                          shutil.rmtree(temp_dir, ignore_errors=True)
                          raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                     base_name = os.path.splitext(os.path.basename(input_path))[0]
                     shutil.move(os.path.join(temp_dir, base_name + ".txt"), output_path)
                
                shutil.rmtree(temp_dir, ignore_errors=True)"""

content = replace_block(content, doc_orig, "word.Quit()", doc_new)


md_orig = """            elif out_ext == '.docx':
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
                            pass"""

md_new = """            elif out_ext == '.docx':
                temp_html = input_path + ".temp.html"
                html_wrapper = _get_md_html_wrapper(text)
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_wrapper)
                
                if os.name == 'nt':
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
                else:
                    import subprocess, tempfile, shutil
                    import sys
                    soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice" if sys.platform == 'darwin' else "soffice"
                    if not os.path.exists(soffice_path) and not shutil.which("soffice"):
                         raise Exception("LibreOffice not found. Please install LibreOffice for Mac.")
                    if not os.path.exists(soffice_path): soffice_path = "soffice"
                    
                    temp_dir = tempfile.mkdtemp()
                    cmd = [soffice_path, "--headless", "--convert-to", "docx", "--outdir", temp_dir, os.path.abspath(temp_html)]
                    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if res.returncode != 0:
                         shutil.rmtree(temp_dir, ignore_errors=True)
                         raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                    
                    base_name = os.path.splitext(os.path.basename(temp_html))[0]
                    shutil.move(os.path.join(temp_dir, base_name + ".docx"), output_path)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if os.path.exists(temp_html):
                        try:
                            os.remove(temp_html)
                        except:
                            pass"""

content = replace_block(content, md_orig, "pass", md_new)


with open("engines/doc_engine.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patching complete!")
