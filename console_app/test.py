import requests

url = 'http://127.0.0.1:8000/console'
param = {"path": "overview"}
post = requests.post(url=url, data=param)
