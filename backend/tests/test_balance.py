from app.services.ledger import record_credit, record_fund


def test_balance_available_locked_pending(client, db_session):
    # credit 100 to user
    record_credit(db_session, user_id="user_1", amount=100)
    # lock 40 for funding
    record_fund(db_session, quest_id=1, user_id="user_1", amount=40)
    db_session.commit()

    r = client.get("/wallet/balance")
    assert r.status_code == 200
    data = r.json()
    assert data["available_usdc"] == 60
    assert data["locked_usdc"] == 40
    assert data["pending_withdrawals_usdc"] == 0
    assert data["total_usdc"] == 100
