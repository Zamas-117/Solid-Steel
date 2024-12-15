from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from product.models import Product, ShoppingCart, UserAccount, Client, Payment, Order, ClientAddress, OrderItem
from product.models import HistorialCompras
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
import stripe
import time
from django.http import JsonResponse 
import pandas as pd
from pay import views
import logging

logger = logging.getLogger(__name__)

# Vista para mostrar el carrito
def cart(request):
    """
    Vista que maneja el carrito de compras de un cliente, incluyendo la creación de una sesión de pago con Stripe.
    Participantes:
    Berenice Flores Hernandez
    Andres Yahir Almanza Quezada
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el usuario está autenticado mediante el ID almacenado en la sesión.
        2. Obtiene el cliente asociado al usuario autenticado.
        3. Recupera los ítems del carrito del cliente y calcula el total.
        4. Si el método es POST, crea una sesión de pago con Stripe y redirige al usuario a la URL de pago.
        5. Si no, renderiza la plantilla del carrito.

    Returns:
        HttpResponse: Renderiza la plantilla 'cart/cart.html' con los ítems del carrito y el total,
        o redirige a la página de inicio de sesión o a la URL de pago de Stripe.
    """
    # Obtener el ID del usuario desde la sesión
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('login')
    
    # Obtener items del carrito solo para este cliente
    carrito_items = ShoppingCart.objects.filter(client=client)
    total = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
    
    # Contar la cantidad total de productos en el carrito
    cart_count = sum(item.cart_product_quantity for item in carrito_items)

    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    if request.method == 'POST':
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {'name': 'Carrito de compras'},
                    'unit_amount': int(total * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_creation='always',
            success_url=settings.REDIRECT_DOMAIN + '/cart/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.REDIRECT_DOMAIN + '/cart/payment_cancelled',
        )

        return redirect(checkout_session.url, code=303)
    
    # Pasar `cart_count` al contexto
    return render(request, 'cart/cart.html', {'carrito_items': carrito_items, 'total': total, 'cart_count': cart_count})


def stripe_webhook(request):
    """
    Webhook que maneja eventos de Stripe relacionados con pagos.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP con el evento de Stripe.

    Lógica:
        1. Verifica y construye el evento de Stripe usando la firma.
        2. Si el evento es 'checkout.session.completed', actualiza el estado del pago asociado al `session_id`.

    Returns:
        HttpResponse: Respuesta con estado HTTP 200 para confirmar que el evento fue procesado.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        time.sleep(15)
        user_payment = Payment.objects.get(stripe_checkout_id=session_id)
        user_payment.payment_bool = True
        user_payment.save()

    return HttpResponse(status=200)


def payment_successful(request):
    """
    Vista que maneja el éxito de un pago realizado con Stripe.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Cesar Omar Andrade - 215430
    
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Recupera la sesión de Stripe y obtiene el correo del cliente.
        2. Crea una nueva orden y registra los ítems en la base de datos.
        3. Crea un registro del pago asociado a la orden.
        4. Limpia el carrito del cliente y renderiza la página de éxito.

    Returns:
        HttpResponse: Renderiza la plantilla 'cart/success.html' con los detalles del pago.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)


    
    customer_email = session.get('customer_email', None)
    user_id = request.session.get('user_id')
    user_account = UserAccount.objects.get(id_user=user_id)
    client = Client.objects.get(user=user_account)


    carrito_items = ShoppingCart.objects.filter(client=client)
    subtotal = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
    total = subtotal


    transaction_id = session.payment_intent
    payment_date = timezone.now()
    payment_method = "Stripe"


    address = ClientAddress.objects.filter(client=client).first()
    order = Order.objects.create(
        client=client,
        address=address,
        order_date=payment_date
    )

    historial_compras = []  # Lista para guardar los registros del historial
    with transaction.atomic():
        for item in carrito_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.cart_product_quantity,
                price_at_purchase=item.product.product_price
            )
            supplier = item.product.supplier
            supplier.balance += item.product.product_price * item.cart_product_quantity
            supplier.save()
            
            # Registrar el historial de compras
            historial_compras.append(HistorialCompras(
                client=client,
                product_name=item.product.product_name,
                quantity=item.cart_product_quantity,
                price=item.product.product_price,
                total=item.product.product_price * item.cart_product_quantity,
                payment_date=payment_date
            ))

            
            # Registrar el envío para cada producto
            views.registrar_rastreador_y_envio(order, client, item)
        
        # Guardar el historial de compras
        HistorialCompras.objects.bulk_create(historial_compras)


    Payment.objects.create(
        order=order,
        payment_method=payment_method,
        payment_amount=total,
        payment_status="Exitosa",
        app_user=client,
        stripe_checkout_id=checkout_session_id,
        payment_bool=True,
        customer_email=customer_email
    )

    ShoppingCart.objects.filter(client=client).delete()
    
    return render(request, 'cart/success.html', {
        'transaction_id': transaction_id,
        'payment_date': payment_date,
        'payment_method': payment_method,
        'subtotal': f"{subtotal:.2f}",
        'total': f"{total:.2f}",
        'status': "Exitosa",
        'customer_email': customer_email
    })

