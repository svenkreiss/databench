import requests

def test_get():
	r = requests.get('http://localhost:5000/simplepi/')
	assert r.status_code == 200
