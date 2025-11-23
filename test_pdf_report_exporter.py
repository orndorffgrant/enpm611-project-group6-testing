"""
Unit tests for pdf_report_exporter.py
Tests the PDFReportExporter class with various edge cases and potential bugs.
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import platform
import tempfile
import shutil
from pdf_report_exporter import PDFReportExporter


class TestPDFReportExporter(unittest.TestCase):
    """Test cases for the PDFReportExporter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_title = "Test Report"
        self.exporter = PDFReportExporter(self.test_title)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # Clean up any test PDF files
        for filename in os.listdir('.'):
            if filename.endswith('.pdf') and 'test' in filename.lower():
                try:
                    os.remove(filename)
                except:
                    pass
    
    def test_init(self):
        """Test PDFReportExporter initialization"""
        exporter = PDFReportExporter("My Report")
        self.assertEqual(exporter.title, "My Report")
    
    def test_init_empty_title(self):
        """Test PDFReportExporter initialization with empty title"""
        exporter = PDFReportExporter("")
        self.assertEqual(exporter.title, "")
    
    def test_get_system_font_path_windows(self):
        """Test _get_system_font_path on Windows"""
        with patch('platform.system', return_value='Windows'):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path == "C:\\Windows\\Fonts\\arial.ttf"
                font_path = self.exporter._get_system_font_path()
                self.assertEqual(font_path, "C:\\Windows\\Fonts\\arial.ttf")
    
    def test_get_system_font_path_darwin(self):
        """Test _get_system_font_path on macOS"""
        with patch('platform.system', return_value='Darwin'):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path == "/Library/Fonts/Arial Unicode.ttf"
                font_path = self.exporter._get_system_font_path()
                self.assertEqual(font_path, "/Library/Fonts/Arial Unicode.ttf")
    
    def test_get_system_font_path_linux(self):
        """Test _get_system_font_path on Linux"""
        with patch('platform.system', return_value='Linux'):
            with patch('os.path.exists') as mock_exists:
                mock_exists.side_effect = lambda path: path == "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                font_path = self.exporter._get_system_font_path()
                self.assertEqual(font_path, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    
    def test_get_system_font_path_no_font_found(self):
        """Test _get_system_font_path when no font is found"""
        with patch('platform.system', return_value='Linux'):
            with patch('os.path.exists', return_value=False):
                font_path = self.exporter._get_system_font_path()
                self.assertIsNone(font_path)
    
    def test_get_system_font_path_unknown_system(self):
        """Test _get_system_font_path on unknown system"""
        with patch('platform.system', return_value='UnknownOS'):
            with patch('os.path.exists', return_value=False):
                font_path = self.exporter._get_system_font_path()
                self.assertIsNone(font_path)
    
    def test_get_system_font_path_second_font_exists(self):
        """Test _get_system_font_path when first font doesn't exist but second does"""
        with patch('platform.system', return_value='Windows'):
            with patch('os.path.exists') as mock_exists:
                def exists_side_effect(path):
                    return path == "C:\\Windows\\Fonts\\Arial.ttf"
                mock_exists.side_effect = exists_side_effect
                font_path = self.exporter._get_system_font_path()
                self.assertEqual(font_path, "C:\\Windows\\Fonts\\Arial.ttf")
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_font_path(self, mock_exists, mock_fpdf_class):
        """Test export method when font path exists"""
        mock_exists.return_value = True
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        with patch.object(self.exporter, '_get_system_font_path', return_value='/path/to/font.ttf'):
            report_data = {
                'Section 1': {'key': 'value'},
                'Section 2': {'key2': 'value2'}
            }
            self.exporter.export(report_data, filename='test_output.pdf')
            
            # Verify PDF was created
            mock_pdf.add_page.assert_called()
            mock_pdf.cell.assert_called()
            mock_pdf.output.assert_called_with('test_output.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_without_font_path(self, mock_exists, mock_fpdf_class):
        """Test export method when font path doesn't exist"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        with patch.object(self.exporter, '_get_system_font_path', return_value=None):
            report_data = {'Section 1': 'Content'}
            self.exporter.export(report_data, filename='test_output2.pdf')
            
            # Should use fallback Arial font
            mock_pdf.set_font.assert_called()
            mock_pdf.output.assert_called_with('test_output2.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_font_load_exception(self, mock_exists, mock_fpdf_class):
        """Test export method when font loading raises exception"""
        mock_exists.return_value = True
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        mock_pdf.add_font.side_effect = Exception("Font load error")
        
        with patch.object(self.exporter, '_get_system_font_path', return_value='/path/to/font.ttf'):
            report_data = {'Section 1': 'Content'}
            # Should not raise exception, should fall back to Arial
            self.exporter.export(report_data, filename='test_output3.pdf')
            mock_pdf.set_font.assert_called()
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_empty_report_data(self, mock_exists, mock_fpdf_class):
        """Test export method with empty report data"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {}
        self.exporter.export(report_data, filename='test_empty.pdf')
        
        mock_pdf.add_page.assert_called()
        mock_pdf.cell.assert_called()
        mock_pdf.output.assert_called_with('test_empty.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_chart_paths(self, mock_exists, mock_fpdf_class):
        """Test export method with chart paths"""
        mock_exists.return_value = True
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        # Create a temporary chart file
        chart_path = os.path.join(self.temp_dir, 'chart.png')
        with open(chart_path, 'w') as f:
            f.write('fake image data')
        
        report_data = {'Section 1': 'Content'}
        chart_paths = [chart_path]
        
        self.exporter.export(report_data, chart_paths=chart_paths, filename='test_charts.pdf')
        
        # Verify image was added
        mock_pdf.add_page.assert_called()
        mock_pdf.image.assert_called()
        mock_pdf.output.assert_called_with('test_charts.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_nonexistent_chart_path(self, mock_exists, mock_fpdf_class):
        """Test export method with nonexistent chart path"""
        mock_exists.side_effect = lambda path: path != 'nonexistent.png'
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {'Section 1': 'Content'}
        chart_paths = ['nonexistent.png']
        
        self.exporter.export(report_data, chart_paths=chart_paths, filename='test_no_chart.pdf')
        
        # Image should not be added if file doesn't exist
        mock_pdf.add_page.assert_called()
        # image should not be called for nonexistent file
        image_calls = [call for call in mock_pdf.method_calls if call[0] == 'image']
        self.assertEqual(len(image_calls), 0)
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_multiple_charts(self, mock_exists, mock_fpdf_class):
        """Test export method with multiple chart paths"""
        mock_exists.return_value = True
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        chart_path1 = os.path.join(self.temp_dir, 'chart1.png')
        chart_path2 = os.path.join(self.temp_dir, 'chart2.png')
        for path in [chart_path1, chart_path2]:
            with open(path, 'w') as f:
                f.write('fake image data')
        
        report_data = {'Section 1': 'Content'}
        chart_paths = [chart_path1, chart_path2]
        
        self.exporter.export(report_data, chart_paths=chart_paths, filename='test_multiple_charts.pdf')
        
        # Verify multiple images were added
        self.assertEqual(mock_pdf.image.call_count, 2)
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_none_chart_paths(self, mock_exists, mock_fpdf_class):
        """Test export method with None chart_paths"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {'Section 1': 'Content'}
        self.exporter.export(report_data, chart_paths=None, filename='test_no_charts.pdf')
        
        # Should not try to add images
        mock_pdf.add_page.assert_called()
        image_calls = [call for call in mock_pdf.method_calls if call[0] == 'image']
        self.assertEqual(len(image_calls), 0)
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_with_empty_chart_paths(self, mock_exists, mock_fpdf_class):
        """Test export method with empty chart_paths list"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {'Section 1': 'Content'}
        self.exporter.export(report_data, chart_paths=[], filename='test_empty_charts.pdf')
        
        # Should not try to add images
        mock_pdf.add_page.assert_called()
        image_calls = [call for call in mock_pdf.method_calls if call[0] == 'image']
        self.assertEqual(len(image_calls), 0)
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_default_filename(self, mock_exists, mock_fpdf_class):
        """Test export method with default filename"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {'Section 1': 'Content'}
        self.exporter.export(report_data)
        
        # Should use default filename
        mock_pdf.output.assert_called_with('report.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_complex_report_data(self, mock_exists, mock_fpdf_class):
        """Test export method with complex nested report data"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {
            'Summary': {'Count': 10, 'Mean': 5.5},
            'Details': {'Min': 1, 'Max': 10, 'Median': 5}
        }
        self.exporter.export(report_data, filename='test_complex.pdf')
        
        # Verify multi_cell was called for each section
        mock_pdf.multi_cell.assert_called()
        mock_pdf.output.assert_called_with('test_complex.pdf')
    
    @patch('pdf_report_exporter.FPDF')
    @patch('os.path.exists')
    def test_export_string_content(self, mock_exists, mock_fpdf_class):
        """Test export method with string content in report data"""
        mock_exists.return_value = False
        mock_pdf = MagicMock()
        mock_fpdf_class.return_value = mock_pdf
        
        report_data = {
            'Section 1': 'Simple string content',
            'Section 2': {'nested': 'data'}
        }
        self.exporter.export(report_data, filename='test_string.pdf')
        
        mock_pdf.multi_cell.assert_called()
        mock_pdf.output.assert_called_with('test_string.pdf')


if __name__ == '__main__':
    unittest.main()


