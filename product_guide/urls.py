from django.urls import path, include
from .views import index, product_base, register, user_login, user_logout, upload_file, change_product_attr, \
    delete_line, save_products
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('', index, name='index'),
    path('product_base', product_base, name='product_base'),
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('upload_file', upload_file, name='upload_file'),
    path('change_product_attr', change_product_attr, name='change_attr'),
    path('delete_line', delete_line, name='delete_line'),
    path('save_products', save_products, name='save_products')
]