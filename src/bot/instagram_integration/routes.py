from fastapi import FastAPI, Request, HTTPException, APIRouter
from src.core.config import Config
import requests

bots_instagram = APIRouter()


@bots_instagram.post("/handle_code")
async def handle_code(request: Request):
    data = await request.json()
    code = data.get('code')
    if code:
        # Exchange the code for a short-lived access token
        access_token_data = get_instagram_access_token(
            Config.instagram_app_ID,
            Config.instagram_app_secret,
            Config.instagram_redirect_uri,
            code
        )

        if access_token_data and 'access_token' in access_token_data:
            short_lived_token = access_token_data['access_token']
            # Exchange for a long-lived access token
            long_lived_token_data = get_long_lived_access_token(
                short_lived_token,
                Config.instagram_app_secret
            )
            if long_lived_token_data and 'access_token' in long_lived_token_data:
                long_lived_token = long_lived_token_data['access_token']
                # Get user info
                user_info = get_instagram_user_info(long_lived_token)
                # Save the long-lived token and user info as needed
                # For example, associate it with the bot_name in your database
                # Return success response
                return {
                    "message": "Integration successful",
                    "user_info": user_info,
                    "access_token": long_lived_token
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to obtain long-lived access token")
        else:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
    else:
        raise HTTPException(status_code=400, detail="No code provided")


def get_instagram_access_token(client_id, client_secret, redirect_uri, code):
    url = 'https://api.instagram.com/oauth/access_token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting short-lived access token: {response.status_code}")
        print(response.text)
        return None


def get_long_lived_access_token(short_lived_token, client_secret):
    url = "https://graph.instagram.com/access_token"
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': client_secret,
        'access_token': short_lived_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting long-lived access token: {response.status_code}")
        print(response.text)
        return None


def get_instagram_user_info(access_token):
    url = "https://graph.instagram.com/me"
    params = {
        "fields": "id,username,account_type",
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting user info: {response.status_code}")
        print(response.text)
        return None