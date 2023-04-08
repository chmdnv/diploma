import requests
from pprint import pprint
import json
from random import choice


url = 'http://127.0.0.1:8000'

with open('data/data_for_test.json') as file:
    data = json.load(file)

r = requests.post(url=url + '/predict', json=choice(data))
# r = requests.get(url+'/version')
# r = requests.get(url+'/status')


if r.status_code == 200:
    pprint(r.json())
else:
    print(r.status_code)
