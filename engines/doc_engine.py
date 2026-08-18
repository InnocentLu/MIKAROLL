import os

def _get_md_html_wrapper(text):
    import markdown
    try:
        from pygments.formatters import HtmlFormatter
        has_pygments = True
    except ImportError:
        has_pygments = False

    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite', 'md_in_html'])
    
    pygments_css = ""
    if has_pygments:
        formatter = HtmlFormatter(style='default', cssclass='codehilite')
        pygments_css = formatter.get_style_defs()

    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script>
        MathJax = {{
          tex: {{
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
            processEscapes: true,
            processEnvironments: true
          }},
          options: {{
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
          }}
        }};
    </script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {{
            font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "STHeiti", "Arial", sans-serif;
            line-height: 1.6;
            margin: 40px;
        }}
        {pygments_css}
        pre, code {{
            font-family: "Menlo", "Monaco", "Courier New", monospace;
            white-space: pre-wrap;
        }}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
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

def _mac_convert_via_applescript(in_ext, out_ext, input_path, output_path):
    import subprocess
    import time
    script = ""
    app_name = ""
    app_id = ""
    
    if in_ext in ['.ppt', '.pptx', '.key']:
        app_name = "Keynote"
        app_id = "com.apple.Keynote"
        if out_ext == '.pdf':
            action = f'export document 1 to POSIX file "{output_path}" as PDF'
        elif out_ext == '.pptx':
            action = f'export document 1 to POSIX file "{output_path}" as PowerPoint'
        elif out_ext == '.key':
            action = f'save document 1 in POSIX file "{output_path}"'
        else:
            action = f'export document 1 to POSIX file "{output_path}" as PDF'
            
        script = f"""
        set inFile to POSIX file "{input_path}"
        tell application id "{app_id}"
            launch
            delay 1
            open inFile
            {action}
            close document 1 saving no
        end tell
        """
        
    elif in_ext in ['.doc', '.docx', '.pages']:
        app_name = "Pages"
        app_id = "com.apple.iWork.Pages"
        if out_ext == '.pdf':
            action = "export myDoc to outFile as PDF"
        elif out_ext == '.docx':
            action = "export myDoc to outFile as Word"
        elif out_ext == '.pages':
            action = "save myDoc in outFile"
        elif out_ext in ['.txt', '.md']:
            action = "export myDoc to outFile as unformatted text"
        else:
            action = "export myDoc to outFile as PDF"
            
        script = f"""
        set inFile to POSIX file "{input_path}"
        set outFile to POSIX file "{output_path}"
        tell application id "{app_id}"
            launch
            delay 1
            set myDoc to open inFile
            {action}
            close myDoc saving no
        end tell
        """
        
    elif in_ext in ['.xls', '.xlsx', '.numbers']:
        app_name = "Numbers"
        app_id = "com.apple.iWork.Numbers"
        if out_ext == '.pdf':
            action = "export myDoc to outFile as PDF"
        elif out_ext in ['.xls', '.xlsx']:
            action = "export myDoc to outFile as Excel"
        elif out_ext == '.csv':
            action = "export myDoc to outFile as CSV"
        elif out_ext == '.numbers':
            action = "save myDoc in outFile"
        else:
            action = "export myDoc to outFile as PDF"
            
        script = f"""
        set inFile to POSIX file "{input_path}"
        set outFile to POSIX file "{output_path}"
        tell application id "{app_id}"
            launch
            delay 1
            set myDoc to open inFile
            {action}
            close myDoc saving no
        end tell
        """
    else:
        raise Exception(f"Unsupported format for Mac native conversion: {in_ext}")

    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0:
        err = res.stderr.strip()
        if "-609" in err or "-1743" in err:
            raise Exception(f"{app_name} 自动化权限未开启或连接失败 ({err})。\\n请前往 macOS「系统设置 -> 隐私与安全性 -> 自动化」，允许当前终端/应用控制 {app_name}。")
        raise Exception(f"{app_name} conversion failed. Error: {err}")
        
    # Preview the file if it's a PDF
    if out_ext == '.pdf':
        subprocess.run(["open", output_path])

