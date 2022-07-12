import araali

def test_alert():
    api = araali.API()
    alerts = len(api.get_alerts()[0])
    assert alerts == 0
