import re
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from django.db.models import Q

from .serializers import *

from .utility import *

from .permissions import *

import stripe
stripe.api_key=settings.STRIPE_SECRET_KEY

from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout

from datetime import  datetime, timedelta
"""User registrations API with Two_AUTH On/OFF"""
class UserSignupVIEW(APIView):
    def get(self, request, format=None):  
        Emp1 = CustomUser.objects.all()
        serializer = UserRegisterSerializer(Emp1, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data=request.data
        email = request.data['email']
        password = request.data['password']
        num=random_number_OTP()
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        otp_expiry_time = exp_time(current_time)
        serializer = UserRegisterSerializer(data=data,context={"number":num,"time":otp_expiry_time})
        if serializer.is_valid():
            serializer.save()
            print("User Created SuccessFully")
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)        
        User_data=CustomUser.objects.get(email=email)
        user = authenticate(email=email, password=password)
        if user:
            token_pair = TokenObtainPairSerializer()
            refresh = token_pair.get_token(user)
            access = refresh.access_token
            auth_login(request,user)
            if User_data.is_auth:
                otp=User_data.number
                username=User_data.name+" "+User_data.last_name
                send_to=User_data.county_code+User_data.mob_number
                Email=User_data.email
                subject = "Greetingsss...."
                message =f'Hi {username},Thank you for Registrations.'+"\n"+ f'Here your ID :"{user}" and OTP:"{otp}".'
                print(message)
                #user_mail_send(subject,message,Email)
                #user_send_sms(message,send_to)
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "User Signup and Two-Factor is Apply SuccessFully(OTP send throught MAIL,SMS)", serializer.data,str(access),str(refresh)),code)      
            else:
                code = status.HTTP_201_CREATED
                return Response(success_login(code, "User Signup and Two-Factor is Off", serializer.data,str(access),str(refresh)),code)
        else:
            return Response("user not found")

