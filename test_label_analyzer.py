# test_label_analyzer.py
"""
Covers counting logic, plotting, integration and export behaviour 
"""

import unittest
from unittest import mock
from collections import Counter

import label_analyzer
from label_analyzer import LabelAnalyzer

from test_helpers import TestDataLoader, mock_issue, MOCK_ISSUES_BASIC

class TestLabelAnalyzer(unittest.TestCase):
   def setUp(self):
       self.analyzer = LabelAnalyzer()

   def test_analyze_area_kind_and_prefix_counts(self):
       issues = [
           mock_issue(1, labels=["area/ui", "kind/bug", "priority/high"]),
           mock_issue(2, labels=["area/backend", "kind/bug", "kind/feature"]),
           mock_issue(3, labels=["area/ui", "kind/feature", "other"]),
           mock_issue(4, labels=[]),
       ]

       area_counts = self.analyzer.analyze_area_labels(issues)
       kind_counts = self.analyzer.analyze_kind_labels(issues)
       prefix_counts = self.analyzer.analyze_label_prefixes(issues)

       # Validate return types and values
       self.assertIsInstance(area_counts, Counter)
       self.assertEqual(dict(area_counts), {"area/ui": 2, "area/backend": 1})

       self.assertIsInstance(kind_counts, Counter)
       self.assertEqual(dict(kind_counts), {"kind/bug": 2, "kind/feature": 2})

       self.assertIsInstance(prefix_counts, Counter)
       # prefixes: area, kind, priority, other
       self.assertEqual(dict(prefix_counts), {"area": 3, "kind": 4, "priority": 1})

       # Ensure report_data updated with exact keys used in implementation
       self.assertIn("Label: Area Counts", self.analyzer.report_data)
       self.assertIn("Label: Kind Counts", self.analyzer.report_data)
       self.assertIn("Label: Prefix Breakdown", self.analyzer.report_data)

   @mock.patch("label_analyzer.plt.show")
   @mock.patch("label_analyzer.plt.savefig")
   def test_plot_kind_label_pie_chart_empty(self, m_savefig, m_show):
       # Empty counts should return None and not call save/show
       res = self.analyzer.plot_kind_label_pie_chart(Counter())
       self.assertIsNone(res)
       m_savefig.assert_not_called()
       m_show.assert_not_called()

   @mock.patch("label_analyzer.plt.show")
   @mock.patch("label_analyzer.plt.savefig")
   def test_plot_kind_label_pie_chart_with_other_grouping(self, m_savefig, m_show):
       # Create counts where many small labels should be grouped into "Other"
       # total = 100, one large 70, many small ones summing to 30; threshold 3% -> small ones grouped
       kind_counts = Counter({
           "kind/large": 70,
           "kind/a": 5,
           "kind/b": 5,
           "kind/c": 5,
           "kind/d": 5,
           "kind/e": 5,
       })
       save_path = "test_kind_chart.png"
       res = self.analyzer.plot_kind_label_pie_chart(kind_counts, save_path=save_path)

       # Should return the save_path and call show
       self.assertEqual(res, save_path)
       m_show.assert_called_once()

   @mock.patch("label_analyzer.plt.show")
   @mock.patch("label_analyzer.plt.savefig")
   def test_plot_label_prefix_distribution_empty(self, m_savefig, m_show):
       res = self.analyzer.plot_label_prefix_distribution(Counter())
       self.assertIsNone(res)
       m_savefig.assert_not_called()
       m_show.assert_not_called()

   @mock.patch("label_analyzer.plt.show")
   @mock.patch("label_analyzer.plt.savefig")
   def test_plot_label_prefix_distribution(self, m_savefig, m_show):
       prefix_counts = Counter({"area": 3, "kind": 5, "priority": 2})
       save_path = "test_prefix_chart.png"
       res = self.analyzer.plot_label_prefix_distribution(prefix_counts, save_path=save_path)

       self.assertEqual(res, save_path)
       m_show.assert_called_once()

   @mock.patch("label_analyzer.LabelAnalyzer.plot_label_prefix_distribution")
   @mock.patch("label_analyzer.LabelAnalyzer.plot_kind_label_pie_chart")
   @mock.patch("label_analyzer.DataLoader", return_value=TestDataLoader(MOCK_ISSUES_BASIC))
   def test_run_appends_chart_paths(self, m_DataLoader, m_plot_kind, m_plot_prefix):
       # Make the plot functions return paths (truthy) so run() appends them
       m_plot_kind.return_value = "kind_path.png"
       m_plot_prefix.return_value = "prefix_path.png"

       # run() should call DataLoader().get_issues() and then append returned chart paths
       self.analyzer.run()

       # run() should have populated report_data keys
       self.assertIn("Label: Kind Counts", self.analyzer.report_data)
       self.assertIn("Label: Prefix Breakdown", self.analyzer.report_data)
       # chart_paths should contain the two returned paths
       self.assertIn("kind_path.png", self.analyzer.chart_paths)
       self.assertIn("prefix_path.png", self.analyzer.chart_paths)

   @mock.patch("label_analyzer.PDFReportExporter")
   def test_export_report_pdf_calls_exporter(self, m_PDFReportExporter):
       # Prepare some report data and chart paths
       self.analyzer.report_data = {"Label: Kind Counts": {"kind/bug": 2}}
       self.analyzer.chart_paths = ["a.png", "b.png"]

       self.analyzer.export_report_pdf(filename="my_report.pdf")

       m_PDFReportExporter.assert_called_once_with("Label Analysis Report")
       m_PDFReportExporter.return_value.export.assert_called_once_with(
           self.analyzer.report_data,
           chart_paths=self.analyzer.chart_paths,
           filename="my_report.pdf"
       )


if __name__ == "__main__":
   unittest.main()
