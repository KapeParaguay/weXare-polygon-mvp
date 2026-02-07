from datetime import datetime
from app.services.orchestration import issue_wave
from app.models.worker_profile import WorkerProfile
from app.models.user import User
from app.models.experience_record import ExperienceRecord


class DummyQuery:
    def __init__(self, rows):
        self._rows = rows

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return self._rows


class DummyDB:
    def __init__(self, rows):
        self._rows = rows
        self.added = []

    def query(self, *args, **kwargs):
        if args and args[0] == ExperienceRecord:
            return DummyQuery([])
        return DummyQuery(self._rows)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None


def test_issue_wave_creates_offers():
    rows = [
        (WorkerProfile(user_id="u1"), User(id="u1", email="u1@x.com", status="ACTIVE", roles="WORKER")),
        (WorkerProfile(user_id="u2"), User(id="u2", email="u2@x.com", status="ACTIVE", roles="WORKER")),
    ]
    db = DummyDB(rows)
    offers = issue_wave(db, task_id=1, count=2)
    assert len(offers) == 2
