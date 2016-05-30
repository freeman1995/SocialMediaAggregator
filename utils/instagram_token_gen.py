from utils.instagram_secrets import CLIENT_ID

URL = 'https://instagram.com/oauth/authorize/?client_id={}&amp;redirect_' \
      'uri=http://localhost&amp;response_type=token&amp;scope=public_content'.format(CLIENT_ID)

with open("TOKEN.txt", "w") as f:
    f.write(URL)

print("OK")
