from django.urls import path, include
from .views import index, product_base

urlpatterns = [
    path('', index),
    path('product_base', product_base)
]