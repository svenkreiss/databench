import requests

def test_get():
	r = requests.get('http://127.0.0.1:5000/dummypi/')
	assert r.status_code == 200
