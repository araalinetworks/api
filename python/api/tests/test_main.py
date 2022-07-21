import araali
import pytest

@pytest.fixture(scope="session")
def api():
    if araali.utils.cfg["backend"] != "nightly": araali.utils.config(backend="nightly")
    if araali.utils.cfg["tenant"] != "meta-tap": araali.utils.config(tenant="meta-tap")
    return araali.API()

def test_alerts(api):
    assert len(api.get_alerts()[0]) > 0

def test_assets(api):
    assert len(api.get_assets()[0]) > len(api.get_assets("scale")[0])

def test_links(api):
    assert len(api.get_links(zone="scale", app="araali-operator")[0]) > 0
    assert len(api.get_links(svc="169.254.169.254:80")[0]) > 0

def test_insights(api):
    assert len(api.get_insights()[0]) >= len(api.get_insights("scale")[0])

def test_templates(api):
    assert len(api.get_templates()[0]) > 0

def test_token(api):
    api.token(op="delete", name="ars_ut")

    api.token(op="add", name="ars_ut")
    tokens = api.token(op="show")[0]
    assert len([a for a in tokens["tokens"] if a["name"] == "ars_ut"]) == 1

    tokens = api.token(op="delete", name="ars_ut")
    tokens = api.token(op="show")[0]
    assert [a for a in tokens["tokens"] if a["name"] == "ars_ut"] == []