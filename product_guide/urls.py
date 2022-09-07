from django.urls import path, include
from .views import index, product_base, register, user_login, user_logout, upload_file
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('', index, name='index'),
    path('product_base', product_base, name='product_base'),
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('upload_file', upload_file, name='upload_file')
]