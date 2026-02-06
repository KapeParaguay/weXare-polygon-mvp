from app.services.reputation import calculate_reputation
from app.models.experience_record import ExperienceRecord


class DummyQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self._rows


class DummyDB:
    def __init__(self, rows):
        self._rows = rows

    def query(self, model):
        return DummyQuery(self._rows)


def test_reputation_v1():
    rows = [
        ExperienceRecord(user_id="u1", quest_id=1, role="worker", outcome="SUCCESS", was_disputed=False, dispute_result=None, executor_type="HUMAN", created_at=None),
        ExperienceRecord(user_id="u1", quest_id=2, role="worker", outcome="FAIL", was_disputed=False, dispute_result=None, executor_type="HUMAN", created_at=None),
        ExperienceRecord(user_id="u1", quest_id=3, role="worker", outcome="SPLIT", was_disputed=False, dispute_result=None, executor_type="HUMAN", created_at=None),
    ]
    db = DummyDB(rows)
    rep = calculate_reputation(db, "u1", "worker")
    assert rep.score == 1000.0 + 10 - 10 + 2
