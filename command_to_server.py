# coding: utf-8
import requests

r = requests.get('http://127.0.0.1:5000/update')
print(r.status_code)
