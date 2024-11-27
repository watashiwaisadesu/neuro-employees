from src.core.mail_setup import mail, create_message
from asgiref.sync import async_to_sync
from src.core.celery_app_setup import c_app

@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
    print("Email sent")