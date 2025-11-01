from fpdf import FPDF
import os

class PDFReportExporter:
    def __init__(self, title):
        self.title = title

    def export(self, report_data, chart_paths=None, filename="report.pdf"):
        pdf = FPDF()
        pdf.add_page()

        # ✅ Add Unicode font if available
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(font_path):
            font_path = "/Library/Fonts/Arial Unicode.ttf"
        if os.path.exists(font_path):
            # Add Unicode font and its bold version
            pdf.add_font("Unicode", "", font_path, uni=True)
            pdf.add_font("Unicode", "B", font_path, uni=True)
            pdf.set_font("Unicode", size=12)
        else:
            pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, txt=self.title, ln=True, align="C")
        pdf.ln(10)

        for section, content in report_data.items():
            pdf.set_font("Unicode", "B", 12)
            pdf.cell(0, 10, txt=f"• {section}", ln=True)
            pdf.set_font("Unicode", "", 10)
            pdf.multi_cell(0, 8, str(content))
            pdf.ln(5)

        if chart_paths:
            for path in chart_paths:
                if os.path.exists(path):
                    pdf.add_page()
                    pdf.image(path, x=10, y=None, w=180)
                    pdf.ln(10)

        pdf.output(filename)
        print(f"✅ PDF exported to {filename}")
