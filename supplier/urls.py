from django.urls import path
from . import views


urlpatterns = [
    path('', views.supplier_menu, name='supplier_menu'),
    path('edit_info/', views.supplier_edit_info, name='supplier_edit_info'),
    path('actualizar-inventario/', views.update_stock, name='update_stock'),
    path('agregar-producto/', views.add_product, name='add_product'),
    path('saldo/', views.saldo_view, name='saldo_view'),  # Vista para mostrar el saldo
    path('saldo/retirar/', views.retirar_saldo, name='saldo_retirar'),  # Vista para retirar saldo
    path('saldo/actualizar/', views.actualizar_datos_retiro, name='saldo_actualizar_datos'),  # Vista para actualizar datos de retiro
    path('todos_movimientos/', views.todos_los_movimientos, name='todos_los_movimientos'),
    path('retiro_saldo/', views.retirar_saldo_view, name='retirar_saldo'),
    path('editar-retiro/', views.add_supplier_payment_method, name='editar_retiro'),
    path('confirmacion-retiro/', views.confirmacion_retiro, name='confirmacion_retiro'),
    path('configurar-datos/', views.configurar_datos, name='configurar_datos'),
    path('cerrar-sesion/', views.log_out, name='log_out'),
    path('delete-product/', views.delete_product, name='delete_product')
]
