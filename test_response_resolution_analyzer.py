"""
Unit tests for response_resolution_analyzer.py
Tests the ResponseResolutionAnalyzer class with various edge cases and potential bugs.
"""
import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
from model import Issue, Event, State
from response_resolution_analyzer import ResponseResolutionAnalyzer


class TestResponseResolutionAnalyzer(unittest.TestCase):
    """Test cases for the ResponseResolutionAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('response_resolution_analyzer.config.get_parameter', return_value='test_value'):
            self.analyzer = ResponseResolutionAnalyzer()
        self.analyzer.USER = 'test_user'
        self.analyzer.LABEL = 'test_label'
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up any test chart files
        import os
        for filename in os.listdir('.'):
            if filename.startswith('chart_') and filename.endswith('.png'):
                try:
                    os.remove(filename)
                except:
                    pass
    
    def test_init(self):
        """Test ResponseResolutionAnalyzer initialization"""
        with patch('response_resolution_analyzer.config.get_parameter', return_value='test'):
            analyzer = ResponseResolutionAnalyzer()
            self.assertEqual(analyzer.USER, 'test')
            self.assertEqual(analyzer.LABEL, 'test')
            self.assertEqual(analyzer.report_data, {})
            self.assertEqual(analyzer.chart_paths, [])
    
    def test_get_first_response_times_empty_issues(self):
        """Test get_first_response_times with empty issues list"""
        issues = []
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_no_events(self):
        """Test get_first_response_times with issues that have no events"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = datetime.now()
        issue.events = []
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_no_events_attribute(self):
        """Test get_first_response_times with issues that don't have events attribute"""
        issue = Mock()
        issue.number = 1
        del issue.events  # Remove events attribute
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_no_created_date(self):
        """Test get_first_response_times with issues that have no created_date"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = None
        event = Event({'event_type': 'commented', 'event_date': '2024-01-15T10:30:00Z'})
        issue.events = [event]
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_no_created_date_attribute(self):
        """Test get_first_response_times with issues that don't have created_date attribute"""
        issue = Mock()
        issue.number = 1
        issue.events = []
        del issue.created_date  # Remove created_date attribute
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_single_comment(self):
        """Test get_first_response_times with single comment event"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        issue.created_date = created
        comment_time = datetime(2024, 1, 15, 12, 0, 0)
        event = Event({'event_type': 'commented', 'event_date': comment_time.isoformat()})
        issue.events = [event]
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[1], 2.0)  # 2 hours
    
    def test_get_first_response_times_multiple_comments(self):
        """Test get_first_response_times with multiple comment events"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        issue.created_date = created
        # Create events with different times
        event1 = Event({'event_type': 'commented', 'event_date': (created + timedelta(hours=5)).isoformat()})
        event2 = Event({'event_type': 'commented', 'event_date': (created + timedelta(hours=2)).isoformat()})
        event3 = Event({'event_type': 'labeled', 'event_date': (created + timedelta(hours=1)).isoformat()})
        issue.events = [event1, event2, event3]
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        # Should use the earliest comment (2 hours)
        self.assertEqual(result[1], 2.0)
    
    def test_get_first_response_times_case_insensitive_event_type(self):
        """Test get_first_response_times with case-insensitive event type"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        issue.created_date = created
        event = Event({'event_type': 'COMMENTED', 'event_date': (created + timedelta(hours=3)).isoformat()})
        issue.events = [event]
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result[1], 3.0)
    
    def test_get_first_response_times_no_comment_events(self):
        """Test get_first_response_times with no comment events"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        issue.created_date = created
        event = Event({'event_type': 'labeled', 'event_date': (created + timedelta(hours=1)).isoformat()})
        issue.events = [event]
        issues = [issue]
        result = self.analyzer.get_first_response_times(issues)
        self.assertEqual(result, {})
    
    def test_get_first_response_times_event_without_type(self):
        """Test get_first_response_times with events that don't have event_type - BUG: raises AttributeError when event_type is None"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        issue.created_date = created
        event = Event({'event_date': (created + timedelta(hours=1)).isoformat()})
        issue.events = [event]
        issues = [issue]
        # BUG: The code tries to call .lower() on None when event_type is None
        with self.assertRaises(AttributeError):
            self.analyzer.get_first_response_times(issues)
    
    def test_get_resolution_times_empty_issues(self):
        """Test get_resolution_times with empty issues list"""
        issues = []
        result = self.analyzer.get_resolution_times(issues)
        self.assertEqual(result, {})
    
    def test_get_resolution_times_open_state(self):
        """Test get_resolution_times with open issues"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = datetime(2024, 1, 15, 10, 0, 0)
        issue.updated_date = datetime(2024, 1, 16, 10, 0, 0)
        issue.state = State.open
        issues = [issue]
        result = self.analyzer.get_resolution_times(issues)
        self.assertEqual(result, {})
    
    def test_get_resolution_times_closed_state(self):
        """Test get_resolution_times with closed issues"""
        issue = Issue(None)
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        updated = datetime(2024, 1, 16, 10, 0, 0)
        issue.created_date = created
        issue.updated_date = updated
        issue.state = State.closed
        issues = [issue]
        result = self.analyzer.get_resolution_times(issues)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[1], 24.0)  # 24 hours
    
    def test_get_resolution_times_no_created_date(self):
        """Test get_resolution_times with issues that have no created_date"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = None
        issue.updated_date = datetime(2024, 1, 16, 10, 0, 0)
        issue.state = State.closed
        issues = [issue]
        result = self.analyzer.get_resolution_times(issues)
        self.assertEqual(result, {})
    
    def test_get_resolution_times_no_updated_date(self):
        """Test get_resolution_times with issues that have no updated_date"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = datetime(2024, 1, 15, 10, 0, 0)
        issue.updated_date = None
        issue.state = State.closed
        issues = [issue]
        result = self.analyzer.get_resolution_times(issues)
        self.assertEqual(result, {})
    
    def test_get_resolution_times_no_state(self):
        """Test get_resolution_times with issues that have no state - BUG: raises AttributeError when state is None"""
        issue = Issue(None)
        issue.number = 1
        issue.created_date = datetime(2024, 1, 15, 10, 0, 0)
        issue.updated_date = datetime(2024, 1, 16, 10, 0, 0)
        issue.state = None
        issues = [issue]
        # BUG: getattr returns None (not ""), so .lower() fails on None
        with self.assertRaises(AttributeError):
            self.analyzer.get_resolution_times(issues)
    
    def test_get_resolution_times_case_insensitive_state(self):
        """Test get_resolution_times with case-insensitive state check"""
        issue = Mock()
        issue.number = 1
        created = datetime(2024, 1, 15, 10, 0, 0)
        updated = datetime(2024, 1, 16, 10, 0, 0)
        issue.created_date = created
        issue.updated_date = updated
        issue.state = "CLOSED"  # Uppercase string, not State enum
        issues = [issue]
        result = self.analyzer.get_resolution_times(issues)
        # Should match because of .lower() == "closed"
        self.assertEqual(len(result), 1)
        self.assertEqual(result[1], 24.0)
    
    @patch('response_resolution_analyzer.np')
    def test_print_summary_statistics_empty_data(self, mock_np):
        """Test print_summary_statistics with empty data"""
        response_times = {}
        resolution_times = {}
        self.analyzer.print_summary_statistics(response_times, resolution_times)
        self.assertIn('Response Time Summary', self.analyzer.report_data)
        self.assertIn('Resolution Time Summary', self.analyzer.report_data)
        self.assertEqual(self.analyzer.report_data['Response Time Summary']['Info'], 'No data available.')
        self.assertEqual(self.analyzer.report_data['Resolution Time Summary']['Info'], 'No data available.')
    
    @patch('response_resolution_analyzer.np')
    def test_print_summary_statistics_with_data(self, mock_np):
        """Test print_summary_statistics with data"""
        mock_np.array.return_value = [1.0, 2.0, 3.0, 4.0, 5.0]
        mock_np.mean.return_value = 3.0
        mock_np.median.return_value = 3.0
        mock_np.min.return_value = 1.0
        mock_np.max.return_value = 5.0
        
        response_times = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0}
        resolution_times = {1: 10.0, 2: 20.0, 3: 30.0}
        
        self.analyzer.print_summary_statistics(response_times, resolution_times)
        
        self.assertIn('Response Time Summary', self.analyzer.report_data)
        self.assertIn('Resolution Time Summary', self.analyzer.report_data)
        self.assertEqual(self.analyzer.report_data['Response Time Summary']['Count'], 5)
        self.assertEqual(self.analyzer.report_data['Response Time Summary']['Mean (hrs)'], 3.0)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_time_histogram_empty_data(self, mock_plt):
        """Test plot_response_time_histogram with empty data"""
        response_times = {}
        self.analyzer.plot_response_time_histogram(response_times)
        # Should not create plot
        mock_plt.figure.assert_not_called()
        self.assertEqual(len(self.analyzer.chart_paths), 0)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_time_histogram_with_data(self, mock_plt):
        """Test plot_response_time_histogram with data"""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        response_times = {1: 1.0, 2: 2.0, 3: 3.0}
        self.analyzer.plot_response_time_histogram(response_times)
        mock_plt.figure.assert_called_once()
        mock_plt.hist.assert_called_once()
        mock_plt.savefig.assert_called_once()
        self.assertEqual(len(self.analyzer.chart_paths), 1)
        self.assertIn('chart_response_time_histogram.png', self.analyzer.chart_paths)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_time_histogram_custom_bins(self, mock_plt):
        """Test plot_response_time_histogram with custom bins"""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        response_times = {1: 1.0, 2: 2.0}
        custom_bins = [1, 5, 10]
        self.analyzer.plot_response_time_histogram(response_times, bins=custom_bins)
        mock_plt.hist.assert_called_once()
        # Check that custom bins were used
        call_args = mock_plt.hist.call_args
        self.assertEqual(call_args[1]['bins'], custom_bins)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_vs_resolution_scatter_no_overlap(self, mock_plt):
        """Test plot_response_vs_resolution_scatter with no overlapping data"""
        response_times = {1: 1.0, 2: 2.0}
        resolution_times = {3: 10.0, 4: 20.0}
        self.analyzer.plot_response_vs_resolution_scatter(response_times, resolution_times)
        # Should not create plot
        mock_plt.figure.assert_not_called()
        self.assertEqual(len(self.analyzer.chart_paths), 0)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_vs_resolution_scatter_with_overlap(self, mock_plt):
        """Test plot_response_vs_resolution_scatter with overlapping data"""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        response_times = {1: 1.0, 2: 2.0, 3: 3.0}
        resolution_times = {2: 10.0, 3: 20.0, 4: 30.0}
        self.analyzer.plot_response_vs_resolution_scatter(response_times, resolution_times)
        mock_plt.figure.assert_called_once()
        mock_plt.scatter.assert_called_once()
        mock_plt.savefig.assert_called_once()
        self.assertEqual(len(self.analyzer.chart_paths), 1)
        self.assertIn('chart_response_vs_resolution.png', self.analyzer.chart_paths)
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_vs_resolution_scatter_empty_response(self, mock_plt):
        """Test plot_response_vs_resolution_scatter with empty response_times"""
        response_times = {}
        resolution_times = {1: 10.0, 2: 20.0}
        self.analyzer.plot_response_vs_resolution_scatter(response_times, resolution_times)
        mock_plt.figure.assert_not_called()
    
    @patch('response_resolution_analyzer.plt')
    def test_plot_response_vs_resolution_scatter_empty_resolution(self, mock_plt):
        """Test plot_response_vs_resolution_scatter with empty resolution_times"""
        response_times = {1: 1.0, 2: 2.0}
        resolution_times = {}
        self.analyzer.plot_response_vs_resolution_scatter(response_times, resolution_times)
        mock_plt.figure.assert_not_called()
    
    @patch('response_resolution_analyzer.DataLoader')
    @patch('response_resolution_analyzer.plt')
    @patch('response_resolution_analyzer.np')
    def test_run_complete_flow(self, mock_np, mock_plt, mock_data_loader_class):
        """Test run method with complete flow"""
        # Setup mocks
        mock_np.array.return_value = [1.0, 2.0]
        mock_np.mean.return_value = 1.5
        mock_np.median.return_value = 1.5
        mock_np.min.return_value = 1.0
        mock_np.max.return_value = 2.0
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        
        # Create test issues
        issue1 = Issue(None)
        issue1.number = 1
        created1 = datetime(2024, 1, 15, 10, 0, 0)
        issue1.created_date = created1
        issue1.updated_date = datetime(2024, 1, 16, 10, 0, 0)
        issue1.state = State.closed
        event1 = Event({'event_type': 'commented', 'event_date': (created1 + timedelta(hours=2)).isoformat()})
        issue1.events = [event1]
        
        issue2 = Issue(None)
        issue2.number = 2
        created2 = datetime(2024, 1, 15, 10, 0, 0)
        issue2.created_date = created2
        issue2.updated_date = datetime(2024, 1, 16, 10, 0, 0)
        issue2.state = State.closed
        event2 = Event({'event_type': 'commented', 'event_date': (created2 + timedelta(hours=4)).isoformat()})
        issue2.events = [event2]
        
        mock_data_loader = MagicMock()
        mock_data_loader.get_issues.return_value = [issue1, issue2]
        mock_data_loader_class.return_value = mock_data_loader
        
        # Run the analyzer
        self.analyzer.run()
        
        # Verify DataLoader was called
        mock_data_loader.get_issues.assert_called_once()
        # Verify plots were created
        self.assertEqual(mock_plt.figure.call_count, 2)
        # Verify report data was populated
        self.assertIn('Response Time Summary', self.analyzer.report_data)
        self.assertIn('Resolution Time Summary', self.analyzer.report_data)
    
    @patch('response_resolution_analyzer.PDFReportExporter')
    def test_export_report_pdf(self, mock_pdf_exporter_class):
        """Test export_report_pdf method"""
        mock_exporter = MagicMock()
        mock_pdf_exporter_class.return_value = mock_exporter
        
        self.analyzer.report_data = {'Section 1': 'Content'}
        self.analyzer.chart_paths = ['chart1.png', 'chart2.png']
        
        self.analyzer.export_report_pdf('test_report.pdf')
        
        mock_pdf_exporter_class.assert_called_once_with("Response & Resolution Analysis Report")
        mock_exporter.export.assert_called_once_with(
            self.analyzer.report_data,
            chart_paths=self.analyzer.chart_paths,
            filename='test_report.pdf'
        )
    
    @patch('response_resolution_analyzer.PDFReportExporter')
    def test_export_report_pdf_default_filename(self, mock_pdf_exporter_class):
        """Test export_report_pdf with default filename"""
        mock_exporter = MagicMock()
        mock_pdf_exporter_class.return_value = mock_exporter
        
        self.analyzer.report_data = {'Section 1': 'Content'}
        self.analyzer.chart_paths = []
        
        self.analyzer.export_report_pdf()
        
        mock_exporter.export.assert_called_once_with(
            self.analyzer.report_data,
            chart_paths=self.analyzer.chart_paths,
            filename='response_resolution_report.pdf'
        )


if __name__ == '__main__':
    unittest.main()

