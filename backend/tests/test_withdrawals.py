from app.services.ledger import record_credit


def test_withdrawal_options(client):
    r = client.get("/withdrawal/options?country=PY")
    assert r.status_code == 200
    assert "options" in r.json()


def test_withdraw_request_crypto_validation(client):
    r = client.post("/wallet/withdraw", json={"amount": 10, "method": "crypto", "destination": "0xabc"})
    assert r.status_code == 200
    assert r.json()["status"] == "error"


def test_withdraw_request_bank(client, db_session):
    record_credit(db_session, user_id="user_1", amount=100)
    db_session.commit()
    r = client.post("/wallet/withdraw", json={"amount": 10, "method": "bank", "country": "PY"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_withdraw_insufficient_balance(client):
    r = client.post("/wallet/withdraw", json={"amount": 10, "method": "bank", "country": "PY"})
    assert r.status_code == 200
    assert r.json()["status"] == "error"
