import unittest
from datetime import datetime
from model import Event, Issue, State


class TestEvent(unittest.TestCase):
    def test_event_from_json_parses_all_fields(self):
        jobj = {
            "event_type": "commented",
            "author": "alice",
            "event_date": "2024-11-01T10:15:00Z",
            "label": "bug",
            "comment": "Looks broken"
        }

        ev = Event(jobj)
        self.assertEqual(ev.event_type, "commented")
        self.assertEqual(ev.author, "alice")
        self.assertEqual(ev.label, "bug")
        self.assertEqual(ev.comment, "Looks broken")
        self.assertIsInstance(ev.event_date, datetime)

    def test_event_from_json_invalid_date_does_not_crash(self):
        jobj = {
            "event_type": "commented",
            "author": "bob",
            "event_date": "not-a-real-date",
        }

        ev = Event(jobj)
        self.assertIsNone(ev.event_date)


class TestIssue(unittest.TestCase):
    def test_issue_from_json_basic_parsing(self):
        jobj = {
            "url": "https://example.com/issues/1",
            "creator": "alice",
            "labels": ["bug", "critical"],
            "state": "open",
            "assignees": ["bob"],
            "title": "Issue title",
            "text": "Issue body",
            "number": "42",
            "created_date": "2024-11-01T10:00:00Z",
            "updated_date": "2024-11-01T12:00:00Z",
            "timeline_url": "https://example.com/issues/1/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "author": "alice",
                    "event_date": "2024-11-01T11:00:00Z",
                }
            ],
        }

        issue = Issue(jobj)
        self.assertEqual(issue.url, jobj["url"])
        self.assertEqual(issue.creator, "alice")
        self.assertEqual(issue.labels, ["bug", "critical"])
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ["bob"])
        self.assertEqual(issue.title, "Issue title")
        self.assertEqual(issue.text, "Issue body")
        self.assertEqual(issue.number, 42)
        self.assertIsInstance(issue.created_date, datetime)
        self.assertIsInstance(issue.updated_date, datetime)
        self.assertEqual(issue.timeline_url, jobj["timeline_url"])
        self.assertEqual(len(issue.events), 1)
        self.assertIsInstance(issue.events[0], Event)

    def test_issue_from_json_missing_state_is_buggy(self):
        """
        BUG: Missing 'state' causes KeyError in Issue.from_json.
        """
        jobj = {
            "url": "https://example.com/issues/3",
            "creator": "dana",
            "number": "3",
        }

        Issue(jobj)  # <-- Should ERROR: KeyError (this is expected)

    def test_issue_from_json_assignees_should_parse_logins(self):
        """
        BUG: Assignees should be usernames, not list of dicts.
        """
        jobj = {
            "url": "https://example.com/issues/99",
            "creator": "alice",
            "state": "open",
            "number": "99",
            "assignees": [
                {"login": "bob"},
                {"login": "charlie"},
            ],
        }

        issue = Issue(jobj)

        # EXPECT: ["bob", "charlie"]
        # ACTUAL: [{"login": ...}, {"login": ...}]
        self.assertEqual(issue.assignees, ["bob", "charlie"])  # <-- Should FAIL


if __name__ == "__main__":
    unittest.main()
