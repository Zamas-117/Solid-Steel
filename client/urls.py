from django.urls import path
from . import views

urlpatterns = [
    path('edit_info/', views.client_edit_info, name='client_edit_info'), # Ruta para modificar la informacion del cliente
    path('client_address/', views.client_address, name='update_client_address'),
]