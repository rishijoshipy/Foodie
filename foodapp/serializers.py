from rest_framework import serializers, status
from foodapp.models import *
from rest_framework.validators import UniqueValidator
from foodapp.utility import success,unsuccess
from django.db.models import Q
import random

"""Signup or Register Enduser/Owneruser"""
class UserRegisterSerializer(serializers.ModelSerializer):
    
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    name = serializers.CharField(required=True,min_length=4,max_length=50)
    last_name = serializers.CharField(required=True,min_length=4,max_length=50)
    is_enduser=serializers.BooleanField(required=True)
    is_owner=serializers.BooleanField(required=True)
    password = serializers.CharField(required=True,min_length=6,write_only= True)
    confirm_password = serializers.CharField(required=True,write_only= True)
    
    class Meta:
        model= CustomUser
        fields = ('email','name','last_name','is_enduser','password','confirm_password','is_owner','is_auth','county_code','mob_number')
    
    def create(self, validated_data):
        password = validated_data['password']  
        num = self.context["number"]
        time=self.context["time"]
        user=CustomUser.objects.create_user(email=validated_data['email'],
                                    name=validated_data['name'],
                                    last_name=validated_data['last_name'],
                                    is_enduser=validated_data['is_enduser'],
                                    is_owner=validated_data['is_owner'],
                                    is_auth=validated_data['is_auth'],
                                    number=num,
                                    otp_expiry_time=time,
                                    mob_number=validated_data['mob_number'],
                                    county_code=validated_data['county_code']
                                    )
        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        email=data.get('email')
        name =  data.get('name')
        last_name = data.get('last_name')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not email[0].isalpha():
            raise serializers.ValidationError({"email" : ["Enter a valid email address."]})

        if name == last_name:
            raise serializers.ValidationError({"last_name": ["Name and LastName shouldn't be same."]})
        
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password":["Those passwords don't match."]})

        return data

