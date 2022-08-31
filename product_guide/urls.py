from django.urls import path, include
from .views import index, product_base

urlpatterns = [
    path('', index, name='index'),
    path('product_base', product_base, name='product_base')
]