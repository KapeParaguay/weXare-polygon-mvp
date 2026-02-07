from app.models.escrow_ledger import EscrowLedger


def test_deposit_initiate_and_webhook(client, db_session):
    r = client.post("/wallet/deposit/initiate", json={"amount_usd": 50})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    deposit_id = data["deposit_id"]

    r2 = client.post("/webhooks/moonpay", json={"deposit_id": deposit_id, "status": "USDC_CONFIRMED"})
    assert r2.status_code == 200
    credits = db_session.query(EscrowLedger).filter(EscrowLedger.user_id == "user_1", EscrowLedger.kind == "CREDIT").all()
    assert len(credits) == 1
    assert credits[0].amount == 50
