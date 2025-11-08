from model import Issue, State

MOCK_ISSUES_BASIC = [
    Issue({
        "url": "url1",
        "creator": "user1",
        "labels": [ "label1", "label2" ],
        "state": State.open,
        "assignees": [],
        "title": "title1",
        "text": "text1",
        "number": 1,
        "created_date": "2024-10-20T00:33:06+00:00",
        "updated_date": "2024-10-20T08:00:46+00:00",
        "timeline_url": "timelineurl1",
        "events": [
          {
            "event_type": "labeled",
            "author": "user1",
            "event_date": "2024-10-20T00:33:06+00:00",
            "label": "label1"
          },
        ]
    }),
    Issue({
        "url": "url2",
        "creator": "user2",
        "labels": [ "label1", "label2" ],
        "state": State.open,
        "assignees": [],
        "title": "title2",
        "text": "text2",
        "number": 2,
        "created_date": "2024-10-20T00:33:06+00:00",
        "updated_date": "2024-10-20T08:00:46+00:00",
        "timeline_url": "timelineurl2",
        "events": [
          {
            "event_type": "labeled",
            "author": "user2",
            "event_date": "2024-10-20T00:33:06+00:00",
            "label": "label2"
          },
        ]
    }),
]

class TestDataLoader:
    def __init__(self, mock_issues):
        self.issues = mock_issues

    def get_issues(self):
        return self.issues
