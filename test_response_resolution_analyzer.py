import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from response_resolution_analyzer import ResponseResolutionAnalyzer


class DummyEvent:
    def __init__(self, event_type, event_date):
        self.event_type = event_type
        self.event_date = event_date


class DummyIssue:
    def __init__(self, number, created_date=None, updated_date=None, state="open", events=None):
        self.number = number
        self.created_date = created_date
        self.updated_date = updated_date
        self.state = state
        self.events = events or []


class TestResponseResolutionAnalyzer(unittest.TestCase):
    def setUp(self):
        patcher = patch("response_resolution_analyzer.config.get_parameter", return_value="dummy")
        self.addCleanup(patcher.stop)
        patcher.start()

        self.analyzer = ResponseResolutionAnalyzer()

    def test_get_first_response_times_basic(self):
        created = datetime(2024, 11, 1, 10, 0, 0)
        events = [
            DummyEvent("commented", created + timedelta(hours=2)),
            DummyEvent("commented", created + timedelta(hours=5)),
        ]
        issue = DummyIssue(1, created_date=created, events=events)

        result = self.analyzer.get_first_response_times([issue])
        self.assertAlmostEqual(result[1], 2.0, places=3)

    def test_get_first_response_times_ignores_issues_without_events(self):
        created = datetime(2024, 11, 1, 10, 0, 0)
        issue = DummyIssue(2, created_date=created, events=[])
        result = self.analyzer.get_first_response_times([issue])
        self.assertEqual(result, {})

    def test_get_first_response_times_bug_missing_event_type(self):
        created = datetime(2024, 11, 1, 10, 0, 0)

        class EventWithoutType:
            def __init__(self, event_date):
                self.event_date = event_date

        bad_event = EventWithoutType(created + timedelta(hours=1))
        issue = DummyIssue(3, created_date=created, events=[bad_event])

        self.analyzer.get_first_response_times([issue])  

    def test_get_resolution_times_closed_and_open(self):
        created = datetime(2024, 11, 1, 10, 0, 0)
        closed_issue = DummyIssue(1, created_date=created, updated_date=created + timedelta(hours=10), state="closed")
        open_issue = DummyIssue(2, created_date=created, updated_date=created + timedelta(hours=5), state="open")
        result = self.analyzer.get_resolution_times([closed_issue, open_issue])
        self.assertAlmostEqual(result[1], 10.0, places=3)
        self.assertNotIn(2, result)

    @patch("builtins.print")
    def test_print_summary_statistics_populates_report_data(self, mock_print):
        self.analyzer.print_summary_statistics({1: 2.0, 2: 4.0}, {1: 10.0})
        self.assertIn("Response Time Summary", self.analyzer.report_data)
        self.assertIn("Resolution Time Summary", self.analyzer.report_data)

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_time_histogram_adds_chart_path(self, mock_plt):
        self.analyzer.chart_paths = []
        self.analyzer.plot_response_time_histogram({1: 1.0, 2: 5.0, 3: 10.0})
        self.assertEqual(len(self.analyzer.chart_paths), 1)
        mock_plt.savefig.assert_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_time_histogram_handles_empty(self, mock_plt):
        self.analyzer.chart_paths = []
        self.analyzer.plot_response_time_histogram({})
        self.assertEqual(self.analyzer.chart_paths, [])
        mock_plt.savefig.assert_not_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_vs_resolution_scatter_adds_chart_path(self, mock_plt):
        self.analyzer.chart_paths = []
        self.analyzer.plot_response_vs_resolution_scatter({1: 2.0}, {1: 10.0})
        self.assertEqual(len(self.analyzer.chart_paths), 1)
        mock_plt.savefig.assert_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_vs_resolution_scatter_handles_no_overlap(self, mock_plt):
        self.analyzer.chart_paths = []
        self.analyzer.plot_response_vs_resolution_scatter({1: 2.0}, {2: 10.0})
        self.assertEqual(self.analyzer.chart_paths, [])
        mock_plt.savefig.assert_not_called()

    @patch("pdf_report_exporter.PDFReportExporter.export")
    def test_export_report_pdf_calls_exporter(self, mock_export):
        self.analyzer.report_data = {"Response Time Summary": {"Count": 0}}
        self.analyzer.chart_paths = ["chart1.png"]
        self.analyzer.export_report_pdf("custom_report.pdf")
        mock_export.assert_called_once()

    @patch("response_resolution_analyzer.DataLoader.get_issues", return_value=[])
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.plot_response_vs_resolution_scatter")
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.plot_response_time_histogram")
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.print_summary_statistics")
    def test_run_integration_with_no_issues(
        self, mock_summary, mock_hist, mock_scatter, mock_get_issues
    ):
        self.analyzer.run()
        mock_summary.assert_called_once()

    def test_resolution_times_missing_created_date_is_buggy(self):
        updated = datetime.now()
        issue = DummyIssue(
            99,
            created_date=None,  # missing
            updated_date=updated,
            state="closed"
        )

        result = self.analyzer.get_resolution_times([issue])

        # BUG: Closed issue should still be accounted for,
        # not silently ignored or dropped from results.
        self.assertIn(
            issue.number,
            result,
            "BUG: Missing created_date should not cause closed issues to disappear from resolution metrics"
        )

    def test_print_summary_statistics_invalid_data_is_buggy(self):
        self.analyzer.print_summary_statistics({1: None}, {})  # Should crash → BUG


if __name__ == "__main__":
    unittest.main()
