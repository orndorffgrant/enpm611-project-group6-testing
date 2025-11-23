# test_config.py
"""
Covers environment precedence, config file fallback, conversion, and set_parameter.
"""

import os
import json
import tempfile
import unittest

import config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        # Reset module state and save environment so tests are isolated
        config._config = None
        self._saved_environ = os.environ.copy()

    def tearDown(self):
        # Restore environment and module state
        os.environ.clear()
        os.environ.update(self._saved_environ)
        config._config = None

    def _create_temp_config(self, data):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_environment_overrides_config_file(self):
        # Create a config file with a value that should be ignored when env var exists
        cfg_path = self._create_temp_config({"MY_PARAM": "from_config"})
        # Temporarily point _get_default_path to our file
        original = config._get_default_path
        config._get_default_path = lambda: cfg_path

        try:
            # Set environment variable using a JSON string literal
            os.environ["MY_PARAM"] = '"from_env"'
            value = config.get_parameter("MY_PARAM")
            # The JSON string should be parsed to the Python string "from_env"
            self.assertEqual(value, "from_env")
        finally:
            config._get_default_path = original
            os.remove(cfg_path)

    def test_config_file_used_when_no_env(self):
        cfg_path = self._create_temp_config({"DATA_PATH": "/tmp/data.json"})
        original = config._get_default_path
        config._get_default_path = lambda: cfg_path

        try:
            # No environment variable set, so value should come from config file
            value = config.get_parameter("DATA_PATH")
            self.assertEqual(value, "/tmp/data.json")
        finally:
            config._get_default_path = original
            os.remove(cfg_path)

    def test_convert_to_typed_value_examples(self):
        # JSON string -> Python string
        self.assertEqual(config.convert_to_typed_value('"hello"'), "hello")
        # Numeric string -> int
        self.assertEqual(config.convert_to_typed_value("123"), 123)
        # Boolean string -> bool
        self.assertEqual(config.convert_to_typed_value("true"), True)
        # Non-string input returned unchanged
        self.assertEqual(config.convert_to_typed_value(5), 5)
        # Invalid JSON returns original string
        self.assertEqual(config.convert_to_typed_value("not json"), "not json")

    def test_set_parameter_writes_environment(self):
        config._config = {}
        # Strings are stored directly
        config.set_parameter("S1", "plain")
        self.assertEqual(os.environ["S1"], "plain")

        # Non-strings are stored with json: prefix
        config.set_parameter("S2", {"a": 1})
        self.assertTrue(os.environ["S2"].startswith("json:"))
        parsed = json.loads(os.environ["S2"][5:])
        self.assertEqual(parsed, {"a": 1})


if __name__ == "__main__":
    unittest.main()
