import hashlib
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Пример запроса для оплаты
class PaymentRequest(BaseModel):
    amount: float  # Сумма платежа в KZT
    order_id: str  # Уникальный идентификатор заказа


# API-ключи CloudPayments
MERCHANT_ID = "your_merchant_id"
SECRET_KEY = "your_secret_key"
PAYMENT_URL = "https://api.cloudpayments.kz/"


# Создание платежа
@app.post("/create-payment/")
async def create_payment(payment_request: PaymentRequest):
    params = {
        'MerchantId': MERCHANT_ID,
        'Amount': payment_request.amount * 100,  # В CloudPayments сумма передается в копейках
        'OrderId': payment_request.order_id,
        'Currency': 'KZT',
        'ReturnUrl': 'https://neuro-employees.com/success',  # Страница успеха
        'FailUrl': 'https://neuro-employees.com/fail',  # Страница неудачи
    }

    # Формируем подпись
    signature = generate_signature(params)
    params['Signature'] = signature

    # Отправка запроса на создание платежа
    response = requests.post(f"{PAYMENT_URL}/payments/cards/charge", json=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Payment creation failed")

    return response.json()

@app.post("/payment-status/")
async def payment_status(data: dict):
    # Пример получения данных из уведомления
    payment_status = data.get('Status')
    order_id = data.get('OrderId')

    if payment_status == "Success":
        # Обработка успешного платежа
        return {"status": "success", "order_id": order_id}
    else:
        # Обработка ошибки платежа
        return {"status": "failed", "order_id": order_id}



# Функция для генерации подписи
def generate_signature(params):
    sign_string = "&".join([f"{key}={value}" for key, value in sorted(params.items())]) + SECRET_KEY
    return hashlib.md5(sign_string.encode()).hexdigest().upper()


