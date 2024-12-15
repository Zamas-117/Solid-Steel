from django.shortcuts import render

# Create your views here.
def recycler(request):
    """
    Template Name: Recycler Finder
    File: recycle.html
    Author: Hugo Abisai Reyes Trejo - 215201
    Description:
        Esta plantilla de Django muestra recicladoras cercanas utilizando Google Maps API y Places API. 
        Permite al usuario interactuar con un mapa dinámico para encontrar centros de reciclaje dentro de un radio configurable. 
        Incluye un modal para mostrar información adicional sobre cada recicladora.

    Características principales:
        - Slider para ajustar el radio de búsqueda.
        - Lista dinámica de recicladoras basada en la ubicación del usuario.
        - Mapa interactivo que centra la ubicación del usuario y permite ver recicladoras.
        - Botón "Ver más" para cargar más resultados en la lista.
        - Modal para mostrar detalles de las recicladoras, incluyendo su ubicación en el mapa.

    Notas:
        - Requiere una clave de API válida para Google Maps y Places API.
        - Los estilos personalizados están en style_recycler.css.
    """
    return render(request, 'recycle.html')

def recycler_map_view(request):
    return render(request, 'map.html')

