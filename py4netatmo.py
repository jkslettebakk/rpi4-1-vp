import requests
import json
from datetime import datetime, timedelta
from time import strftime, localtime

def load_secrets(file_path='netatmo_secrets.json'):
    with open(file_path, 'r') as file:
        return json.load(file)

secrets = load_secrets()

# Netatmo OAuth2 endpoints
AUTH_URL = "https://api.netatmo.com/oauth2/token"
API_URL = "https://api.netatmo.com/api/getstationsdata"

# Global variables for token management
access_token = None
token_expiration_time = datetime.min

def authenticate():
    """Authenticate with Netatmo and manage access token."""
    global access_token, token_expiration_time
    if datetime.now() < token_expiration_time:
        return

    if secrets["REFRESH_TOKEN"]:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": secrets["REFRESH_TOKEN"],
            "client_id": secrets["CLIENT_ID"],
            "client_secret": secrets["CLIENT_SECRET"]
        }
    else:
        payload = {
            "grant_type": "authorization_code",
            "code": secrets["AUTHORIZATION_CODE"],
            "redirect_uri": secrets["REDIRECT_URI"],
            "client_id": secrets["CLIENT_ID"],
            "client_secret": secrets["CLIENT_SECRET"]
        }

    response = requests.post(AUTH_URL, data=payload)
    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        secrets["REFRESH_TOKEN"] = data.get("refresh_token", secrets["REFRESH_TOKEN"])
        token_expiration_time = datetime.now() + timedelta(seconds=data["expires_in"])
        # Update the secrets file with the new refresh token
        with open('netatmo_secrets.json', 'w') as file:
            json.dump(secrets, file, indent=4)
    else:
        raise Exception(f"Failed to authenticate: {response.text}")

def fetch_netatmo_data():
    """Fetch data from Netatmo using the access token."""
    authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"device_id": secrets['DEVICE_ID']}
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.text}")
    return response.json()

def OutputDataForVPApp(data):
    outdorTimestamp = data["body"]["devices"][0]["modules"][0]["dashboard_data"]["time_utc"]
    outdoor_temp = data["body"]["devices"][0]["modules"][0]["dashboard_data"]["Temperature"]
    inhouse_temp = data["body"]["devices"][0]["dashboard_data"]["Temperature"]
    inhousAndOutdorResult = {
        "time_utc": strftime('%Y-%m-%d %H:%M:%S', localtime(outdorTimestamp)),
        "inhouse": inhouse_temp,
        "outdor": outdoor_temp
    }
    # Make inhousAndOutdorResult a proper json string
    inhousAndOutdorResult = json.dumps(inhousAndOutdorResult)
    print(inhousAndOutdorResult)


def main():
    try:
        data = fetch_netatmo_data()
        # Add your data handling logic here
        OutputDataForVPApp(data)
        # print(data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

