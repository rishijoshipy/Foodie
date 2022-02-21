from time import time
import random
from django.conf import settings

from .models import *
from django.db.models import Q

import stripe
stripe.api_key=settings.STRIPE_SECRET_KEY
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
account_sid =settings.TWILLIO_ACCOUNT_SID
auth_token =settings.TWILIO_AUTH_TOKEN

from datetime import  datetime, timedelta

import pytz
utc=pytz.UTC
time=datetime.now()
current_time = time.replace(tzinfo=utc)

def exp_time(now):
    expired = now+timedelta(seconds=120)
    return expired

def exp_time_payment(now):
    expired= now+timedelta(minutes=5)
    return expired


def time_save(cuis):
    for cui in cuis:
        time=datetime.now()
        current_time = time.replace(tzinfo=utc)
        cui.payment_exp_time = exp_time_payment(current_time)
        cui.save()


def success(code,message,dataser):
    return {"code":code,"message":message,"data":dataser}

def unsuccess(code,dataser):
    message = "Data Error...Bad Reuest!"
    return {"code":code,"message":message,"data":dataser}

def success_login(code,message,dataser,access,refresh):
    data = {
        "user" : dataser,
        "access_token":access,
        "refresh_token":refresh
    }
    return {"code":code,"message":message,"data":data}

def success_logout(code,message):
    return {"code":code,"message":message}

def success_price(code,message,dataser,total_price,total_quantity,pay_status):
    data = {
        "user" : dataser,
        "Total_price":total_price,
        "Total_Dishes":total_quantity,
        "Payment_status":pay_status
    }
    return {"code":code,"message":message,"Order_cart":data}

def success_payment_intent(code,message,client_sec,total_quantity,dishes,total_price,status,web_auth):
    data = {

        'clientSecret': client_sec,
        'order_quantity':total_quantity,
        'Order_items':dishes,
        'Total_price':total_price,
        'status':status,
        'auth':web_auth
    }
    return {"code":code,"message":message,"Payment_details":data}

def user_mail_send(subject,message,Email):
    """SEND EMAIL"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [Email, ]
    send_mail(subject, message, email_from, recipient_list)
    print("Email Send")
            

def user_send_sms(message,send_to):
    """SEND SMS"""
    client = Client(account_sid, auth_token) 
    message = client.messages.create(  
                    messaging_service_sid=settings.TWILIO_SERVICE_SID, 
                    body=message,      
                    to=send_to 
                ) 
    print("SMS Send")

def random_number_OTP():
    number_list=[x for x in range(10)]
    code_items=[]
    for i in range(5):
        num=random.choice(number_list)
        code_items.append(num)
    code_string="".join(str(item) for item in code_items)
    numbers=code_string
    return numbers

def dishes_items(cuis):
    dishes=[]   
    for cui in cuis:
            dishe=cui.items.dishe_name
            dishes.append(dishe)
    return dishes

def Calcualte_Price(cuis): 
    prices=[]
    for cui in cuis:
            price=cui.items.dishe_price*cui.quantity
            prices.append(price)
    total_price=sum(prices)
    return total_price

def Calcualte_quantity(cuis):
    quantity=[]
    for cui in cuis:
        quantity.append(cui.quantity)
    total_quantity=sum(quantity)
    return total_quantity

def count_of_order_add(quantity,item):
    dish=dishe.objects.get(Q(id=item))
    dish.count_sold=dish.count_sold+quantity
    dish.save()

def count_of_order_remove(quantity,item):
    dish=dishe.objects.get(Q(id=item))
    dish.count_sold=dish.count_sold-quantity
    dish.save()

def orderstatusactive(cuis,intent):
    for cui in cuis:
        cui.payment_id=intent.id
        cui.order_status="Active"
        cui.save()

def orderstatuspaid(cuis):
    for cui in cuis:
        cui.order_status="Paid"
        cui.save()

def pay_id(intent,cuis):
    for cui in cuis:
        cui.payment_id=intent.id
        cui.save()
        
def orderstatuscance(cuis):
    for cui in cuis:
        cui.order_status="Cancel"
        cui.save()