def payment_cancelled(request):
    """
    Vista que maneja la cancelación de un pago realizado con Stripe.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'cart/cancel.html'.
    """
    return render(request, 'cart/cancel.html')



# Vista para agregar productos al carrito
def agregar_al_carrito(request, id):
    """
    View Name: agregar_al_carrito
    File: views.py
    Author: Berenice Flores Hernández

    Descripción:
        Esta vista permite agregar productos al carrito de compras de un cliente.
        Verifica la sesión del usuario, obtiene el producto y cliente asociados, y gestiona la cantidad
        de productos en el carrito. También verifica el stock disponible del producto.

    Parámetros:
        - request: La solicitud HTTP recibida.
        - id: El ID del producto a agregar al carrito.

    Acciones:
        - Verifica si el usuario está autenticado.
        - Recupera el producto y el cliente asociado al usuario.
        - Crea o actualiza el item en el carrito con la cantidad especificada.
        - Verifica el stock disponible del producto antes de agregarlo al carrito.

    Retorna:
        - Redirecciona a la página del carrito después de agregar el producto.

    """
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('product_detail', id=id)

    producto = get_object_or_404(Product, id_product=id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Obtener o crear el item en el carrito, asegurando que esté asociado al cliente específico
    cart_item, created = ShoppingCart.objects.get_or_create(
        client=client,
        product=producto,
        defaults={'cart_product_quantity': 0, 'cart_added_date': timezone.now()}
    )

    cantidad_total = cart_item.cart_product_quantity + cantidad
    if cantidad_total > producto.product_stock:
        messages.error(request, f"No hay suficiente stock de {producto.product_name}. Solo quedan {producto.product_stock - cart_item.cart_product_quantity} unidades.")
        return redirect('product_detail', id=id)

    # Actualizar cantidad sin modificar el stock del producto en la base de datos
    cart_item.cart_product_quantity = cantidad_total
    cart_item.save()
    return redirect('cart')

# Vista para restar una unidad de un producto del carrito
def restar_del_carrito(request, id):
    """
    View Name: restar_del_carrito
    File: views.py
    Author: Berenice Flores Hernández

    Descripción:
        Esta vista permite restar una unidad de un producto específico del carrito de compras de un cliente.
        Verifica la sesión del usuario, obtiene el cliente asociado y gestiona la cantidad de productos en el carrito.

    Parámetros:
        - request: La solicitud HTTP recibida.
        - id: El ID del producto a restar del carrito.

    Acciones:
        - Verifica si el usuario está autenticado.
        - Recupera el cliente asociado al usuario.
        - Actualiza la cantidad del producto en el carrito o elimina el item si la cantidad es cero.

    Retorna:
        - Redirecciona a la página del carrito después de restar el producto.

    """
    user_id = request.session.get('user_id')

    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    cantidad = int(request.POST.get('cantidad', 1))

    if carrito_item.cart_product_quantity > cantidad:
        carrito_item.cart_product_quantity -= cantidad
        carrito_item.save()
    else:
        carrito_item.delete()
    return redirect('cart')


# Vista para eliminar productos del carrito
def eliminar_del_carrito(request, id):
    """
    View Name: eliminar_del_carrito
    File: views.py
    Author: Berenice Flores Hernández

    Descripción:
        Esta vista permite eliminar un producto específico del carrito de compras de un cliente.
        Verifica la sesión del usuario, obtiene el cliente asociado y elimina el producto del carrito.

    Parámetros:
        - request: La solicitud HTTP recibida.
        - id: El ID del producto a eliminar del carrito.

    Acciones:
        - Verifica si el usuario está autenticado.
        - Recupera el cliente asociado al usuario y elimina el item correspondiente del carrito.

    Retorna:
        - Redirecciona a la página del carrito después de eliminar el producto.

    """
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    carrito_item.delete()
    return redirect('cart')