"""USer TWo-auth"""
class User_Two_AuthVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):  
        Emp1 = CustomUser.objects.all()
        serializer = UserRegisterSerializer(Emp1, many=True)
        return Response(serializer.data)
    
    def patch(self,request,format=None):
        user=request.user
        user_otp=request.data["OTP"]
        code=CustomUser.objects.get(email=user)
        if code.is_auth:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            if current_time < code.otp_expiry_time:
                gen_otp=code.number
                if user_otp==gen_otp:
                    data={"number":"","is_verify":"True"}
                    serializer = VerifySerializer(code,data=data,context={'user':request.user},partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        subject="User Activations"
                        username=code.name +" "+ code.last_name
                        message=f'{username} is Verified Successfully'
                        send_to=code.county_code+code.mob_number
                        Email=code.email
                        #user_mail_send(subject,message,Email)
                        #user_send_sms(message,send_to)
                        code = status.HTTP_200_OK
                        return Response(success(code,"User Verified Successfully",serializer.data),code)
                    else:    
                        code = status.HTTP_404_NOT_FOUND
                        return Response(unsuccess(code,serializer.errors),code)
                else:
                    return HttpResponse("Wrong OTP")
            else:
                return Response("OTP Expire")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""OTP Resend"""
class Resend_OtpVIEW(APIView):
    permission_classes = [IsAuthenticated,]

    def patch(self,request,format=None):        
        user=request.user
        if user.is_auth:
            num=random_number_OTP()
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            T_time = exp_time(current_time)
            code=CustomUser.objects.get(email=user)
            if current_time > code.otp_expiry_time:
                data={"number":num,"otp_expiry_time":T_time}
                serializer = ResendOTPSerializer(code,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                else: 
                    code = status.HTTP_404_NOT_FOUND
                    return Response(unsuccess(code,serializer.errors),code)
                number=code.number
                subject="Resend OTP"
                message=f'Resend OTP:{number}'
                Email=code.email
                send_to=code.county_code+code.mob_number
                #user_mail_send(subject,message,Email)
                #user_send_sms(message,send_to)
                code = status.HTTP_200_OK
                return Response(success(code,"OTP Resend Successfully",serializer.data),code)
            else:
                return Response("Try Afer Some Time")
        else:
            code = status.HTTP_200_OK
            return Response(success(code, "Two-Factor-Auth not Avaliable ",user),code)

"""USer Login API"""
class LoginVIEW(APIView):
    
    def post(self,request,format=None):
        data = request.data
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        print(user)
        if user:
            token_pair = TokenObtainPairSerializer()
            refresh = token_pair.get_token(user)
            access = refresh.access_token
            auth_login(request,user)
            code = status.HTTP_200_OK
            return Response(success_login(code, "Login SuccessFull", data,str(access),str(refresh)),code)
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"Fail"),code)

"""User logout API"""
class LogoutVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        auth_logout(request)
        code = status.HTTP_200_OK
        return Response(success_logout(code, "Logout SuccessFull"))
        

"""Restorent Owner Profile Update"""
class OwnerDetailsVIEW(APIView):
    permission_classes = [IsAuthenticated,Res_ownerAuthenticationPermission]
    def get(self, request, format=None):
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        serializer = OwneruserSerializer(user1)
        return Response(serializer.data)

    def patch(self, request, format=None):
        data = request.data
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        print(user1)
        serializer = OwneruserSerializer(user1,data=data,context={'user':request.user},partial=True)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "Owner details added",serializer.data),code)
        else:    
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)
        
"""ENduser Profile update"""
class EnduserDetailVIEW(APIView):
    permission_classes = [IsAuthenticated,EnduserAuthenticationPermission]
    
    def get(self, request, format=None):
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        serializer = EnduserSerializer(user1)
        return Response(serializer.data)

    def patch(self, request, format=None):
        data = request.data
        user=request.user
        user1 = CustomUser.objects.get(email=user)
        serializer = EnduserSerializer(user1,data=data,context={'user':request.user},partial=True)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "End-User details added",serializer.data),code)
        else:   
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)


"""Cuisine View By Owner Create,Update,delete"""
class CuisineVIEW(APIView):
    permission_classes = (IsAuthenticated,Res_ownerAuthenticationPermission)
    
    def get(self, request, format=None):
        user=request.user
        cui = Cuisine.objects.filter(user=user)
        serializer = CuisineSerializer(cui,many=True)
        return Response(serializer.data)      

    def post(self, request,format=None):
        user =request.user 
        data = request.data
        serializer = CuisineSerializer(data=data,context={'user':user})
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "cuisine added",serializer.data),code)
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)
    
    def patch(self, request, format=None):
        data = request.data
        user=request.user
        u_id=request.data['id']
        cui = Cuisine.objects.filter(Q(user=user) & Q(id=u_id))
        if cui:
            user1=Cuisine.objects.get(id=u_id)
            serializer = CuisineSerializer(user1,data=data,context={'user':request.user},partial=True)
            if serializer.is_valid():
                serializer.save()
                code = status.HTTP_200_OK
                return Response(success(code, "Cuisine details updated",serializer.data),code)
            else:
                code = status.HTTP_404_NOT_FOUND
                return Response(unsuccess(code,serializer.errors),code)
        else:
            return Response("cuisine not found")

    def delete(self, request, format=None):
        try:
            stu = Cuisine.objects.get(id=request.data['id'])
            stu.delete()
            code=status.HTTP_204_NO_CONTENT
            return Response(success(code,"Data deleted successfully!","null"),code)
        except:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"null"),code)

"""Restorent Dishes By Owner create,update,delete"""
class OWnerDishesVIEW(APIView):
    permission_classes = (IsAuthenticated,Res_ownerAuthenticationPermission)
    def get(self, request, format=None): 
        user=request.user
        dishes = dishe.objects.filter(Q(user=user))
        serializer = DishesSerializer(dishes, many=True)
        return Response(serializer.data)      

    def post(self, request):
        data = request.data
        serializer = DishesSerializer(data=data,context={'user':request.user})
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "dish added successfully",serializer.data),code)
        else:   
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)

    def patch(self, request, format=None):
        data = request.data
        user1 = dishe.objects.get(id=request.data['id'])
        serializer = DishesSerializer(user1,data=data,context={'user':request.user},partial=True)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "Dishe details updated",serializer.data),code)
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)

    def delete(self, request, format=None):
        try:
            stu = dishe.objects.get(id=request.data['id'])
            stu.delete()
            code=status.HTTP_204_NO_CONTENT
            return Response(success(code,"Data deleted successfully!","null"),code)
        except:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"null"),code)

"""Search Dishes by Owner"""
class OwnerDishesSearchVIew(APIView):
    permission_classes = (IsAuthenticated,Res_ownerAuthenticationPermission)
    
    def get(self, request, format=None):  
        dishes = dishe.objects.all().order_by('-count_sold')[3:]        
        best_dishes= dishe.objects.all().order_by('-count_sold')[:3]
        serializer = SerchSerializer(dishes ,many=True)
        best_serializer = SerchSerializer(best_dishes ,many=True)
        data={"Best Dishes":best_serializer.data,"common Dishes":serializer.data}
        return Response(data)
    
    def post(self, request,format=None):
        searched = request.data['searched']
        best_dish= dishe.objects.filter(Q(dishe_name=searched)|Q(user__restaurant_name=searched)|Q(user__city=searched)).order_by('-count_sold')[:3]
        normal_dish= dishe.objects.filter(Q(dishe_name=searched)|Q(user__restaurant_name=searched)|Q(user__city=searched)).order_by('-count_sold')[3:]
        best_serializer = SerchSerializer(best_dish,many=True)
        serializer = SerchSerializer(normal_dish,many=True)
        data={"Best Dishes":best_serializer.data,"common Dishes":serializer.data}
        return Response(data)

"""search dishes by Enduser GET-BEST Selling dish & Common dish """
class EndUserDishesSearchVIew(APIView):
    permission_classes = (IsAuthenticated,EnduserAuthenticationPermission)
    def get(self, request, format=None):
        dishes = dishe.objects.all().order_by('-count_sold')[3:]        
        best_dishes= dishe.objects.all().order_by('-count_sold')[:3]
        serializer = SerchSerializer(dishes ,many=True)
        best_serializer = SerchSerializer(best_dishes ,many=True)
        data={"Best Dishes":best_serializer.data,"common Dishes":serializer.data}
        return Response(data)

    def post(self, request,format=None):
        searched = request.data['searched']
        best_dish= dishe.objects.filter(Q(dishe_name=searched)|Q(user__restaurant_name=searched)|Q(user__city=searched)).order_by('-count_sold')[:3]
        normal_dish= dishe.objects.filter(Q(dishe_name=searched)|Q(user__restaurant_name=searched)|Q(user__city=searched)).order_by('-count_sold')[3:]
        best_serializer = SerchSerializer(best_dish,many=True)
        serializers = SerchSerializer(normal_dish,many=True)
        data={"Best Dishes":best_serializer.data,"common Dishes":serializers.data}
        return Response(data)

"""Order VIEW GET and POST"""
class OrderVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user=request.user
        cui = Order.objects.filter(Q(user=user) and Q(order_status=None)).order_by("created_on")
        serializer = OrderdetailSerializer(cui,many=True)
        return Response(serializer.data)      

    def post(self, request,format=None):
        user =request.user 
        print(user)
        data = request.data
        print(data)
        time = datetime.now()
        current_time = time.replace(tzinfo=utc)
        payment_exp_time = exp_time_payment(current_time)
        serializer = OrderSerializer(data=data,context={'user':user,"time":payment_exp_time})
        if serializer.is_valid():
            serializer.save()
            quantity=serializer.data["quantity"]
            item=serializer.data["items"]
            count_of_order_add(quantity,item)
            code = status.HTTP_200_OK
            return Response(success(code, "order added Successfull",serializer.data),code)
        else:   
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)

    def patch(self,request,format=None):
        data = request.data
        user=request.user
        user1 = Order.objects.filter(Q(user=user) and Q(order_status=None)).get(id=request.data['id'])
        if user1: 
            serializer = OrderSerializer(user1,data=data,context={'user':request.user},partial=True)
            if serializer.is_valid():
                serializer.save()
                code = status.HTTP_200_OK
                return Response(success(code, "Order details updated",serializer.data),code)
            else:
                code = status.HTTP_404_NOT_FOUND
                return Response(unsuccess(code,serializer.errors),code)
        else:
            return Response("Order id not Found")
            
    def delete(self, request, format=None):
        user=request.user
        stu = Order.objects.filter(Q(user=user) and Q(order_status=None)).get(id=request.data['id'])
        if stu:
            items=stu.items
            quantity=stu.quantity
            count_of_order_remove(quantity,items)
            stu.delete()
            code=status.HTTP_204_NO_CONTENT
            return Response(success(code,"Order Data deleted successfully!","null"),code)
        else:
            return Response("order id not found")

"""Payment--->Create Customer,Payment method,Payment Intent"""
class PaymentOrder(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):  
        user=request.user
        cui=Order.objects.filter(Q(user=user) and Q(order_status="Active")).order_by("payment_exp_time")
        serializer = OrderdetailSerializer(cui,many=True)
        return Response(serializer.data)      

    def post(self,request):
        user=request.user
        data=request.data
        card_number= request.data['card_number']
        exp_month= request.data['exp_month']
        exp_year= request.data['exp_year']
        cvc= request.data['cvc']
        currencys= request.data['currency']
        cuis=Order.objects.filter(Q(user=user) and Q(order_status=None)).order_by("payment_exp_time")
        serializer = PaymentMethodSerializer(data=data)
        if cuis:
            dishes=dishes_items(cuis)   
            total_price=Calcualte_Price(cuis)
            total_quantity=Calcualte_quantity(cuis)
            if serializer.is_valid():
                stripe_customers=stripe.Customer.list(email=user.email).data
                if len(stripe_customers)==0:
                    stripe_customer = stripe.Customer.create(email=user.email,name=user.name+user.last_name,)
                else:
                    stripe_customer=stripe_customers[0]
                stripe_payments=stripe.PaymentMethod.list(customer=stripe_customer,type="card").data
                if len(stripe_payments)==0:
                    cards={"number": card_number,"exp_month": exp_month,"exp_year": exp_year,"cvc": cvc,}
                    details={"email": user.email,"name": user.name,}
                    payment_method = stripe.PaymentMethod.create(type="card",card=cards,billing_details=details,)
                    stripe_payment_method=stripe.PaymentMethod.attach(payment_method,customer=stripe_customer,)
                else:
                    stripe_payment_method=stripe_payments[0]
                """Create a PaymentIntent with the order amount"""
                intent = stripe.PaymentIntent.create(amount=total_price*100,currency=currencys,customer=stripe_customer,payment_method= stripe_payment_method)
                """Confirm Payment for customer and it will give multiple payments"""
                payment_intent_confirm = stripe.PaymentIntent.confirm(intent.id)
                """Confirm payment link js"""
                web_auth=payment_intent_confirm.next_action.use_stripe_sdk.stripe_js
                time_save(cuis)
                orderstatusactive(cuis,payment_intent_confirm)
                pay_id(payment_intent_confirm,cuis)
                username=user.name+user.last_name
                Email=user.email
                subject = "Your Order Confirmations link"
                message =f'Hi {username},Please Confirm payment...'+"\n"+ f'Here your Confirmations Order link:"{web_auth}".'
                print(message)
                #user_mail_send(subject,message,Email)
                code = status.HTTP_200_OK
                return Response(success_payment_intent(code,"Payment Intent Details:",str(payment_intent_confirm.client_secret),str(total_quantity),dishes,str(payment_intent_confirm.amount/100),str(payment_intent_confirm.status),str(web_auth)),code)
            else:
                code = status.HTTP_404_NOT_FOUND
                return Response(unsuccess(code,serializer.errors),code)
        else:
            return Response("Order not Found,Please Add...")

import time as t
"""Payment--->Payment Intent Retrieve,Cancel/Cofirm"""
class PaymentOrder_Confirm(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user=request.user
        cui=Order.objects.filter(Q(user=user) and Q(order_status="Paid")).order_by("payment_exp_time")
        serializer = OrderdetailSerializer(cui,many=True)
        return Response(serializer.data)      

    def post(self,request):
        user=request.user
        payment=request.data["Payment"]
        cuis=Order.objects.filter(Q(user=user) and Q(order_status="Active")).order_by("payment_exp_time")
        print(cuis)
        data=[]
        for cui in cuis:
            data.append(cui.payment_exp_time)
            data.append(cui.payment_id)
        print(data)
        if cuis:
            time = datetime.now()
            current_time = time.replace(tzinfo=utc)
            intent=stripe.PaymentIntent.retrieve(data[1],)
            if payment=="cancel":
                    if current_time<data[0]:
                        stripe.PaymentIntent.cancel(intent.id)
                        orderstatuscance(cuis)
                        return Response("Payment and Status Cancel Successfully")
                    else:
                        return Response("Time Expired for Canceling")
            elif payment=="confirm":
                while intent.status!="succeeded":

                    intent=stripe.PaymentIntent.retrieve(data[1],)
                    print(intent.status)
                    print("payment not succeeded")
                    
                    if current_time<data[0]:
                        if intent.status=="succeeded":
                            break
                    else:
                        stripe.PaymentIntent.cancel(intent.id)
                        print("payment cancel due to time....")
                        orderstatuscance(cuis)
                        return Response("Payment Session Expired")
                    t.sleep(60)
            
                orderstatuspaid(cuis)
                username=user.name+user.last_name
                Email=user.email
                subject = "Your Order Confirmations link"
                message =f'Hi {username},Thank you for Ordering.'+"\n"+ f'Here your Order Id:"{intent.id}".'
                print(message)
                #user_mail_send(subject,message,Email)
                return Response("Payment Succeessfully,Thank you.")
            else:
                #stripe.PaymentIntent.cancel(intent.id)
                return Response("enter correct choice:cancel/confirm")
        else:
            return Response("Order's not getting")
            
"""Order Invioce Details of payments"""
class Order_InVoice(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None): 
        user=request.user
        cuis=Order.objects.filter(Q(user=user) and Q(order_status="Paid")).order_by("payment_exp_time")
        total_price=Calcualte_Price(cuis)
        or_status="Paid"
        total_quantity=Calcualte_quantity(cuis)
        serializer = OrderdetailSerializer(cuis,many=True,context={"user":user})
        code = status.HTTP_200_OK
        return Response(success_price(code, "Food order Receipts", serializer.data,str(total_price),str(total_quantity),str(or_status)),code)

"""Food Ratings VIEW--->Retrieve and add ratings to the Food."""
class RatingsVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None): 
        user=request.user
        cuis=Order.objects.filter(Q(user=user))
        print(cuis)
        serializer = RatingsSerializer(cuis,many=True,context={"user":user})
        code = status.HTTP_200_OK
        return Response(success(code, "YOUR food order list ", serializer.data),code)

    def patch(self,request,format=None):
        data = request.data
        user=request.user
        try:
            user1 = Order.objects.filter(Q(user=user)).get(id=request.data["id"])
            print(user1)
            if user1:
                serializer = RatingsSerializer(user1,data=data,context={'user':user},partial=True)
                if serializer.is_valid():
                    serializer.save()
                    code = status.HTTP_200_OK
                    return Response(success(code, "User give Ratings To the food from 0 to 5 star.",serializer.data),code)
                else:
                    code = status.HTTP_404_NOT_FOUND
                    return Response(unsuccess(code,serializer.errors),code)
        except:
            return Response("order id not found")

"""Admin User Signup"""
class AdminUserSign(APIView):
    def get(self, request, format=None):  
        Emp1 = CustomUser.objects.all()
        serializer = AdminUserRegisterSerializer(Emp1, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data=request.data
        serializer = AdminUserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_201_CREATED
            return Response(success(code, "Admin Created", serializer.data),code)
        code = status.HTTP_404_NOT_FOUND
        return Response(unsuccess(code,serializer.errors),code)     

"""ADMIN MANAGER FOR OWNER/ENDUSER GET,UPDATE,DELETE,SEARCH"""
class AdminUserManager(APIView):
    permission_classes = (IsAuthenticated,adminuserAuthenticationPermission)
    def get(self, request, format=None):  
        user=request.user
        Emp1 = CustomUser.objects.all()
        serializer = AdminUserManagerSerializer(Emp1,many=True,context={'request': request})
        return Response(serializer.data)

    def post(self, request,format=None):
        searched = request.data['searched']
        if searched=="admin":
            isadmin= CustomUser.objects.filter(Q(is_superuser=True))
            serializers = AdminUserManagerSerializer(isadmin,many=True)
            return Response(serializers.data)
        elif searched=="owner":
            isowner= CustomUser.objects.filter(Q(is_owner=True) & Q(is_superuser=False))
            serializers = AdminUserManagerSerializer(isowner,many=True)
            return Response(serializers.data)
        elif searched=="enduser":
            isenduser= CustomUser.objects.filter(Q(is_enduser=True) & Q(is_superuser=False))
            serializers = AdminUserManagerSerializer(isenduser,many=True)
            return Response(serializers.data)

    def patch(self, request, format=None):
        data = request.data
        email=request.data['email']
        user1 = CustomUser.objects.get(email=email)
        serializer = AdminUserManagerSerializer(user1,data=data,context={'user':request.user,"email":user1},partial=True)
        if serializer.is_valid():
            serializer.save()
            code = status.HTTP_200_OK
            return Response(success(code, "details updated",serializer.data),code)
        else:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,serializer.errors),code)

    def delete(self, request, format=None):
        try:
            stu = CustomUser.objects.get(email=request.data['email'])
            stu.delete()
            code=status.HTTP_204_NO_CONTENT
            return Response(success(code,"Data deleted successfully!","null"),code)
        except:
            code = status.HTTP_404_NOT_FOUND
            return Response(unsuccess(code,"null"),code)

"""ADMIN MANAGER Dishes/Cuisine GET,UPDATE,DELETE"""
class ADMIN_Dishes_CuisineVIEW(APIView):
    permission_classes = (IsAuthenticated,adminuserAuthenticationPermission)
    def get(self, request, format=None):
        searched=request.data["searched"]
        if searched=="dishes":
            email=request.data["email"]
            dishes= dishe.objects.filter(Q(user__email=email))
            print(dishes)
            serializer = DishesSerializer(dishes,many=True)
            return Response(serializer.data) 
        elif searched=="cuisine" :
            email=request.data["email"]
            cuisines= Cuisine.objects.filter(Q(user__email=email))
            print(cuisines)
            serializer = CuisineSerializer(cuisines,many=True)
            return Response(serializer.data) 

"""ADMIN or Owner MANAGER ORDER VIEW"""
class ADMIN_Order_OwnerVIEW(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user=request.user
        if user.is_owner:
            order=Order.objects.filter(Q(items__user=user))
            print(order)
            serializer = OrderdetailSerializer(order,many=True)
            return Response(serializer.data)
        elif user.is_superuser:
            data=request.data['email']
            user=CustomUser.objects.filter(Q(email=user) and Q(is_enduser=True))
            serializer = OrderdetailSerializer(user,many=True)
            return Response(serializer.data)
        else:
            return Response("not found")