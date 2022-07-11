import araali

def test_alert():
    api = araali.API()
    assert len(api.get_alerts()[0]) == 10
