from app.models.escrow_ledger import EscrowLedger


def test_payment_initiate_and_confirm(client, db_session):
    r = client.post("/payments/initiate", json={"quest_id": 1, "amount": 100})
    assert r.status_code == 200
    data = r.json()
    assert "payment_id" in data

    pid = data["payment_id"]
    r2 = client.post(f"/payments/{pid}/confirm", json={"status": "USDC_CONFIRMED"})
    assert r2.status_code == 200
    assert r2.json()["payment_status"] == "USDC_CONFIRMED"

    credits = db_session.query(EscrowLedger).filter(EscrowLedger.user_id == "user_1", EscrowLedger.kind == "CREDIT").all()
    assert len(credits) == 1
    assert credits[0].amount == 100
