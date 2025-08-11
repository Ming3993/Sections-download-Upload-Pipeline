import requests
import urllib.parse

# Your access_token get from get_access_token function

def get_item_id(folder_path, access_token):
    encoded_path = urllib.parse.quote(folder_path)
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{encoded_path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.json()["id"]
