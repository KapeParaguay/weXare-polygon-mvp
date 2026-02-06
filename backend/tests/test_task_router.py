from app.services.task_router import route_quest
from app.models.quest import Quest


class DummyDB:
    def __init__(self, quest):
        self.quest = quest
        self.added = []

    def get(self, model, obj_id):
        return self.quest

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None


def test_task_router_auto_success():
    q = Quest(id=1, project_id=1, parent_quest_id=None, index=1, scope_hash="s", budget=100, status="FUNDED", funded_at=None)
    db = DummyDB(q)
    res = route_quest(db, 1, "writing")
    assert res["status"] == "auto_success"


def test_task_router_fallback():
    q = Quest(id=1, project_id=1, parent_quest_id=None, index=1, scope_hash="s", budget=100, status="FUNDED", funded_at=None)
    db = DummyDB(q)
    res = route_quest(db, 1, "research")
    assert res["status"] == "needs_human"
