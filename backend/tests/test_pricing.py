from app.services.pricing import compute_pricing


def test_pricing_math():
    p = compute_pricing(worker_cost=100, buffer_pct=20, moonpay_fee_pct=6)
    assert p.buffer_amount == 20
    assert round(p.moonpay_fee, 2) >= 7.2
    assert round(p.price_to_creator, 2) >= 127.2
