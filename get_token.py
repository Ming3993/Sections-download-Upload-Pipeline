

import msal
import os

SCOPES = ["Files.ReadWrite"]

TOKEN_CACHE_FILE = "token_cache.json"

def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        cache.deserialize(open(TOKEN_CACHE_FILE, "r").read())
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())

def get_access_token(client_id, tenant_id):
    cache = load_cache()
    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache
    )
    
    accounts = app.get_accounts()
    if accounts:
        # Refresh token
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            return result["access_token"]
    
    # Login using device code flow when there is not valid token
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError("Failed to create device flow")
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]
    else:
        raise RuntimeError(f"Failed to get token: {result.get('error_description')}")
