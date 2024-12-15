from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, WishItem, Client, UserAccount
from functools import wraps
from product.models import UserRole  # Importar UserRole

def user_authenticated_and_role(role):
    """
    Verifica si el usuario está autenticado y tiene el rol adecuado antes de acceder a una vista protegida.

    Participantes:
    Almanza Quezada Andres Yahir - 215993

    Args:
        role (str): El rol requerido para acceder a la vista (por ejemplo, 'Cliente', 'Proveedor').

    Lógica:
        1. Recupera el rol del usuario almacenado en la sesión.
        2. Si el usuario no está autenticado o no tiene el rol requerido:
            - Muestra un mensaje de error.
            - Redirige al login del cliente.
        3. Si el usuario tiene el rol adecuado, permite el acceso a la vista.

    Returns:
        function: Un decorador que protege la vista y verifica los permisos del usuario.

    Ejemplo de uso:
        @user_authenticated_and_role('Proveedor')
        def vista_protegida(request):
            # Lógica de la vista aquí
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if not user_role or user_role != role:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('client_login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Aplicar el decorador en la vista
@user_authenticated_and_role(UserRole.CLIENT)
def product_list(request):
    """
    Vista que muestra una lista de productos con opciones de filtrado, búsqueda y ordenamiento.
    Participantes:
    Cesar Omar Rodarte Andrade
    Berenice Flores Hernandez
    Almanza Quezada Andres Yahir 

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene parámetros de búsqueda y filtros.

    Parámetros GET:
        - q (str): Texto de búsqueda en los nombres de productos.
        - order (str): Criterio de ordenamiento ('asc', 'desc', 'new').
        - thickness (float): Filtra por espesor del producto.
        - category (str): Filtra por material del producto.
        - price_min (float): Filtra por precio mínimo.
        - price_max (float): Filtra por precio máximo.
        - width (float): Filtra por ancho del producto.
        - height (float): Filtra por altura del producto.

    Variables locales:
        - productos (QuerySet): Conjunto de productos disponibles.
        - thicknesses (QuerySet): Lista de espesores únicos ordenados.
        - widths (QuerySet): Lista de anchos únicos ordenados.
        - heights (QuerySet): Lista de alturas únicas ordenadas.

    Lógica:
        1. Obtiene todos los productos disponibles.
        2. Procesa medidas únicas (espesor, ancho, altura) para mostrar filtros dinámicos.
        3. Aplica filtros según los parámetros de búsqueda ingresados por el usuario.
        4. Aplica ordenamiento basado en el parámetro 'order'.
        5. Devuelve la lista de productos filtrados y ordenados al template.

    Returns:
        HttpResponse: Renderiza el template 'product/products_menu.html' con los productos filtrados y sus atributos adicionales.
    """
    # Obtener productos
    productos = Product.objects.all()

    # Obtener y procesar las medidas sin duplicados y ordenadas
    thicknesses = productos.values_list('product_thickness', flat=True).distinct().order_by('product_thickness')
    widths = productos.values_list('product_width', flat=True).distinct().order_by('product_width')
    heights = productos.values_list('product_height', flat=True).distinct().order_by('product_height')

    # Obtener parámetros de búsqueda y orden
    query = request.GET.get('q', '')
    order = request.GET.get('order', '')
    thickness = request.GET.get('thickness', '')
    category = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    width = request.GET.get('width', '')
    height = request.GET.get('height', '')

    # Filtrar productos según búsqueda
    if query:
        productos = productos.filter(product_name__icontains=query)

    # Filtrar por espesor
    if thickness:
        productos = productos.filter(product_thickness=thickness)

    # Filtrar por categoría
    if category:
        productos = productos.filter(product_material=category)

    # Filtrar por precio
    if price_min:
        productos = productos.filter(product_price__gte=price_min)
    if price_max:
        productos = productos.filter(product_price__lte=price_max)

    # Filtrar por ancho
    if width:
        productos = productos.filter(product_width=width)

    # Filtrar por alto
    if height:
        productos = productos.filter(product_height=height)

    # Ordenar productos
    if order == 'asc':
        productos = productos.order_by('product_price')
    elif order == 'desc':
        productos = productos.order_by('-product_price')
    elif order == 'new':
        productos = productos.order_by('-id_product')

    return render(request, "product/products_menu.html", {
        "productos": productos,
        "thicknesses": thicknesses,
        "widths": widths,
        "heights": heights
    })


def product_detail(request, id):
    """
    Vista que muestra los detalles de un producto específico.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El identificador único del producto a mostrar.

    Variables locales:
        - productos_aleatorios (QuerySet): Tres productos seleccionados aleatoriamente.
        - product_info (Product): Información completa del producto solicitado.

    Lógica:
        1. Obtiene el producto solicitado utilizando `id`.
        2. Obtiene tres productos aleatorios para sugerencias relacionadas.
        3. Renderiza la página con los detalles del producto y las sugerencias.

    Returns:
        HttpResponse: Renderiza el template 'product/product_view.html' con la información del producto y sugerencias.
    """
    productos_aleatorios = Product.objects.all().order_by('?')[:3]
    product_info = get_object_or_404(Product, id_product=id)
    return render(request, 'product/product_view.html', {'product_info': product_info, "productos": productos_aleatorios})

def add_to_wishlist(request, product_id):
    """
    Agrega un producto a la lista de deseos del cliente.

    Parámetros:
        - request: Objeto HttpRequest que contiene la información de la solicitud.
        - product_id: ID del producto que se desea agregar a la lista de deseos.

    Proceso:
        1. Valida que la solicitud sea de tipo POST.
        2. Obtiene el producto correspondiente al `product_id`.
        3. Recupera al cliente asociado al usuario en sesión.
        4. Verifica si el producto ya está en la lista de deseos del cliente:
            - Si ya está, muestra un mensaje informativo.
            - Si no está, agrega el producto a la lista de deseos y muestra un mensaje de éxito.
        5. Redirige al detalle del producto.

    Manejo de errores:
        - Si no se encuentra un cliente asociado al usuario en sesión, muestra un mensaje de error.
        - Si la solicitud no es de tipo POST, muestra un mensaje de error.

    Retorno:
        - Redirige al detalle del producto con un mensaje de éxito, información o error.

    Notas:
        - La función utiliza mensajes de Django para informar al usuario sobre el estado de la operación.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id_product=product_id)
        user_id = request.session.get('user_id')
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
        
        if not client:
            messages.error(request, "No se encontró un cliente asociado a tu cuenta.")
            return redirect('product_detail', id=product_id)

        # Verificar si ya está en la lista de deseos
        if WishItem.objects.filter(client=client, product=product).exists():
            messages.info(request, "Este producto ya está en tu lista de favoritos.")
        else:
            WishItem.objects.create(client=client, product=product)
            messages.success(request, "Producto agregado a la lista de favoritos.")

        return redirect('product_detail', id=product_id)

    messages.error(request, "Método no permitido.")
    return redirect('product_detail', id=product_id)


def wishlist(request):
    """
    Muestra la lista de deseos del cliente.

    Parámetros:
        - request: Objeto HttpRequest que contiene la información de la solicitud.

    Proceso:
        1. Recupera al usuario en sesión a través de `user_id` almacenado en la sesión.
        2. Obtiene al cliente asociado al usuario.
        3. Consulta los productos en la lista de deseos del cliente.
        4. Renderiza la plantilla `wishlist.html` con los productos de la lista de deseos.

    Contexto para la plantilla:
        - wishlist_items: Productos que el cliente tiene en su lista de deseos.
        - productos: Lista completa de productos disponibles (opcional).

    Retorno:
        - Renderiza la página de la lista de deseos del cliente (`wishlist.html`).

    Notas:
        - La plantilla debe manejar la visualización de los productos de la lista de deseos.
        - Utiliza `select_related` en la consulta para optimizar la recuperación de productos relacionados.
    """
    user_id = request.session.get('user_id')
    user_account = UserAccount.objects.get(id_user=user_id)
    client = Client.objects.get(user=user_account)
    wishlist_items = WishItem.objects.filter(client=client).select_related('product')
    productos = Product.objects.all()
    return render(request, 'client/wishlist.html', {'wishlist_items': wishlist_items, 'productos': productos})