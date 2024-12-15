from django.urls import path
from . import views

urlpatterns = [
    path('', views.recycler, name='recycler'),  # Ruta para la página principal
    path('map/', views.recycler_map_view, name='recycler_map'),  # Ruta para la vista del mapa
]
