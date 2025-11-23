"""
Unit tests for model.py
Tests the Issue and Event classes with various edge cases and potential bugs.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from dateutil import parser
from model import Issue, Event, State


class TestEvent(unittest.TestCase):
    """Test cases for the Event class"""
    
    def test_event_init_with_none(self):
        """Test Event initialization with None"""
        event = Event(None)
        self.assertIsNone(event.event_type)
        self.assertIsNone(event.author)
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)
    
    def test_event_from_json_complete(self):
        """Test Event from_json with complete data"""
        jobj = {
            'event_type': 'commented',
            'author': 'test_user',
            'event_date': '2024-01-15T10:30:00Z',
            'label': 'bug',
            'comment': 'This is a test comment'
        }
        event = Event(jobj)
        self.assertEqual(event.event_type, 'commented')
        self.assertEqual(event.author, 'test_user')
        self.assertIsInstance(event.event_date, datetime)
        self.assertEqual(event.label, 'bug')
        self.assertEqual(event.comment, 'This is a test comment')
    
    def test_event_from_json_partial(self):
        """Test Event from_json with partial data"""
        jobj = {
            'event_type': 'labeled',
            'label': 'enhancement'
        }
        event = Event(jobj)
        self.assertEqual(event.event_type, 'labeled')
        self.assertIsNone(event.author)
        self.assertIsNone(event.event_date)
        self.assertEqual(event.label, 'enhancement')
        self.assertIsNone(event.comment)
    
    def test_event_from_json_invalid_date(self):
        """Test Event from_json with invalid date string"""
        jobj = {
            'event_type': 'commented',
            'event_date': 'invalid-date-string'
        }
        event = Event(jobj)
        self.assertEqual(event.event_type, 'commented')
        self.assertIsNone(event.event_date)
    
    def test_event_from_json_missing_date(self):
        """Test Event from_json with missing date"""
        jobj = {
            'event_type': 'commented',
            'event_date': None
        }
        event = Event(jobj)
        self.assertEqual(event.event_type, 'commented')
        self.assertIsNone(event.event_date)
    
    def test_event_from_json_empty_dict(self):
        """Test Event from_json with empty dictionary"""
        jobj = {}
        event = Event(jobj)
        self.assertIsNone(event.event_type)
        self.assertIsNone(event.author)
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)


class TestIssue(unittest.TestCase):
    """Test cases for the Issue class"""
    
    def test_issue_init_with_none(self):
        """Test Issue initialization with None"""
        issue = Issue(None)
        self.assertIsNone(issue.url)
        self.assertIsNone(issue.creator)
        self.assertEqual(issue.labels, [])
        self.assertIsNone(issue.state)
        self.assertEqual(issue.assignees, [])
        self.assertIsNone(issue.title)
        self.assertIsNone(issue.text)
        self.assertEqual(issue.number, -1)
        self.assertIsNone(issue.created_date)
        self.assertIsNone(issue.updated_date)
        self.assertIsNone(issue.timeline_url)
        self.assertEqual(issue.events, [])
    
    def test_issue_from_json_complete(self):
        """Test Issue from_json with complete data"""
        jobj = {
            'url': 'https://github.com/test/repo/issues/1',
            'creator': 'test_user',
            'labels': ['bug', 'priority-high'],
            'state': 'open',
            'assignees': ['user1', 'user2'],
            'title': 'Test Issue',
            'text': 'This is a test issue',
            'number': 1,
            'created_date': '2024-01-15T10:00:00Z',
            'updated_date': '2024-01-16T11:00:00Z',
            'timeline_url': 'https://github.com/test/repo/issues/1/timeline',
            'events': [
                {
                    'event_type': 'commented',
                    'author': 'user1',
                    'event_date': '2024-01-15T10:30:00Z'
                }
            ]
        }
        issue = Issue(jobj)
        self.assertEqual(issue.url, 'https://github.com/test/repo/issues/1')
        self.assertEqual(issue.creator, 'test_user')
        self.assertEqual(issue.labels, ['bug', 'priority-high'])
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ['user1', 'user2'])
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.text, 'This is a test issue')
        self.assertEqual(issue.number, 1)
        self.assertIsInstance(issue.created_date, datetime)
        self.assertIsInstance(issue.updated_date, datetime)
        self.assertEqual(issue.timeline_url, 'https://github.com/test/repo/issues/1/timeline')
        self.assertEqual(len(issue.events), 1)
        self.assertEqual(issue.events[0].event_type, 'commented')
    
    def test_issue_from_json_closed_state(self):
        """Test Issue from_json with closed state"""
        jobj = {
            'state': 'closed',
            'number': 2
        }
        issue = Issue(jobj)
        self.assertEqual(issue.state, State.closed)
        self.assertEqual(issue.number, 2)
    
    def test_issue_from_json_invalid_state(self):
        """Test Issue from_json with invalid state - should raise KeyError"""
        jobj = {
            'state': 'invalid_state'
        }
        with self.assertRaises(KeyError):
            Issue(jobj)
    
    def test_issue_from_json_missing_state(self):
        """Test Issue from_json with missing state - BUG: raises KeyError when state is None"""
        jobj = {
            'number': 3
        }
        # BUG: The code tries State[None] which raises KeyError
        with self.assertRaises(KeyError):
            Issue(jobj)
    
    def test_issue_from_json_invalid_number_string(self):
        """Test Issue from_json with invalid number as string"""
        jobj = {
            'number': 'not-a-number',
            'state': 'open'
        }
        issue = Issue(jobj)
        # Should fall back to -1 when conversion fails
        self.assertEqual(issue.number, -1)
    
    def test_issue_from_json_number_as_string(self):
        """Test Issue from_json with number as string"""
        jobj = {
            'number': '123',
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.number, 123)
    
    def test_issue_from_json_invalid_created_date(self):
        """Test Issue from_json with invalid created_date"""
        jobj = {
            'created_date': 'invalid-date',
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertIsNone(issue.created_date)
    
    def test_issue_from_json_invalid_updated_date(self):
        """Test Issue from_json with invalid updated_date"""
        jobj = {
            'updated_date': 'invalid-date',
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertIsNone(issue.updated_date)
    
    def test_issue_from_json_empty_labels(self):
        """Test Issue from_json with empty labels list"""
        jobj = {
            'labels': [],
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.labels, [])
    
    def test_issue_from_json_missing_labels(self):
        """Test Issue from_json with missing labels key"""
        jobj = {
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.labels, [])
    
    def test_issue_from_json_empty_assignees(self):
        """Test Issue from_json with empty assignees list"""
        jobj = {
            'assignees': [],
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.assignees, [])
    
    def test_issue_from_json_missing_assignees(self):
        """Test Issue from_json with missing assignees key"""
        jobj = {
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.assignees, [])
    
    def test_issue_from_json_empty_events(self):
        """Test Issue from_json with empty events list"""
        jobj = {
            'events': [],
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.events, [])
    
    def test_issue_from_json_missing_events(self):
        """Test Issue from_json with missing events key"""
        jobj = {
            'state': 'open'
        }
        issue = Issue(jobj)
        self.assertEqual(issue.events, [])
    
    def test_issue_from_json_multiple_events(self):
        """Test Issue from_json with multiple events"""
        jobj = {
            'state': 'open',
            'events': [
                {'event_type': 'commented', 'author': 'user1'},
                {'event_type': 'labeled', 'label': 'bug'},
                {'event_type': 'closed', 'author': 'user2'}
            ]
        }
        issue = Issue(jobj)
        self.assertEqual(len(issue.events), 3)
        self.assertEqual(issue.events[0].event_type, 'commented')
        self.assertEqual(issue.events[1].event_type, 'labeled')
        self.assertEqual(issue.events[2].event_type, 'closed')
    
    def test_issue_from_json_none_number(self):
        """Test Issue from_json with None number"""
        jobj = {
            'number': None,
            'state': 'open'
        }
        issue = Issue(jobj)
        # Should fall back to -1 when conversion fails
        self.assertEqual(issue.number, -1)
    
    def test_issue_from_json_empty_dict(self):
        """Test Issue from_json with empty dictionary - BUG: raises KeyError when state is None"""
        jobj = {}
        # BUG: The code tries State[None] which raises KeyError
        with self.assertRaises(KeyError):
            Issue(jobj)


if __name__ == '__main__':
    unittest.main()


