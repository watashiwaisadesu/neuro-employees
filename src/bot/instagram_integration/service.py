import requests

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

def get_instagram_page_info(access_token):
    url = "https://graph.facebook.com/v16.0/me/accounts"
    params = {
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get('data')
        if data and len(data) > 0:
            page = data[0]
            return page.get('id'), page.get('access_token')
    else:
        print(f"Error getting page info: {response.status_code}")
        print(response.text)
    return None, None
