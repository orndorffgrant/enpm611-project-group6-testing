import runpy
import sys
import unittest
from unittest import mock

import content_text_analyzer
import label_analyzer
import contributor_activity_analyzer
import response_resolution_analyzer
import pdf_report_exporter

class TestRun(unittest.TestCase):
    @mock.patch.object(sys, "argv", ["run.py", "--feature", "6"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___invalid_feature(
        self,
        m_input,
        m_print,
    ):
        runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [mock.call("⚠️ Invalid feature selected (choose 1–5).")])

    @mock.patch.object(sys, "argv", ["run.py", "--feature", "1"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___feature_one(
        self,
        m_input,
        m_print,
    ):
        m_analyzer = mock.MagicMock()
        with mock.patch.object(contributor_activity_analyzer, "ContributorActivityAnalyzer", m_analyzer):
            runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [
            mock.call("\n👥 Running Contributor Activity Analysis..."),
            mock.call("\n✅ Contributor Activity Analysis Complete."),
        ])
        self.assertTrue(m_analyzer.called)
        self.assertTrue(m_analyzer.return_value.run.called)

    @mock.patch.object(sys, "argv", ["run.py", "--feature", "2"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___feature_two(
        self,
        m_input,
        m_print,
    ):
        m_analyzer = mock.MagicMock()
        with mock.patch.object(response_resolution_analyzer, "ResponseResolutionAnalyzer", m_analyzer):
            runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [
            mock.call("\n🕒 Running Response & Resolution Analysis..."),
            mock.call("\n✅ Response & Resolution Analysis Complete."),
        ])
        self.assertTrue(m_analyzer.called)
        self.assertTrue(m_analyzer.return_value.run.called)

    @mock.patch.object(sys, "argv", ["run.py", "--feature", "3"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___feature_three(
        self,
        m_input,
        m_print,
    ):
        m_analyzer = mock.MagicMock()
        with mock.patch.object(content_text_analyzer, "ContentTextAnalyzer", m_analyzer):
            runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [
            mock.call("\n🧠 Running Content/Text Analysis..."),
            mock.call("\n✅ Content/Text Analysis Complete."),
        ])
        self.assertTrue(m_analyzer.called)
        self.assertTrue(m_analyzer.return_value.run.called)

    @mock.patch.object(sys, "argv", ["run.py", "--feature", "4"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___feature_four(
        self,
        m_input,
        m_print,
    ):
        m_analyzer = mock.MagicMock()
        with mock.patch.object(label_analyzer, "LabelAnalyzer", m_analyzer):
            runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [
            mock.call("\n🏷️ Running Label Analysis..."),
            mock.call("\n✅ Label Analysis Complete."),
        ])
        self.assertTrue(m_analyzer.called)
        self.assertTrue(m_analyzer.return_value.run.called)

    @mock.patch.object(sys, "argv", ["run.py", "--feature", "5"])
    @mock.patch("builtins.print")
    @mock.patch("builtins.input", return_value="n")
    def test___main___feature_five(
        self,
        m_input,
        m_print,
    ):
        m_analyzer1 = mock.MagicMock()
        m_analyzer2 = mock.MagicMock()
        m_analyzer3 = mock.MagicMock()
        m_analyzer4 = mock.MagicMock()
        m_exporter = mock.MagicMock()
        with mock.patch.object(contributor_activity_analyzer, "ContributorActivityAnalyzer", m_analyzer1):
            with mock.patch.object(response_resolution_analyzer, "ResponseResolutionAnalyzer", m_analyzer2):
                with mock.patch.object(content_text_analyzer, "ContentTextAnalyzer", m_analyzer3):
                    with mock.patch.object(label_analyzer, "LabelAnalyzer", m_analyzer4):
                        with mock.patch.object(pdf_report_exporter, "PDFReportExporter", m_exporter):
                            runpy.run_module("run", run_name="__main__")
        self.assertTrue(m_analyzer1.called)
        self.assertTrue(m_analyzer2.called)
        self.assertTrue(m_analyzer3.called)
        self.assertTrue(m_analyzer4.called)
        self.assertTrue(m_analyzer1.return_value.run.called)
        self.assertTrue(m_analyzer2.return_value.run.called)
        self.assertTrue(m_analyzer3.return_value.run.called)
        self.assertTrue(m_analyzer4.return_value.run.called)
        
        self.assertEqual(m_exporter.call_args_list, [mock.call("Combined Project Analysis Report")])
        self.assertEqual(m_exporter.return_value.export.call_args_list, [
            mock.call(mock.ANY, chart_paths=mock.ANY, filename="combined_analysis_report.pdf")
        ])

        self.assertEqual(m_print.call_args_list, [
            mock.call("\n📊 Running Combined Report (All Analyses)..."),
            mock.call("\n✅ Combined Analysis Report Generated as combined_analysis_report.pdf"),
        ])

    @mock.patch("builtins.print")
    @mock.patch("builtins.input")
    def test___main___interactive_mode_feature_three(
        self,
        m_input,
        m_print,
    ):
        m_input.side_effect = [
            "y",
            "6",
            "3",
            "",
            "",
            "",
            "",
        ]
        m_analyzer = mock.MagicMock()
        with mock.patch.object(content_text_analyzer, "ContentTextAnalyzer", m_analyzer):
            runpy.run_module("run", run_name="__main__")
        self.assertEqual(m_print.call_args_list, [
            mock.call("\n=== Interactive Analyzer Runner ==="),
            mock.call("1️⃣  Contributor Activity Analysis"),
            mock.call("2️⃣  Response & Resolution Analysis"),
            mock.call("3️⃣  Content/Text Analysis"),
            mock.call("4️⃣  Label Analysis"),
            mock.call("5️⃣  Combined Report (All Analyses)"),
            mock.call("Invalid input. Please enter 1–5."),
            mock.call("\n🧠 Running Content/Text Analysis..."),
            mock.call("\n✅ Content/Text Analysis Complete."),
        ])
        self.assertTrue(m_analyzer.called)
        self.assertTrue(m_analyzer.return_value.run.called)
