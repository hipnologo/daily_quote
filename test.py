import requests
api_url = 'https://api.api-ninjas.com/v1/quotes'
api_key = '2JORP+gh/eyAMbtZ6/5mFQ==xkb9fNkyTI1H6xT1'
response = requests.get(api_url, headers={'X-Api-Key': api_key})
print(response.status_code)
print(response.text)