import json
import requests
import os
import time
import sys

# Global variabel for autentiseringsfilen
auth_file = os.path.expanduser('~/.netatmo.credentials.json')

# Globale konstanter
AUTH_URL = 'https://api.netatmo.com/oauth2/token'
WEATHER_URL = 'https://api.netatmo.com/api/getstationsdata'
REDIRECT_URI = 'https://www.slettebakk.com'

# Les autentiseringsdata fra fil
with open(auth_file) as f:
    auth_data = json.load(f)

# Konfigurasjon
client_id = auth_data['client_id']
client_secret = auth_data['client_secret']
refresh_token = auth_data['refresh_token']
access_token = auth_data['access_token']
token_expiry = auth_data.get('token_expiry', 0)

# Funksjon for å fornye tilgangstoken
def refresh_access_token(refresh_token):
    auth_payload = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    response = requests.post(AUTH_URL, data=auth_payload)
    tokens = response.json()
    print(f"Refresh token response: {tokens}", file=sys.stderr)  # Log response for debugging to stderr
    if 'access_token' in tokens and 'refresh_token' in tokens:
        return tokens['access_token'], tokens['refresh_token'], time.time() + tokens['expires_in']
    else:
        raise Exception(f"Failed to refresh access token: {tokens}")

# Sjekk om tilgangstoken er utløpt
if time.time() >= token_expiry:
    try:
        access_token, refresh_token, token_expiry = refresh_access_token(refresh_token)
        # Oppdater autentiseringsdata med nye tokens og utløpstid
        auth_data['access_token'] = access_token
        auth_data['refresh_token'] = refresh_token
        auth_data['token_expiry'] = token_expiry
        with open(auth_file, 'w') as f:
            json.dump(auth_data, f)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(1)

# Hente værdata
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(WEATHER_URL, headers=headers)
weather_data = response.json()

print(json.dumps(weather_data, indent=2))  # Print Netatmo data to stdout