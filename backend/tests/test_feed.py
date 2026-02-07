def test_unified_feed(client):
    r = client.get("/feed")
    assert r.status_code == 200
    assert "cards" in r.json()
