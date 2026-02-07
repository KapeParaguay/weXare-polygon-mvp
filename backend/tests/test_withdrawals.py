from app.services.ledger import record_credit


def test_withdrawal_options(client):
    r = client.get("/withdrawal/options?country=PY")
    assert r.status_code == 200
    data = r.json()
    assert "options" in data
    methods = {o["method"] for o in data["options"]}
    assert "moonpay" in methods
    assert "external" in methods


def test_withdraw_request_external_validation(client):
    r = client.post("/wallet/withdraw/external", json={"amount_usdc": 10, "destination": "0xabc"})
    assert r.status_code == 200
    assert r.json()["status"] == "error"


def test_withdraw_request_moonpay(client, db_session):
    record_credit(db_session, user_id="user_1", amount=100)
    db_session.commit()
    r = client.post("/wallet/withdraw/moonpay", json={"amount_usdc": 10})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_withdraw_insufficient_balance(client):
    r = client.post("/wallet/withdraw/moonpay", json={"amount_usdc": 10})
    assert r.status_code == 200
    assert r.json()["status"] == "error"
