import pytest
import app
app_t = app.app.test_client()

def test_url():
    r = app_t.get('/24')
    j = r.get_json()
    assert len(j) == 24
    print(len(j))
    
    r = app_t.get('/48')
    j = r.get_json()
    assert len(j) == 48
    print(len(j))

    r = app_t.get('/72')
    j = r.get_json()
    assert len(j) == 72
    print(len(j))

    r = app_t.get('/nan')
    assert r.status_code == 404