from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'), # Ruta para la página principal
    path('<int:id>/', views.product_detail, name= 'product_detail'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'), 
]