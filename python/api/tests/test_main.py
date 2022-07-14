import araali
import pytest

@pytest.fixture(scope="session")
def api():
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
