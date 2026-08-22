"""utils/pdf_stamper.py - 使用 ReportLab 在 PDF 每页绝对居中添加页码"""
import os


def stamp_page_numbers(input_pdf: str, output_pdf: str, stop_event=None) -> bool:
    """
    在 input_pdf 的每一页底部添加居中页码，写入 output_pdf。
    使用 ReportLab drawCentredString 确保 X 轴数学绝对居中。

    Returns:
        True on success, False on failure or cancellation.
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.lib.pagesizes import A4
        import io

        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            from PyPDF2 import PdfReader, PdfWriter

        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            if stop_event and stop_event.is_set():
                return False

            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # Create an overlay with the page number
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0.4, 0.4, 0.4)

            # drawCentredString centers the text string at the given X coordinate
            label = f"- {i + 1} -"
            c.drawCentredString(page_width / 2.0, 15 * mm, label)
            c.save()

            packet.seek(0)
            overlay_reader = PdfReader(packet)
            overlay_page = overlay_reader.pages[0]

            page.merge_page(overlay_page)
            writer.add_page(page)

        with open(output_pdf, 'wb') as f:
            writer.write(f)

        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
