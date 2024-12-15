from product.models import ShoppingCart, Client, UserAccount

def cart_items_count(request):
    """
    Context Processor Name: Contador de elementos en el carrito de compras
    File: context_processors.py
    Author: Berenice Flores Hernández

    Descripción:
        Este contexto procesador calcula y devuelve el número de elementos en el carrito de compras del usuario.
        Si el número total de elementos supera 99, incluye una clave adicional `cart_items_display` con el texto '+99'.

    """
    if not request.session.get('user_id'):
        return {'cart_items_count': 0, 'cart_items_display': '0'}

    try:
        user_account = UserAccount.objects.get(id_user=request.session['user_id'])
        client = Client.objects.get(user=user_account)
        cart_items = ShoppingCart.objects.filter(client=client)
        
        # Sumar las cantidades de productos en el carrito
        count = sum(item.cart_product_quantity for item in cart_items)

        # Manejar la lógica de '+99'
        cart_items_display = '+99' if count > 99 else str(count)

        return {'cart_items_count': count, 'cart_items_display': cart_items_display}
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        return {'cart_items_count': 0, 'cart_items_display': '0'}