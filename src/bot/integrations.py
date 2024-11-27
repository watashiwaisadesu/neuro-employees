from src.core.config import Config
from urllib.parse import urlencode

# src/integrations/telegram_integration.py
class TelegramIntegration:
    @staticmethod
    async def create_bot(bot_name: str) -> str:
        """
        Заглушка для интеграции с Telegram.
        """
        return f"telegram_fake_token_for_{bot_name}"


# src/integrations/whatsapp_integration.py
class WhatsAppIntegration:
    @staticmethod
    async def create_bot(bot_name: str) -> str:
        """
        Заглушка для интеграции с WhatsApp.
        """
        return f"whatsapp_fake_token_for_{bot_name}"

class InstagramIntegration:
    @staticmethod
    async def create_bot(bot_uid: str) -> dict:
        base_url = "https://www.instagram.com/oauth/authorize"
        query_params = {
            "enable_fb_login": 0,
            "force_authentication": 1,
            "client_id": Config.INSTAGRAM_APP_ID,
            "redirect_uri": Config.INSTAGRAM_REDIRECT_URI,  # Ensure this matches the registered URI
            "response_type": "code",
            "scope": "instagram_business_basic,"
                     "instagram_business_manage_messages,"
                     "instagram_business_manage_comments,"
                     "instagram_business_content_publish",
            "state": bot_uid  # Add the `state` parameter here
        }
        encoded_params = urlencode(query_params, safe=",")
        auth_url = f"{base_url}?{encoded_params}"
        return {"authorization_url": auth_url}

