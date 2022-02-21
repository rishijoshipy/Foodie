from django.urls import path, include

from django.contrib import admin

from foodapp import views

from rest_framework_simplejwt import views as jv

urlpatterns = [
  path('admin/',admin.site.urls),
    #"""SIGNUp ENDUSER AND OWNER"""
    path('signup',views.UserSignupVIEW.as_view()),
    
    path('Two_Auth',views.User_Two_AuthVIEW.as_view()),
    path('ResendOtp',views.Resend_OtpVIEW.as_view()),

    #LOGIN AND LOGOUT FOR ANY USER
    path('login',views.LoginVIEW.as_view(),name="login"),
    path('logout',views.LogoutVIEW.as_view()),

    #""UPDATE PROFILE""
    path('ownerlogin',views.OwnerDetailsVIEW.as_view()),
    path('enduserlogin',views.EnduserDetailVIEW.as_view()),

    #""Add DISHES by OWNER""
    path('cuisineadd',views.CuisineVIEW.as_view()), 
    path('ownerdisheadd',views.OWnerDishesVIEW.as_view()),

    #""SEARCH DISHES by OWNER AND ENDUSER"" 
    path("searchdish_owner",views.OwnerDishesSearchVIew.as_view()),  
    path("searchdish_enduser",views.EndUserDishesSearchVIew.as_view()),

    #ENDUSER ORDER DETAILS AND PAYMENTS AND RATINGSS
    path('order', views.OrderVIEW.as_view()),
    path("payment",views.PaymentOrder.as_view()),
    path("paymentconfirm",views.PaymentOrder_Confirm.as_view()),
    path('invoice', views.Order_InVoice.as_view()),
    path('foodratings', views.RatingsVIEW.as_view()),#"ratings"

    #""ADMIN PANEL SIGNUP AND MANAGER""
    path('adminsignup',views.AdminUserSign.as_view()),
    path('adminmanager', views.AdminUserManager.as_view()),
    path('admindishesview', views.ADMIN_Dishes_CuisineVIEW.as_view()),
    path('admin_orders', views.ADMIN_Order_OwnerVIEW.as_view()),
   
  ]