"""TWO-auth Verify"""
class VerifySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("is_verify","number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)        
        instance.is_verify = validated_data.get('is_verify', instance.is_verify)
        instance.save()
        return instance

"""Resend OTP"""
class ResendOTPSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=("number","otp_expiry_time",)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.otp_expiry_time = validated_data.get('otp_expiry_time', instance.otp_expiry_time)
        instance.save()
        return instance

"""Owner User update res_name,city,res_address"""
class OwneruserSerializer(serializers.ModelSerializer):
     
    class Meta:
        model=CustomUser
        fields=('email','restaurant_name','city','restaurant_address')

    def update(self, instance, validated_data):
        instance.restaurant_name = validated_data.get('restaurant_name', instance.restaurant_name)
        instance.city = validated_data.get('city', instance.city)
        instance.restaurant_address = validated_data.get('restaurant_address', instance.restaurant_address)
        instance.save()
        return instance

"""End User update dob,city,address"""
class EnduserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=('dob','city','address')

    def update(self, instance, validated_data):
        instance.dob = validated_data.get('dob', instance.dob)
        instance.city = validated_data.get('city', instance.city)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance

"""Cuisine ADD,UPDATE,DELETE Serializer by Owner"""
class CuisineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Cuisine
        fields=("id","cuisine_name",)

    def create(self, validated_data):
        user = self.context["user"]
        return Cuisine.objects.create(user=user,**validated_data)

    def update(self, instance, validated_data):
        instance.cuisine_name = validated_data.get('cuisine_name', instance.cuisine_name)
        instance.save()
        return instance

    def delete(self,instance):
        instance.delete()

    def validate(self, data):
        name = data['cuisine_name']
        if name:
            return super().validate(data)
        
        raise serializers.ValidationError('required name')

"""DISHES ADD,UPDATE,DELETE Serializer by Owner"""
class DishesSerializer(serializers.ModelSerializer):
    class Meta:
        model=dishe
        #fields="__all__"
        fields=('id','cuisine','dishe_name','dishe_price')

    def create(self, validated_data):
        user = self.context["user"]
        return dishe.objects.create(user=user,**validated_data)

    def update(self, instance, validated_data):
        instance.cuisine = validated_data.get('cuisine', instance.cuisine)
        instance.dishe_name = validated_data.get('dishe_name', instance.dishe_name)
        instance.dishe_price = validated_data.get('dishe_price', instance.dishe_price)
        instance.count_sold = validated_data.get('count_sold', instance.dishe_price)

        instance.save()
        return instance

    def delete(self,instance):
        instance.delete()
    
    def validate(self, data):
        cuisine = data['cuisine']
        users = self.context["user"]
        matchs = Cuisine.objects.filter(Q(user__email=users))
        print(matchs)
        if matchs:
            for match in matchs:
                if match==cuisine:
                    print(match)
                    return super().validate(data)

        raise serializers.ValidationError('This cuisine do not exit in this owner')

"""Search DISHES BY OWNER / ENDUSER"""
class SerchSerializer(serializers.ModelSerializer):
    user=OwneruserSerializer()
    cuisine=CuisineSerializer()

    class Meta:
        model=dishe
        fields="__all__"

"""ADMIN SIGNUP"""
class AdminUserRegisterSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    name = serializers.CharField(required=True,min_length=4,max_length=50)
    last_name = serializers.CharField(required=True,min_length=4,max_length=50)
    password = serializers.CharField(required=True,min_length=6,write_only= True)
    confirm_password = serializers.CharField(required=True,write_only= True)
    
    class Meta:
        model= CustomUser
        fields = ('email','name','last_name','password','confirm_password')

    def validate(self, data):
        email=data.get('email')
        name =  data.get('name')
        last_name = data.get('last_name')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not email[0].isalpha():
            raise serializers.ValidationError({"email" : ["Enter a valid email address."]})

        if name == last_name:
            raise serializers.ValidationError({"last_name": ["Name and LastName shouldn't be same."]})
        
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password":["Those passwords don't match."]})

        return data
        
    def create(self, validated_data):
        password = validated_data['password']
        user=CustomUser.objects.create_superuser(email=validated_data['email'],
                                    password = validated_data['password'],
                                    name=validated_data['name'],
                                    last_name=validated_data['last_name'],
                                    )
        user.set_password(password)
        user.save()
        return user


"""ORDER Serializer create,delete"""
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Order
        fields=("items","quantity")

    def create(self, validated_data):
        user = self.context["user"]
        #price=self.context["price"]
        time=self.context["time"]
        return Order.objects.create(user=user,payment_exp_time=time,**validated_data)#price=price

    def update(self, instance, validated_data):
        instance.items = validated_data.get('items', instance.items)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.created_on = validated_data.get('created_on', instance.created_on)
        instance.save()
        return instance

    def delete(self,instance):
        instance.delete()

"""USer Order detail serializer"""
class OrderdetailSerializer(serializers.ModelSerializer):
    
    #items=SerchSerializer()

    class Meta:
        model=Order
        fields="__all__"

"""Payment Method Serializer"""
class PaymentMethodSerializer(serializers.Serializer):
    card_number=serializers.CharField(required=True)
    exp_month= serializers.CharField(required=True)
    exp_year= serializers.CharField(required=True)
    cvc= serializers.CharField(required=True)

"""ADMIN MANAGER---- USER ---UPDATE,DELETE SERIALIZER"""
class AdminUserManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= CustomUser
        fields = ("email","name","last_name","is_owner","is_enduser","restaurant_name","city","restaurant_address","dob","address")
    
    def update(self, instance, validated_data):

        user = self.context["email"]
        print(user.is_enduser)
        print(user.is_owner)
        instance.is_owner = validated_data.get('is_owner', instance.is_owner)
        instance.is_enduser = validated_data.get('is_enduser', instance.is_enduser)
   
        instance.name = validated_data.get('name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
 
        if user.is_owner:
            instance.restaurant_name = validated_data.get('restaurant_name', instance.restaurant_name)
            instance.city = validated_data.get('city', instance.city)
            instance.restaurant_address = validated_data.get('restaurant_address', instance.restaurant_address)
            
        elif user.is_enduser:
            instance.dob = validated_data.get('dob', instance.dob)
            instance.city = validated_data.get('city', instance.city)
            instance.address = validated_data.get('address', instance.address)
        
        instance.save()
        return instance

    def delete(self,instance):
        instance.delete()

"""Ratings serializer"""
class RatingsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Order
        fields=("ratings",)

    def update(self, instance, validated_data):
        instance.ratings = validated_data.get('ratings', instance.ratings)
        instance.save()
        return instance
