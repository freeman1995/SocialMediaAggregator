import requests

from utils import facebook_secrets

URL = "https://graph.facebook.com/oauth/access_token"

r = requests.get(URL, {
    'client_id': facebook_secrets.APP_ID,
    'client_secret': facebook_secrets.APP_SECRET,
    'grant_type': 'client_credentials',
})

r.raise_for_status()

# print(r.text)

key, value = r.text.split("=")
assert key == "access_token"

with open("TOKEN.txt", "w") as f:
    f.write(value)

print("OK")
