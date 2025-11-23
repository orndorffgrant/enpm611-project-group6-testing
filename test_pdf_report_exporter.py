import unittest
from unittest.mock import patch, MagicMock
from pdf_report_exporter import PDFReportExporter


class TestPDFReportExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = PDFReportExporter("Test Report")

    @patch("pdf_report_exporter.platform.system")
    @patch("pdf_report_exporter.os.path.exists")
    def test_get_system_font_path_returns_existing_font(self, mock_exists, mock_system):
        # Simulate Windows with only the second font existing
        mock_system.return_value = "Windows"

        def exists_side_effect(path):
            return path.endswith("Arial.ttf")

        mock_exists.side_effect = exists_side_effect

        font_path = self.exporter._get_system_font_path()
        self.assertIsNotNone(font_path)
        self.assertTrue(font_path.endswith(".ttf"))

    @patch("pdf_report_exporter.platform.system")
    @patch("pdf_report_exporter.os.path.exists")
    def test_get_system_font_path_returns_none_when_no_fonts_found(self, mock_exists, mock_system):
        mock_system.return_value = "Linux"
        mock_exists.return_value = False

        font_path = self.exporter._get_system_font_path()
        self.assertIsNone(font_path)

    @patch("pdf_report_exporter.FPDF")
    @patch.object(PDFReportExporter, "_get_system_font_path")
    @patch("pdf_report_exporter.os.path.exists")
    def test_export_with_unicode_font_and_charts(
        self, mock_exists, mock_get_font_path, mock_fpdf
    ):
        """
        Happy path: system font is found, Unicode fonts are added,
        report_data is written, and chart images are inserted.
        """
        mock_get_font_path.return_value = "/fake/font.ttf"

        def exists_side_effect(path):
            if path == "/fake/font.ttf":
                return True
            if path == "chart1.png":
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        mock_pdf = MagicMock()
        mock_fpdf.return_value = mock_pdf

        report_data = {"Section 1": "Content"}
        chart_paths = ["chart1.png"]

        self.exporter.export(report_data, chart_paths=chart_paths, filename="out.pdf")

        mock_pdf.add_page.assert_called()
        mock_pdf.add_font.assert_any_call("Unicode", "", "/fake/font.ttf", uni=True)
        mock_pdf.add_font.assert_any_call("Unicode", "B", "/fake/font.ttf", uni=True)
        mock_pdf.set_font.assert_any_call("Unicode", size=12)
        mock_pdf.image.assert_called_with("chart1.png", x=10, y=None, w=180)
        mock_pdf.output.assert_called_with("out.pdf")

    def test_export_without_unicode_font_is_buggy(self):
        """
        BUG: When no system font is available, exporter falls back to Arial,
        but still tries to use the 'Unicode' font name later, which FPDF
        doesn't know about. This causes a runtime exception.
        """
        report_data = {"Section": "Content"}

        # Force the exporter into the fallback branch (no system font path)
        with patch.object(PDFReportExporter, "_get_system_font_path", return_value=None):
            # We EXPECT this not to crash and simply use built-in fonts,
            # but the current implementation will raise an FPDFException
            # when calling pdf.set_font("Unicode", ...).
            self.exporter.export(report_data, chart_paths=None, filename="no_font_report.pdf")


if __name__ == "__main__":
    unittest.main()
