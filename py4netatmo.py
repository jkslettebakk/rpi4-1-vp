import requests
import json
from datetime import datetime, timedelta
from time import strftime, localtime

# Replace these with your own client_id and client_secret
# Replace these with your own client_id and client_secret
CLIENT_ID = "6506e1ce5765a18a1b081431"
CLIENT_SECRET = "HvDmwoEBJPfSeQyBUf4XM1fCJu"
USERNAME = "jkslettebakk@yahoo.no"
PASSWORD = "Frank#10"
DEVICE_ID = "70:ee:50:3c:f4:20"
REFRESH_TOKEN = "5ccdae726b5cc20a008b71e9|3f1d3d96cb43610f31d50e746e085063"  # Replace with your refresh token

# Netatmo OAuth2 endpoints
AUTH_URL = "https://api.netatmo.com/oauth2/token"
API_URL = "https://api.netatmo.com/api/getstationsdata"

access_token = None
token_expiration_time = None

# Authenticate and get an access token
def get_access_token():
    global access_token, token_expiration_time

    auth_payload = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD,
        "scope": "read_station"
    }

    try:
        response = requests.post(AUTH_URL, data=auth_payload)
        response.raise_for_status()
        data = response.json()
        access_token = data["access_token"]
        expires_in = data["expires_in"]
        token_expiration_time = datetime.now() + timedelta(seconds=expires_in)
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Autentication Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

# Refresh the access token using the refresh token
def refresh_access_token():
    global access_token, token_expiration_time

    refresh_payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }

    try:
        response = requests.post(AUTH_URL, data=refresh_payload)
        response.raise_for_status()
        data = response.json()
        access_token = data["access_token"]
        expires_in = data["expires_in"]
        token_expiration_time = datetime.now() + timedelta(seconds=expires_in)
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Refresh Access Token Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

# Fetch outdoor temperature
def get_netatmoData():
    global access_token, token_expiration_time

    if access_token is None or datetime.now() > token_expiration_time:
        access_token = refresh_access_token()

    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        params = {
            "device_id": DEVICE_ID  # Replace with your device ID
        }

        try:
            response = requests.get(API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            # print("Headers:\n", headers, "\nParams:\n", params, "\nData:\n", data)
            # outdoor_temp = data['body']['devices'][0]['dashboard_data']['Outdoor']['Temperature']
            # outdoor_temp = data["body"]["devices"][0]["modules"][0]["dashboard_data"]["Temperature"]
            return data
        except requests.exceptions.RequestException as e:
            print(f"Get outdoor temperature Error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

if __name__ == "__main__":
    netatmoData = get_netatmoData()

    if netatmoData is not None:
        outdorTimestamp = netatmoData["body"]["devices"][0]["modules"][0]["dashboard_data"]["time_utc"]
        outdoor_temp = netatmoData["body"]["devices"][0]["modules"][0]["dashboard_data"]["Temperature"]
        inhouse_temp = netatmoData["body"]["devices"][0]["dashboard_data"]["Temperature"]
        inhousAndOutdorResult = {
            "time_utc": strftime('%Y-%m-%d %H:%M:%S', localtime(outdorTimestamp)),
            "inhouse": inhouse_temp,
            "outdor": outdoor_temp
        }
        print(inhousAndOutdorResult)
    else:
        print("Failed to fetch outdoor temperature.")
