from django.urls import path, include
from .views import index, register, user_login, user_logout, upload_file, change_product_attr, \
    delete_line, save_products, download_changed_file, download_nomenclature, save_incoming_invoice, show_products, \
    save_changes

urlpatterns = [
    path('', index, name='index'),
    path('product_base', show_products, name='product_base'),
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('upload_file', upload_file, name='upload_file'),
    path('change_product_attr', change_product_attr, name='change_attr'),
    path('delete_line', delete_line, name='delete_line'),
    path('save_products', save_products, name='save_products'),
    path('download_changed_file', download_changed_file, name='download_changed_file'),
    path('download_nomenclature', download_nomenclature, name='download_nomenclature'),
    path('save_incoming_invoice', save_incoming_invoice, name='save_incoming_invoice'),
    path('save_changes', save_changes, name='save_changes')
]