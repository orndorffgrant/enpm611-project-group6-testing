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
        # Avoid depending on real config file
        patcher = patch(
            "response_resolution_analyzer.config.get_parameter",
            return_value="dummy"
        )
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

        self.assertIn(1, result)
        # First response should be 2 hours after created_date
        self.assertAlmostEqual(result[1], 2.0, places=3)

    def test_get_first_response_times_ignores_issues_without_events(self):
        created = datetime(2024, 11, 1, 10, 0, 0)
        issue = DummyIssue(2, created_date=created, events=[])

        result = self.analyzer.get_first_response_times([issue])

        self.assertEqual(result, {})

    def test_get_first_response_times_bug_missing_event_type(self):
        """
        BUG: If an event has no event_type (or None), get_first_response_times
        will raise an AttributeError when calling e.event_type.lower().
        A robust implementation should ignore such malformed events instead.
        """
        created = datetime(2024, 11, 1, 10, 0, 0)

        class EventWithoutType:
            def __init__(self, event_date):
                self.event_date = event_date
                # NOTE: no event_type attribute at all

        bad_event = EventWithoutType(created + timedelta(hours=1))
        issue = DummyIssue(3, created_date=created, events=[bad_event])

        # We EXPECT this to safely ignore the malformed event and not crash,
        # but the current implementation will blow up with AttributeError.
        self.analyzer.get_first_response_times([issue])

    def test_get_resolution_times_closed_and_open(self):
        created = datetime(2024, 11, 1, 10, 0, 0)
        closed_issue = DummyIssue(
            1,
            created_date=created,
            updated_date=created + timedelta(hours=10),
            state="closed",
        )
        open_issue = DummyIssue(
            2,
            created_date=created,
            updated_date=created + timedelta(hours=5),
            state="open",
        )

        result = self.analyzer.get_resolution_times([closed_issue, open_issue])

        self.assertIn(1, result)
        self.assertAlmostEqual(result[1], 10.0, places=3)
        self.assertNotIn(2, result)

    @patch("builtins.print")
    def test_print_summary_statistics_populates_report_data(self, mock_print):
        response_times = {1: 2.0, 2: 4.0}
        resolution_times = {1: 10.0}

        self.analyzer.print_summary_statistics(response_times, resolution_times)

        self.assertIn("Response Time Summary", self.analyzer.report_data)
        self.assertIn("Resolution Time Summary", self.analyzer.report_data)

        resp_summary = self.analyzer.report_data["Response Time Summary"]
        self.assertEqual(resp_summary["Count"], 2)
        self.assertEqual(resp_summary["Min (hrs)"], 2.0)
        self.assertEqual(resp_summary["Max (hrs)"], 4.0)

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_time_histogram_adds_chart_path(self, mock_plt):
        data = {1: 1.0, 2: 5.0, 3: 10.0}
        self.analyzer.chart_paths = []

        self.analyzer.plot_response_time_histogram(data)

        self.assertEqual(len(self.analyzer.chart_paths), 1)
        mock_plt.hist.assert_called()
        mock_plt.savefig.assert_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_time_histogram_handles_empty(self, mock_plt):
        self.analyzer.chart_paths = []
        self.analyzer.plot_response_time_histogram({})

        # Should not add any chart paths or try to plot
        self.assertEqual(self.analyzer.chart_paths, [])
        mock_plt.hist.assert_not_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_vs_resolution_scatter_adds_chart_path(self, mock_plt):
        self.analyzer.chart_paths = []
        response = {1: 2.0, 2: 4.0}
        resolution = {1: 10.0, 2: 20.0}

        self.analyzer.plot_response_vs_resolution_scatter(response, resolution)

        self.assertEqual(len(self.analyzer.chart_paths), 1)
        mock_plt.scatter.assert_called()
        mock_plt.savefig.assert_called()

    @patch("response_resolution_analyzer.plt")
    def test_plot_response_vs_resolution_scatter_handles_no_overlap(self, mock_plt):
        self.analyzer.chart_paths = []
        response = {1: 2.0}
        resolution = {2: 10.0}  # no common keys

        self.analyzer.plot_response_vs_resolution_scatter(response, resolution)

        self.assertEqual(self.analyzer.chart_paths, [])
        mock_plt.scatter.assert_not_called()

    @patch("pdf_report_exporter.PDFReportExporter.export")
    def test_export_report_pdf_calls_exporter(self, mock_export):
        self.analyzer.report_data = {"Response Time Summary": {"Count": 0}}
        self.analyzer.chart_paths = ["chart1.png"]

        self.analyzer.export_report_pdf("custom_report.pdf")

        mock_export.assert_called_once()
        args, kwargs = mock_export.call_args
        self.assertIn("chart_paths", kwargs)
        self.assertEqual(kwargs["filename"], "custom_report.pdf")

    @patch("response_resolution_analyzer.DataLoader.get_issues", return_value=[])
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.plot_response_vs_resolution_scatter")
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.plot_response_time_histogram")
    @patch("response_resolution_analyzer.ResponseResolutionAnalyzer.print_summary_statistics")
    def test_run_integration_with_no_issues(
        self,
        mock_summary,
        mock_hist,
        mock_scatter,
        mock_get_issues,
    ):
        self.analyzer.run()

        mock_get_issues.assert_called_once()
        mock_summary.assert_called_once()
        mock_hist.assert_called_once()
        mock_scatter.assert_called_once()


if __name__ == "__main__":
    unittest.main()
