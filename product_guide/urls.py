from django.urls import path, include
from .views import index, product_base, register, login
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('', index, name='index'),
    path('product_base', product_base, name='product_base'),
    path('register', register, name='register'),
    path('login', LoginView.as_view, name='login')
]