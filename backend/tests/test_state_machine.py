from app.services.state_machine import can_fund, can_approve, can_dispute, can_submit_task, can_move_to_review


def test_can_fund():
    assert can_fund("DRAFT")
    assert not can_fund("FUNDED")


def test_can_approve():
    assert can_approve("REVIEW")
    assert not can_approve("FUNDED")


def test_can_dispute():
    assert can_dispute("REVIEW")
    assert can_dispute("FUNDED")
    assert not can_dispute("APPROVED")


def test_task_submit_and_review():
    assert can_submit_task("ACTIVE")
    assert not can_submit_task("OPEN")
    assert can_move_to_review("FUNDED")
