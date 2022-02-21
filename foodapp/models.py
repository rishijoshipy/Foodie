from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    dob = models.DateField(null=True)
    city =models.CharField(max_length=50,  blank=True,null=True)
    address = models.TextField(null=True)
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_enduser=models.BooleanField(default=False)
    is_owner=models.BooleanField(default=False)

    """restorent owner details"""
    restaurant_name=models.CharField(max_length=100,null=True)
    city=models.CharField(max_length=100,null=True)
    restaurant_address=models.CharField(max_length=100,null=True)
    
    """user order details"""
    dishes=models.CharField(max_length=100,null=True)
    cuisines=models.CharField(max_length=100,null=True)

    """User TWO-Auth"""
    is_auth=models.BooleanField(default=False)
    is_verify=models.BooleanField(default=False)
    
    mob_number=models.CharField(max_length=10,null=True)
    county_code=models.CharField(max_length=3,null=True)

    number = models.CharField(max_length=5,blank=True)#OTP
    otp_expiry_time = models.DateTimeField(null=True)

    payment_exp_time=models.DateTimeField(null=True)
    
    """user login as email"""
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    def get_email(self):
        return self.email
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'

class Cuisine(models.Model):

    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cuisine_name=models.CharField(max_length=100,null=True)

    def __str__(self):
        return str(self.cuisine_name)

class dishe(models.Model):

    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    cuisine=models.ForeignKey(Cuisine, on_delete=models.CASCADE)
  
    dishe_name=models.CharField(max_length=100)
    dishe_price=models.IntegerField()

    count_sold=models.IntegerField(default=0)

    def __str__(self):
        return self.dishe_name

class Order(models.Model):
    
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ForeignKey(dishe,on_delete=models.CASCADE)

    created_on = models.DateTimeField(null=True)

    quantity=models.IntegerField(default=1)

    ratings=models.IntegerField(null=True)
    payment_id=models.CharField(max_length=30,null=True)

    order_status=models.CharField(max_length=10,null=True)
    payment_exp_time=models.DateTimeField(null=True)

    

    def __str__(self):
        return str(self.items)





