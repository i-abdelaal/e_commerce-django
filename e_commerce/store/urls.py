from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('picture/', views.picture, name="picture"),
    path('accounts/register/', views.registerPage, name="register"),
    path('accounts/login/', views.loginPage, name="login"),
    path('accounts/logout/', views.logoutPage, name="logout"),
]
