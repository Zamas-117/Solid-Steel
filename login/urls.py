from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.client_login, name='client_login'),
    path('supplier/', views.supplier_login, name='supplier_login'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'), 
    path('set_new_password/', views.set_new_password, name='set_new_password'), 
    
]


