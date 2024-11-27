from fastapi import FastAPI, Request, HTTPException, APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import datetime
import httpx
import logging

from src.core.config import Config
from src.core.database_setup import get_async_db
from src.db.models.instagram_account import InstagramAccount
from src.bot.instagram_integration.service import (
    get_instagram_page_info,
    get_instagram_access_token,
    get_long_lived_access_token,
    get_instagram_user_info
)

bots_instagram = APIRouter()

# Constants
VERIFY_TOKEN = Config.INSTAGRAM_VERIFY_TOKEN  # Define this in your Config


@bots_instagram.post("/handle_code")
async def handle_code(request: Request, db: AsyncSession = Depends(get_async_db)):
    data = await request.json()
    code = data.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")

    # Exchange the code for a short-lived access token
    access_token_data = get_instagram_access_token(
        Config.INSTAGRAM_APP_ID,
        Config.INSTAGRAM_APP_SECRET,
        Config.INSTAGRAM_REDIRECT_URI,
        code
    )

    if not access_token_data or 'access_token' not in access_token_data:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    short_lived_token = access_token_data['access_token']

    # Exchange for a long-lived access token
    long_lived_token_data = get_long_lived_access_token(
        short_lived_token,
        Config.INSTAGRAM_APP_SECRET
    )
    if not long_lived_token_data or 'access_token' not in long_lived_token_data:
        raise HTTPException(status_code=400, detail="Failed to obtain long-lived access token")

    long_lived_token = long_lived_token_data['access_token']
    expires_in = long_lived_token_data.get('expires_in')  # in seconds

    # Get user info
    user_info = get_instagram_user_info(long_lived_token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to obtain user info")

    instagram_id = user_info.get('id')
    username = user_info.get('username')
    full_name = user_info.get('account_type')  # Adjust according to the fields you have

    # Calculate expiration date
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    # Get page ID and page access token
    page_id, page_access_token = get_instagram_page_info(long_lived_token)
    if not page_id or not page_access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain page info")

    # Save the data into the InstagramAccount model
    result = await db.execute(select(InstagramAccount).filter_by(instagram_id=instagram_id))
    account = result.scalars().first()
    if not account:
        account = InstagramAccount(
            instagram_id=instagram_id,
            username=username,
            full_name=full_name,
            access_token=page_access_token,
            page_id=page_id,
            expires_at=expires_at
        )
        db.add(account)
    else:
        # Update existing account
        account.username = username
        account.full_name = full_name
        account.access_token = page_access_token
        account.page_id = page_id
        account.expires_at = expires_at

    await db.commit()

    return {
        "message": "Integration successful",
        "user_info": user_info,
        "access_token": long_lived_token
    }


# Webhook Verification Endpoint
@bots_instagram.get("/webhook/instagram", response_class=PlainTextResponse)
async def verify_token(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    logging.info(f"Verification request received: mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge  # Return challenge as plain text
    raise HTTPException(status_code=403, detail="Verification token mismatch")

# Webhook Event Handler Endpoint
@bots_instagram.post("/webhook/instagram")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    logging.info(f"Webhook event received: {data}")

    try:
        webhook_event = WebhookObject(**data)
    except Exception as e:
        logging.error(f"Error parsing webhook data: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if webhook_event.object == "instagram":
        for entry in webhook_event.entry:
            page_id = entry.id  # Extract the page_id dynamically

            # Fetch the InstagramAccount associated with this page_id
            account = db.query(InstagramAccount).filter_by(page_id=page_id).first()
            if not account:
                logging.error(f"No InstagramAccount found for page_id: {page_id}")
                continue  # Skip if no account found

            page_access_token = account.access_token  # Use the user's page access token

            for messaging_event in entry.messaging:
                # Skip messages that are echoes
                if messaging_event.message.get("is_echo"):
                    logging.info(f"Skipping echo message: {messaging_event.message}")
                    continue

                sender_id = messaging_event.sender.get("id")
                message_text = messaging_event.message.get("text")

                if message_text:
                    logging.info(f"Received message: {message_text} from {sender_id}")
                    response_message = f"Your message: {message_text}"
                    await send_message(page_access_token, sender_id, response_message)

    return {"status": "success"}


async def send_message(page_token: str, recipient_id: str, message_text: str):
    """
    Sends a message to the customer via Instagram Graph API.
    """
    url = f"https://graph.facebook.com/v16.0/me/messages"
    # Create payload
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }

    # Add access token in params
    params = {
        "access_token": page_token
    }

    # Make POST request to Instagram Graph API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, params=params)
            response.raise_for_status()
            logging.info(f"Message sent successfully to {recipient_id}: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logging.error(f"Request error while sending message: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error while sending message: {e.response.json()}")
