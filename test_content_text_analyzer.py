import unittest
from unittest import mock
from content_text_analyzer import ContentTextAnalyzer
from test_helpers import TestDataLoader, MOCK_ISSUES_BASIC, mock_issue

class TestContentTextAnalyzer(unittest.TestCase):
    @mock.patch("content_text_analyzer.ContentTextAnalyzer.get_common_error_messages")
    @mock.patch("content_text_analyzer.ContentTextAnalyzer.get_top_keywords")
    @mock.patch("content_text_analyzer.ContentTextAnalyzer.plot_wordcloud")
    @mock.patch("content_text_analyzer.ContentTextAnalyzer.plot_sentiment_categories")
    @mock.patch("content_text_analyzer.ContentTextAnalyzer.compute_sentiment_summary")
    @mock.patch("content_text_analyzer.DataLoader", return_value=TestDataLoader(MOCK_ISSUES_BASIC))
    def test_run(
        self,
        m_DataLoader,
        m_compute_sentiment_summary,
        m_plot_sentiment_categories,
        m_plot_wordcloud,
        m_get_top_keywords,
        m_get_common_error_messages,
    ):
        ContentTextAnalyzer().run()
        self.assertEqual(m_compute_sentiment_summary.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_plot_sentiment_categories.call_args_list, [mock.call()])
        self.assertEqual(m_plot_wordcloud.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_get_top_keywords.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])
        self.assertEqual(m_get_common_error_messages.call_args_list, [mock.call(MOCK_ISSUES_BASIC)])

    def test_get_top_keywords(self):
        analyzer = ContentTextAnalyzer()
        freq = analyzer.get_top_keywords([
            mock_issue(1, text="one two two three three three"),
            mock_issue(2, text="four four four four"),
        ])
        self.assertEqual(freq, analyzer.report_data["Top Keywords"])
        self.assertEqual(freq, [
            ("four", 4),
            ("three", 3),
            ("two", 2),
            ("one", 1),
        ])
    
    def test_get_common_error_messages(self):
        """
        This test fails because lines with "failure" are not interpreted as error messages.
        """
        analyzer = ContentTextAnalyzer()
        errors = analyzer.get_common_error_messages([
            mock_issue(1, text="failure"),
            mock_issue(2, text="error"),
            mock_issue(3, text="exception"),
        ])
        self.assertEqual(errors, analyzer.report_data["Common Errors"])
        self.assertEqual(errors, [
            ("failure", 1),
            ("error", 1),
            ("exception", 1),
        ])


    def test_compute_sentiment_summary(self):
        """
        This test fails because "the opposite of sad" is interpreted as "Negative".
        """
        analyzer = ContentTextAnalyzer()
        
        cats = analyzer.compute_sentiment_summary([
            mock_issue(1, text="I am happy"),
        ])
        self.assertEqual(cats, analyzer.report_data["Sentiment Summary"])
        self.assertEqual(cats, {
            "Positive": 1,
            "Neutral": 0,
            "Negative": 0,
        })
        
        cats = analyzer.compute_sentiment_summary([
            mock_issue(1, text="I am sad"),
        ])
        self.assertEqual(cats, analyzer.report_data["Sentiment Summary"])
        self.assertEqual(cats, {
            "Positive": 0,
            "Neutral": 0,
            "Negative": 1,
        })
        
        cats = analyzer.compute_sentiment_summary([
            mock_issue(1, text="I am neutral"),
        ])
        self.assertEqual(cats, analyzer.report_data["Sentiment Summary"])
        self.assertEqual(cats, {
            "Positive": 0,
            "Neutral": 1,
            "Negative": 0,
        })
        
        cats = analyzer.compute_sentiment_summary([
            mock_issue(1, text="I am the opposite of sad"),
        ])
        self.assertEqual(cats, analyzer.report_data["Sentiment Summary"])
        self.assertEqual(cats, {
            "Positive": 1,
            "Neutral": 0,
            "Negative": 0,
        })

    @mock.patch("content_text_analyzer.plt.show")
    @mock.patch("content_text_analyzer.plt.subplots")
    def test_plot_sentiment_categories(self, m_plt_subplots, m_plt_show):
        analyzer = ContentTextAnalyzer()
        analyzer.report_data["Sentiment Summary"] = {
            "Positive": 1,
            "Neutral": 2,
            "Negative": 3,
        }
        mock_ax = mock.MagicMock()
        m_plt_subplots.return_value = (mock.MagicMock(), mock_ax)
        
        analyzer.plot_sentiment_categories()
        
        self.assertEqual(list(mock_ax.bar.call_args_list[0].args[0]), ["Positive", "Neutral", "Negative"])
        self.assertEqual(list(mock_ax.bar.call_args_list[0].args[1]), [1, 2, 3])
        self.assertEqual(m_plt_show.call_args_list, [mock.call()])
        self.assertEqual(analyzer.chart_paths, ["sentiment_chart.png"])

    @mock.patch("content_text_analyzer.plt.show")
    @mock.patch("content_text_analyzer.plt.imshow")
    @mock.patch("content_text_analyzer.WordCloud")
    def test_plot_wordcloud(self, m_WordCloud, m_plt_imshow, m_plt_show):
        analyzer = ContentTextAnalyzer()
        m_wc = m_WordCloud.return_value
        
        analyzer.plot_wordcloud(MOCK_ISSUES_BASIC)
        
        self.assertEqual(m_wc.generate.call_args_list, [mock.call("text1 text2")])
        self.assertEqual(m_plt_imshow.call_args_list, [mock.call(m_wc, interpolation="bilinear")])
        self.assertEqual(m_plt_show.call_args_list, [mock.call()])
        self.assertEqual(analyzer.chart_paths, ["wordcloud.png"])

    @mock.patch("content_text_analyzer.PDFReportExporter")
    def test_export_report_pdf(self, m_PDFReportExporter):
        analyzer = ContentTextAnalyzer()
        analyzer.report_data = mock.sentinel.report_data
        analyzer.chart_paths = mock.sentinel.chart_paths
        
        analyzer.export_report_pdf()
        
        self.assertEqual(m_PDFReportExporter.call_args_list, [mock.call("Content/Text Analysis Report")])
        self.assertEqual(m_PDFReportExporter.return_value.export.call_args_list, [mock.call(mock.sentinel.report_data, chart_paths=mock.sentinel.chart_paths, filename="content_text_analysis_report.pdf")])
