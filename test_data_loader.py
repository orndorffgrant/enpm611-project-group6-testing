# test_data_loader.py
"""
Covers reading JSON into Issue objects and caching behavior.
"""

import json
import os
import tempfile
import unittest
from unittest import mock

import data_loader


def _write_temp_json(obj):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


class DataLoaderTests(unittest.TestCase):
    def setUp(self):
        # Clear module cache before test
        data_loader._ISSUES = None
        self._saved_environ = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved_environ)
        data_loader._ISSUES = None

    def test_get_issues_reads_file_and_constructs_Issue(self):
        sample = [{"a": 1}, {"b": 2}]
        path = _write_temp_json(sample)

        # Make config.get_parameter return the temp file path
        with mock.patch("data_loader.config.get_parameter", return_value=path):
            # Patch Issue so tests don't depend on model.Issue implementation
            with mock.patch("data_loader.Issue", side_effect=lambda d: {"wrapped": d}) as m_issue:
                dl = data_loader.DataLoader()
                issues = dl.get_issues()

                # Issue should be called for each JSON object
                self.assertEqual(m_issue.call_count, 2)
                # Returned list should contain the wrapped objects
                self.assertEqual(issues, [{"wrapped": {"a": 1}}, {"wrapped": {"b": 2}}])

        os.remove(path)

    def test_get_issues_uses_cached_result(self):
        sample = [{"x": 1}]
        path = _write_temp_json(sample)

        with mock.patch("data_loader.config.get_parameter", return_value=path):
            with mock.patch("data_loader.Issue", side_effect=lambda d: {"wrapped": d}) as m_issue:
                dl = data_loader.DataLoader()
                first = dl.get_issues()
                # Issue called once during first load
                self.assertEqual(m_issue.call_count, 1)

                # Call again; because of caching, Issue should not be called again
                m_issue.reset_mock()
                second = dl.get_issues()
                m_issue.assert_not_called()
                # The same object should be returned (cached)
                self.assertIs(first, second)

        os.remove(path)


if __name__ == "__main__":
    unittest.main()
