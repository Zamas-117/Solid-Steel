from django.shortcuts import render

def index(request):
    """
    Vista que renderiza la página de inicio principal.

    Participantes:
    Cesar Omar Andrade - 215430 

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Renderiza la plantilla `menu/index.html`.

    Returns:
        HttpResponse: Renderiza la página principal `menu/index.html`.
    """ 
    return render(request, 'menu/index.html')  # index principal solid-steel.com
