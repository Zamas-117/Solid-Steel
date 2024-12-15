from django.urls import path
from . import views


urlpatterns = [
    path("", views.mostrar_pagos_view, name="mostrar_pagos"),  # Página de pago
    path("iniciar/", views.iniciar_pago_view, name="iniciar_pago"),
    path("exitoso/", views.pago_exitoso_view, name="pago_exitoso"),
    path("cancelado/", views.pago_cancelado_view, name="pago_cancelado"),# Ruta para la página principal
    path("escojer_metodo/", views.escojer_metodo_view, name="escojer_metodo"),# Ruta para la página principal
    path('create-payout/', views.create_payout, name='create_payout'),
    path("historial-compras/", views.historial_compras_view, name="historial_compras"),
]