from fpdf import FPDF
import os
import platform

class PDFReportExporter:
    def __init__(self, title):
        self.title = title

    def _get_system_font_path(self):
        """Get the appropriate font path based on operating system"""
        system = platform.system()
        
        if system == "Windows":
            font_paths = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\Arial.ttf"
            ]
        elif system == "Darwin":  # macOS
            font_paths = [
                "/Library/Fonts/Arial Unicode.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
        else:  # Linux and others
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
        
        # Return first existing font path
        for path in font_paths:
            if os.path.exists(path):
                return path
                
        return None

    def export(self, report_data, chart_paths=None, filename="report.pdf"):
        pdf = FPDF()
        pdf.add_page()

        # Get system-appropriate font path
        font_path = self._get_system_font_path()
        
        if font_path and os.path.exists(font_path):
            try:
                # Add Unicode font and its bold version
                pdf.add_font("Unicode", "", font_path, uni=True)
                pdf.add_font("Unicode", "B", font_path, uni=True)
                pdf.set_font("Unicode", size=12)
            except Exception as e:
                print(f"Warning: Could not load font {font_path}: {e}")
                pdf.set_font("Arial", size=12)
        else:
            # Fallback to built-in Arial
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