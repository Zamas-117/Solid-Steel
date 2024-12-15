from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipping, name='shipping'), # Ruta para la página principal
    path('shipping_actualizar_datos/', views.shipping_actualizar_datos, name='shipping_actualizar_datos'), # Ruta para la página principal
    path('paid-orders/', views.paid_orders, name='paid_orders'),  # URL para pedidos pagados
    path('tracking/<str:tracking_number>/', views.shipment_tracking_info, name='shipment_tracking_info'),
    path('webhook/ship24/', views.ship24_webhook, name='ship24_webhook'),
]