def convert_document(input_path, output_path):
    try:
        in_ext = os.path.splitext(input_path)[1].lower()
        out_ext = os.path.splitext(output_path)[1].lower()
        
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        
        # 1. PPT/PPTX/Keynote processing
        if in_ext in ['.ppt', '.pptx', '.key']:
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
                temp_dir = tempfile.mkdtemp()
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                temp_pdf = os.path.join(temp_dir, base_name + ".pdf")
                
                try:
                    if sys.platform == 'darwin':
                        if out_ext in ['.pdf', '.key', '.pptx']:
                             _mac_convert_via_applescript(in_ext, out_ext, input_path, output_path)
                             shutil.rmtree(temp_dir, ignore_errors=True)
                             return True, None
                        _mac_convert_via_applescript(in_ext, '.pdf', input_path, temp_pdf)
                    else:
                        soffice_path = "soffice"
                        if not shutil.which("soffice"):
                             raise Exception("LibreOffice not found.")
                        cmd = [soffice_path, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path]
                        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if res.returncode != 0:
                             raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                except Exception as e:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    raise e
                
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
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        # 2. Word/Pages processing (.doc / .docx / .pages)
        elif in_ext in ['.doc', '.docx', '.pages']:
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
                temp_dir = tempfile.mkdtemp()
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                
                try:
                    if sys.platform == 'darwin':
                        if out_ext in ['.pdf', '.pages', '.docx', '.txt', '.md']:
                             _mac_convert_via_applescript(in_ext, out_ext, input_path, output_path)
                             shutil.rmtree(temp_dir, ignore_errors=True)
                             return True, None
                    else:
                        soffice_path = "soffice"
                        if not shutil.which("soffice"):
                             raise Exception("LibreOffice not found.")
                        if out_ext == '.pdf':
                             cmd = [soffice_path, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path]
                             res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                             if res.returncode != 0:
                                  raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                             shutil.move(os.path.join(temp_dir, base_name + ".pdf"), output_path)
                        elif out_ext in ['.txt', '.md']:
                             cmd = [soffice_path, "--headless", "--convert-to", "txt:Text (encoded):UTF8", "--outdir", temp_dir, input_path]
                             res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                             if res.returncode != 0:
                                  raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                             shutil.move(os.path.join(temp_dir, base_name + ".txt"), output_path)
                except Exception as e:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    raise e
                
                shutil.rmtree(temp_dir, ignore_errors=True)
                        
        # 2.5 Excel/Numbers processing (.numbers)
        elif in_ext in ['.xls', '.xlsx', '.numbers']:
            import subprocess, tempfile, shutil
            import sys
            temp_dir = tempfile.mkdtemp()
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            if out_ext == '.pdf':
                fmt = "pdf"
            elif out_ext == '.xlsx':
                fmt = "xlsx"
            elif out_ext == '.csv':
                fmt = "csv"
            else:
                fmt = out_ext.lstrip('.')
                
            try:
                if sys.platform == 'darwin':
                    if out_ext in ['.pdf', '.numbers', '.xlsx', '.csv', '.xls']:
                         _mac_convert_via_applescript(in_ext, out_ext, input_path, output_path)
                         shutil.rmtree(temp_dir, ignore_errors=True)
                         return True, None
                else:
                    soffice_path = "soffice"
                    if not shutil.which("soffice"):
                         raise Exception("LibreOffice not found.")
                    cmd = [soffice_path, "--headless", "--convert-to", fmt, "--outdir", temp_dir, input_path]
                    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if res.returncode != 0:
                         raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                    shutil.move(os.path.join(temp_dir, f"{base_name}.{fmt}"), output_path)
            except Exception as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise e
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
                        
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
                # Ensure literal representation of potential escapes to avoid python escape issues
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
                
                import sys
                if getattr(sys, 'frozen', False):
                    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(sys._MEIPASS, "ms-playwright")
                    
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.set_content(html_wrapper)
                    # 等待 MathJax 等异步渲染完成
                    page.wait_for_load_state("networkidle")
                    page.pdf(path=output_path, format="A4", margin={"top": "20px", "right": "20px", "bottom": "20px", "left": "20px"}, print_background=True)
                    browser.close()
                import subprocess
                subprocess.run(["open", output_path])
            elif out_ext == '.docx':
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
                    temp_dir = tempfile.mkdtemp()
                    base_name = os.path.splitext(os.path.basename(temp_html))[0]
                    
                    try:
                        if sys.platform == 'darwin':
                            # HTML to DOCX natively using Word
                            temp_out = os.path.join(temp_dir, base_name + ".docx")
                            script = f"""
                            set inFile to POSIX file "{os.path.abspath(temp_html)}"
                            set outFile to POSIX file "{temp_out}"
                            tell application "Microsoft Word"
                                set myDoc to open inFile
                                save as myDoc file name (outFile as string) file format format document
                                close myDoc saving no
                            end tell
                            """
                            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                            if res.returncode != 0:
                                raise Exception(f"Microsoft Word conversion failed. Please ensure Word is installed. Error: {res.stderr.strip()}")
                            shutil.move(temp_out, output_path)
                        else:
                            soffice_path = "soffice"
                            if not shutil.which("soffice"):
                                 raise Exception("LibreOffice not found.")
                            cmd = [soffice_path, "--headless", "--convert-to", "docx", "--outdir", temp_dir, os.path.abspath(temp_html)]
                            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            if res.returncode != 0:
                                 raise Exception(f"LibreOffice error: {res.stderr.decode('utf-8', errors='ignore')}")
                            shutil.move(os.path.join(temp_dir, base_name + ".docx"), output_path)
                    except Exception as e:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        raise e
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)
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
