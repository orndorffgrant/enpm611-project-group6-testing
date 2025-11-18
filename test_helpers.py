from model import Issue, State

def mock_issue(i, **kwargs):
    defaults = {
        "url": f"url{i}",
        "creator": f"user{i}",
        "labels": [ "label1", "label2" ],
        "state": State.open,
        "assignees": [],
        "title": f"title{i}",
        "text": f"text{i}",
        "number": i,
        "created_date": "2024-10-20T00:33:06+00:00",
        "updated_date": "2024-10-20T08:00:46+00:00",
        "timeline_url": f"timelineurl{i}",
        "events": [
          {
            "event_type": "labeled",
            "author": f"user{i}",
            "event_date": "2024-10-20T00:33:06+00:00",
            "label": "label2"
          },
        ]
    }
    return Issue({**defaults, **kwargs})
    
MOCK_ISSUES_BASIC = [
    mock_issue(1),
    mock_issue(2),
]

class TestDataLoader:
    def __init__(self, mock_issues):
        self.issues = mock_issues

    def get_issues(self):
        return self.issues
