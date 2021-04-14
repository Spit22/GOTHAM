

def test_de_base(app, client):
    res = client.get('/')
    assert b'project' in res.data