from celery import Celery
from src.core.mail_setup import mail, create_message
from asgiref.sync import async_to_sync
from src.core.config import Config
import os

c_app = Celery("app")
c_app.conf.broker_url = Config.REDIS_URL
c_app.conf.result_backend = Config.REDIS_URL

c_app.autodiscover_tasks(["src.tasks.email_tasks"])

