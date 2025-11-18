import unittest
from unittest import mock
from example_analysis import ExampleAnalysis
from test_helpers import TestDataLoader, MOCK_ISSUES_BASIC

class TestExampleAnalysis(unittest.TestCase):
    @mock.patch("example_analysis.plt.show")
    @mock.patch("example_analysis.pd.DataFrame.from_records")
    @mock.patch("example_analysis.DataLoader", return_value=TestDataLoader(MOCK_ISSUES_BASIC))
    def test_run(self, m_DataLoader, m_from_records, m_plt_show):
        ExampleAnalysis().run()
        self.assertEqual(m_from_records.call_args_list, [mock.call([{"creator": "user1"}, {"creator": "user2"}])])
        self.assertEqual(m_plt_show.call_args_list, [mock.call()])
