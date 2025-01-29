import requests,os,json
from dotenv import load_dotenv

load_dotenv()
pesapal_url="https://cybqa.pesapal.com/pesapalv3/api"

# paypal authentication
def authentication():
    url = f"{pesapal_url}/Auth/RequestToken"
    payload = json.dumps({
    "consumer_key": os.getenv("consumer_key"),
    "consumer_secret": os.getenv("consumer_secret")
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

#  register IPN URL
def registerIPNURL(auth_response,payment_id):
    url = f"{pesapal_url}/URLSetup/RegisterIPN"
    payload = json.dumps({
        "url": f"https://e3b7-105-163-2-186.ngrok-free.app/payment/{payment_id}",
        "ipn_notification_type": "POST"
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    "Authorization":f"Bearer {auth_response['token']}"
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# Get my IPNURls
def getUrls(auth_response):
    url = f"{pesapal_url}/URLSetup/GetIpnList"
    payload={}
    headers = {
        "Authorization":f"Bearer {auth_response['token']}"
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

# Submit order request
def submit_order(ipn_id,auth_response,order_id,amount):
    url=f"{pesapal_url}/Transactions/SubmitOrderRequest"
    payload = json.dumps({
        "id": order_id,
        "currency": "KES",
        "amount": amount,
        "description": "Payment for invoice",
        "callback_url": " https://e3b7-105-163-2-186.ngrok-free.app",
        "notification_id": ipn_id,
        "branch": "Store Name - HQ",
        "billing_address": {
            "email_address": "example@gmail.com",
            "phone_number": "",
            "country_code": "KE",
            "first_name": "John",
            "middle_name": "",
            "last_name": "Doe",
            "line_1": "Pesapal Limited",
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": ""
    }
    })
    headers = {
    'Content-Type': 'application/json',
    "Authorization":f"Bearer {auth_response['token']}"
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# check transaction status
def check_transaction(tracking_id):
    url = f"{pesapal_url}/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}"
    payload={}
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    "Authorization": f"Bearer {authentication()['token']}"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()
