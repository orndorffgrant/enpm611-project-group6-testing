import unittest
from unittest import mock
from contributor_activity_analyzer import ContributorActivityAnalyzer
from test_helpers import TestDataLoader, MOCK_ISSUES_BASIC, mock_issue

class TestContributorActivityAnalyzer(unittest.TestCase):
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.plot_issue_type_distribution_per_contributor")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.plot_top_contributors_by_active_issues")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.printContributorSummary")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.printIssueTypeDistributionPerContributor")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.printActiveIssuesPerContributor")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_active_issues_count_per_contributor")
    @mock.patch("contributor_activity_analyzer.DataLoader", return_value=TestDataLoader(MOCK_ISSUES_BASIC))
    def test_run(
        self,
        m_DataLoader,
        m_get_active_issues_count_per_contributor,
        m_get_issue_type_distribution_per_contributor,
        m_printActiveIssuesPerContributor,
        m_printIssueTypeDistributionPerContributor,
        m_printContributorSummary,
        m_plot_top_contributors_by_active_issues,
        m_plot_issue_type_distribution_per_contributor,
    ):
        ContributorActivityAnalyzer().run()
        self.assertEqual(m_get_active_issues_count_per_contributor.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_get_issue_type_distribution_per_contributor.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_printActiveIssuesPerContributor.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_printIssueTypeDistributionPerContributor.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_printContributorSummary.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_plot_top_contributors_by_active_issues.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_plot_issue_type_distribution_per_contributor.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])

    def test_get_active_issues_count_per_contributor(self):
        analyzer = ContributorActivityAnalyzer()
        issues = analyzer.get_active_issues_count_per_contributor([
            mock_issue(1, assignees=[{"login": "one"}]),
            mock_issue(2, assignees=[{"login": "two"}]),
            mock_issue(3, assignees=[{"login": "two"}]),
            mock_issue(4, assignees=[{"login": "three"}]),
            mock_issue(5, assignees=[{"login": "three"}]),
            mock_issue(6, assignees=[{"login": "three"}]),
        ])
        self.assertEqual(issues, {
            "one": 1,
            "two": 2,
            "three": 3,
        })
    
    def test_get_issue_type_distribution_per_contributor(self):
        analyzer = ContributorActivityAnalyzer()
        issues = analyzer.get_issue_type_distribution_per_contributor([
            mock_issue(1, labels=["doesnt-count"], assignees=[{"login": "one"}]),
            mock_issue(2, labels=["kind/one", "kind/two"], assignees=[{"login": "two"}]),
            mock_issue(3, labels=["kind/two", "kind/three"], assignees=[{"login": "two"}]),
            mock_issue(4, labels=["kind/one"], assignees=[{"login": "three"}]),
            mock_issue(5, labels=["ignore", "kind/one"], assignees=[{"login": "three"}]),
            mock_issue(6, assignees=[{"login": "three"}]),
        ])
        self.assertEqual(issues, {
            "two": {
                "one": 1,
                "two": 2,
                "three": 1,
            },
            "three": {
                "one": 2,
            },
        })

    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_active_issues_count_per_contributor")
    def test_get_contributor_summary(
        self,
        m_get_active_issues_count_per_contributor,
        m_get_issue_type_distribution_per_contributor,
    ):
        m_get_active_issues_count_per_contributor.return_value = {
            "contributor": 42,
        }
        m_get_issue_type_distribution_per_contributor.return_value = {
            "contributor": {
                "fourty": 2
            }
        }
        
        analyzer = ContributorActivityAnalyzer()
        summary = analyzer.get_contributor_summary("contributor", mock.MagicMock())
        
        self.assertEqual(summary, {
            "active_issues": 42,
            "issue_type_distribution": {
                "fourty": 2
            },
        })
        
    @mock.patch("contributor_activity_analyzer.plt.show")
    @mock.patch("contributor_activity_analyzer.plt.barh")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_active_issues_count_per_contributor")
    def test_plot_top_contributors_by_active_issues(
        self,
        m_get_active_issues_count_per_contributor,
        m_plt_barh,
        m_plt_show,
    ):
        m_get_active_issues_count_per_contributor.return_value = {
            "one": 1,
            "two": 2,
            "three": 3,
        }
        
        analyzer = ContributorActivityAnalyzer()
        analyzer.plot_top_contributors_by_active_issues(mock.MagicMock())
        
        self.assertEqual(m_plt_barh.call_args_list, [mock.call(("three", "two", "one"), (3, 2, 1), color="skyblue")])
        self.assertEqual(m_plt_show.call_args_list, [mock.call()])
        self.assertEqual(analyzer.chart_paths, ["chart_active_issues_per_contributor.png"])

    @mock.patch("contributor_activity_analyzer.plt.show")
    @mock.patch("contributor_activity_analyzer.plt.barh")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor")
    def test_plot_issue_type_distribution_per_contributor(
        self,
        m_get_issue_type_distribution_per_contributor,
        m_plt_barh,
        m_plt_show,
    ):
        m_get_issue_type_distribution_per_contributor.return_value = {
            "one": {
                "k1": 1,
                "k2": 2,
            },
            "two": {
                "k2": 2,
                "k3": 3,
            },
        }
        
        analyzer = ContributorActivityAnalyzer()
        analyzer.plot_issue_type_distribution_per_contributor(mock.MagicMock())
        
        self.assertEqual(m_plt_barh.call_args_list, [
            mock.call(["one", "two"], [1, 0], left=[0,0], color=mock.ANY, label="k1"),
            mock.call(["one", "two"], [2, 2], left=[1,0], color=mock.ANY, label="k2"),
            mock.call(["one", "two"], [0, 3], left=[3,2], color=mock.ANY, label="k3"),
        ])
        self.assertEqual(m_plt_show.call_args_list, [mock.call()])
        self.assertEqual(analyzer.chart_paths, ["chart_issue_type_distribution_per_contributor.png"])
        
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_active_issues_count_per_contributor")
    @mock.patch("builtins.print")
    def test_printActiveIssuesPerContributor(
        self,
        m_print,
        m_get_active_issues_count_per_contributor,
    ):
        m_get_active_issues_count_per_contributor.return_value = {
            "one": 1,
            "two": 2,
            "three": 3,
        }
        
        analyzer = ContributorActivityAnalyzer()
        analyzer.printActiveIssuesPerContributor(mock.MagicMock())
        
        self.assertEqual(m_print.call_args_list, [
            mock.call("\nActive Issues per Contributor:"),
            mock.call("one: 1"),
            mock.call("two: 2"),
            mock.call("three: 3"),
        ])

    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor")
    @mock.patch("builtins.print")
    def test_printIssueTypeDistributionPerContributor(
        self,
        m_print,
        m_get_issue_type_distribution_per_contributor,
    ):
        m_get_issue_type_distribution_per_contributor.return_value = {
            "one": {
                "k1": 1,
                "k2": 2,
            },
            "two": {
                "k2": 2,
                "k3": 3,
            },
        }
        
        analyzer = ContributorActivityAnalyzer()
        analyzer.printIssueTypeDistributionPerContributor(mock.MagicMock())
        
        self.assertEqual(m_print.call_args_list, [
            mock.call("\nIssue Type Distribution per Contributor:"),
            mock.call("one: {'k1': 1, 'k2': 2}"),
            mock.call("two: {'k2': 2, 'k3': 3}"),
        ])

    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_contributor_summary")
    @mock.patch("contributor_activity_analyzer.ContributorActivityAnalyzer.get_issue_type_distribution_per_contributor")
    @mock.patch("builtins.print")
    @mock.patch("builtins.input")
    def test_printContributorSummary(
        self,
        m_input,
        m_print,
        m_get_issue_type_distribution_per_contributor,
        m_get_contributor_summary,
    ):
        m_input.side_effect = ["one", "q"]
        m_get_issue_type_distribution_per_contributor.return_value = {
            "one": {},
            "two": {},
        }
        m_get_contributor_summary.return_value = {
            "active_issues": 4,
            "issue_type_distribution": {
                "k1": 1,
                "k2": 2,
                "k3": 3,
            }
        }
        
        analyzer = ContributorActivityAnalyzer()
        analyzer.printContributorSummary(mock.MagicMock())
        
        self.assertEqual(m_print.call_args_list, [
            mock.call("\nSummary for one:"),
            mock.call("Active Issues: 4"),
            mock.call("Issue Type Distribution:"),
            mock.call("  k1: 1"),
            mock.call("  k2: 2"),
            mock.call("  k3: 3"),
        ])

    @mock.patch("contributor_activity_analyzer.PDFReportExporter")
    def test_export_report_pdf(self, m_PDFReportExporter):
        analyzer = ContributorActivityAnalyzer()
        analyzer.report_data = mock.sentinel.report_data
        analyzer.chart_paths = mock.sentinel.chart_paths
        
        analyzer.export_report_pdf()
        
        self.assertEqual(m_PDFReportExporter.call_args_list, [mock.call("Contributor Activity Analysis Report")])
        self.assertEqual(m_PDFReportExporter.return_value.export.call_args_list, [mock.call(mock.sentinel.report_data, chart_paths=mock.sentinel.chart_paths, filename="contributor_activity_report.pdf")])
