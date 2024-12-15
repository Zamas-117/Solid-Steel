from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount, Product, SupplierPaymentMethodModel, Payment, Order, OrderItem
from django.contrib import messages
from .forms import SupplierForm, AgregarProductoForm, ActualizarDatosForm
from django.contrib.auth.decorators import login_required
from supplier.forms import SupplierPaymentMethodForm

def supplier_edit_info(request):
    """
    Permite a un proveedor editar su información personal y de usuario.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante el `supplier_id` en la sesión.
        2. Permite editar datos personales y de usuario, incluyendo la actualización de la contraseña.
        3. Valida y guarda los cambios en la base de datos.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/supplier_edit_info.html` con el formulario prellenado.
    """
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    
    user_id = request.session.get('supplier_id')  # Obtener el ID del usuario desde la sesión
    user = get_object_or_404(UserAccount, pk=user_id)  # Obtener el usuario asociado
    supplier = get_object_or_404(Supplier, user=user)  # Obtener el proveedor asociado con el usuario
    
    if request.method == 'POST':
        # Aquí pasamos la instancia de supplier para asegurarnos de que se actualiza correctamente
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            # Guardar los datos del proveedor directamente desde el formulario
            supplier = form.save()

            # Actualizar los datos del usuario
            user.user_email = form.cleaned_data['user_email']
            
            # Si se ingresó una nueva contraseña, actualízala
            new_password = form.cleaned_data.get('user_password')
            if new_password:
                user.set_password(new_password)  # Encriptar la nueva contraseña
            user.save()  # Guardar los cambios en el usuario
            messages.success(request, 'Se modificaron los datos correctamente', extra_tags='edit')
            return render(request, 'supplier/supplier_edit_info.html', {
        'form': form,
        'supplier': supplier,
        'user': user,
    })  # Redirigir a una página de éxito
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.', extra_tags='edit')
            print(form.errors)  # Verificar si hay errores en el formulario
    else:
        # Inicializar el formulario con los datos del proveedor y del usuario
        form = SupplierForm(initial={
            'user_email': user.user_email,  # Correo electrónico del usuario
            'user_password': '',  # Campo vacío por seguridad
            'supplier_name': supplier.supplier_name,
            'supplier_address': supplier.supplier_address,
            'supplier_state': supplier.supplier_state,
            'supplier_city': supplier.supplier_city,
            'supplier_zip_code': supplier.supplier_zip_code,
        })

    return render(request, 'supplier/supplier_edit_info.html', {
        'form': form,
        'supplier': supplier,
        'user': user,
    })
    
    
    
# Vista de saldo (ya existente)
def saldo_view(request):
    """
    Vista que muestra el saldo acumulado de un proveedor y el resumen de las transacciones relacionadas.
    Integrantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante el `supplier_id` almacenado en la sesión.
        2. Recupera al proveedor autenticado, su método de pago y los productos asociados.
        3. Obtiene todos los `OrderItem` relacionados con los productos del proveedor.
        4. Filtra los pagos exitosos asociados a estas órdenes para crear un resumen de transacciones.
        5. Genera una lista de transacciones con detalles como el nombre del producto, cantidad vendida y monto ganado.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/saldo.html` con:
            - `supplier`: Información del proveedor.
            - `mail`: Método de pago asociado al proveedor.
            - `transactions`: Lista de transacciones con detalles de productos vendidos y ganancias.

    Manejo de errores:
        - Si el `supplier_id` no está en la sesión, redirige al índice con un mensaje de error.

    Dependencias:
        - `Supplier`: Modelo que representa al proveedor.
        - `Product`: Modelo que representa los productos.
        - `OrderItem`: Modelo que representa los ítems de las órdenes.
        - `Payment`: Modelo que representa los pagos.
        - `SupplierPaymentMethodModel`: Modelo que almacena los métodos de pago de los proveedores.
        - `messages`: Para mostrar mensajes flash al usuario.

    Ejemplo de uso:
        - Un proveedor accede a esta vista para consultar sus ganancias y el resumen de ventas relacionadas.
        - Puede ver detalles específicos de cada producto vendido y el monto ganado.

    """
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    # Recupera al usuario y al proveedor asociado
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 

    # Obtiene los productos del proveedor
    supplier_products = Product.objects.filter(supplier=supplier)

    # Obtiene todos los OrderItems relacionados con los productos del proveedor
    order_items = OrderItem.objects.filter(product__in=supplier_products)

    # Filtra los pagos exitosos relacionados con los OrderItems
    payments = Payment.objects.filter(
        order__orderitem__in=order_items,
        payment_status='Exitosa'
    ).distinct()  # Evita duplicados en caso de múltiples OrderItems por orden

    # Crea un resumen de las transacciones
    transactions = []
    for payment in payments:
        # Filtra los OrderItems relacionados con la orden y el proveedor
        order_items_related = order_items.filter(order=payment.order)
        for order_item in order_items_related:
            transactions.append({
                'product_name': order_item.product.product_name,
                'quantity_sold': order_item.quantity,
                'amount_earned': payment.payment_amount,  # Ajustar si el pago es proporcional a los ítems
            })

    return render(request, 'supplier/saldo.html', {
            'supplier': supplier,
            'transactions': transactions
        })



# Vista para retirar saldo
def retirar_saldo(request):
    """
    Redirige a la vista del saldo del proveedor después de una acción de retiro.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista `saldo_view`.
    """
    return redirect('saldo_view')  # Redirige a la vista de saldo después del retiro

# Vista para actualizar datos de retiro
def actualizar_datos_retiro(request):
    """
    Muestra la plantilla para que un proveedor actualice sus datos de retiro.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/actualizar_datos.html`.
    """
    return render(request, 'supplier/actualizar_datos.html')  # Muestra una plantilla para actualizar los datos

def todos_los_movimientos(request):
    """
    Vista que muestra un historial detallado de los movimientos financieros de un proveedor.
    Integrantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante el `supplier_id` en la sesión.
        2. Recupera al proveedor autenticado, su método de pago y los productos asociados.
        3. Obtiene todos los `OrderItem` relacionados con los productos del proveedor.
        4. Filtra los pagos exitosos asociados a estos `OrderItem`.
        5. Genera una lista de transacciones con detalles como:
            - Nombre del producto.
            - Cantidad vendida.
            - Ganancia por artículo.
            - Fecha de la transacción.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/todos_los_movimientos.html` con:
            - `transactions`: Lista de transacciones detalladas.

    Manejo de errores:
        - Si el `supplier_id` no está en la sesión, redirige al índice con un mensaje de error.

    Dependencias:
        - `Supplier`: Modelo que representa al proveedor.
        - `Product`: Modelo que representa los productos.
        - `OrderItem`: Modelo que representa los ítems de las órdenes.
        - `Payment`: Modelo que representa los pagos.
        - `messages`: Para mostrar mensajes flash al usuario.

    Ejemplo de uso:
        - Un proveedor accede a esta vista para consultar todas sus transacciones financieras detalladas.

    """
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    # Recupera al usuario y proveedor asociado
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 
    payment_method = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)

    # Obtiene los productos del proveedor
    supplier_products = Product.objects.filter(supplier=supplier)

    # Obtiene todos los OrderItems relacionados con los productos del proveedor
    order_items = OrderItem.objects.filter(product__in=supplier_products)

    # Filtra los pagos exitosos relacionados con los OrderItems
    payments = Payment.objects.filter(
        order__orderitem__in=order_items,
        payment_status='Exitosa'
    ).distinct()  # Evita duplicados en caso de múltiples OrderItems por orden

    # Crea un resumen de las transacciones
    transactions = []
    for payment in payments:
        order_items_related = order_items.filter(order=payment.order)
        for item in order_items_related:
            transactions.append({
                'product_name': item.product.product_name,
                'quantity_sold': item.quantity,
                'amount_earned': item.price_at_purchase * item.quantity,
                'transaction_date': payment.payment_date,
            })

    return render(request, 'supplier/todos_los_movimientos.html', {'transactions': transactions})

def retirar_saldo_view(request):
    """
    Vista que muestra la página para que un proveedor solicite el retiro de saldo.
    Integrantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante el `supplier_id` en la sesión.
        2. Recupera al proveedor autenticado y su método de pago asociado.
        3. Renderiza una página que muestra el saldo del proveedor y su método de pago.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/retirar_saldo.html` con:
            - `supplier`: Información del proveedor.
            - `pago`: Método de pago asociado al proveedor.

    Manejo de errores:
        - Si el `supplier_id` no está en la sesión, redirige al índice con un mensaje de error.

    Dependencias:
        - `Supplier`: Modelo que representa al proveedor.
        - `SupplierPaymentMethodModel`: Modelo que almacena los métodos de pago de los proveedores.
        - `messages`: Para mostrar mensajes flash al usuario.

    Ejemplo de uso:
        - Un proveedor accede a esta vista para iniciar el proceso de retiro de saldo disponible.

    """
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    
    # Recupera al usuario y proveedor asociado
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 
    supplier_payment = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)

    return render(request, 'supplier/retirar_saldo.html', {'supplier': supplier, 'pago': supplier_payment})

def supplier_menu(request):
    """
    Vista que muestra el menú principal del proveedor, incluyendo una lista de productos asociados.
    Participantes:
    Almanza Quezada Andres Yahir
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante la sesión.
        2. Recupera al usuario y proveedor asociado.
        3. Obtiene la lista de productos que pertenecen al proveedor autenticado.

    Returns:
        HttpResponse: Renderiza la plantilla 'supplier/suppliers_menu.html' con la lista de productos.
    """
    supplier_id = request.session.get('supplier_id')
    
    if supplier_id is None:
        return redirect('index')

    user_id = request.session.get('supplier_id')  
    user = get_object_or_404(UserAccount, pk=user_id)  
    supplier = get_object_or_404(Supplier, user=user)  

    productos = Product.objects.filter(supplier=supplier)

    return render(request, 'supplier/suppliers_menu.html', {'productos': productos})


def update_stock(request):
    """
    Vista que permite a un proveedor actualizar el precio y el stock de sus productos.
    Participantes:
    Almanza Quezada Andres Yahir
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante la sesión.
        2. Recupera al usuario y proveedor asociado.
        3. Si el método es POST:
            - Obtiene el producto mediante `product_id`.
            - Actualiza el precio y/o stock según los datos ingresados.
        4. Renderiza una página con los productos del proveedor.

    Returns:
        HttpResponse: Renderiza la plantilla 'supplier/update_stock.html' con la lista de productos.
    """
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    user_id = request.session.get('supplier_id')  
    user = get_object_or_404(UserAccount, pk=user_id) 
    supplier = get_object_or_404(Supplier, user=user)  
    productos = Product.objects.filter(supplier=supplier)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')  
        product = get_object_or_404(Product, id_product=product_id)  

        new_price = request.POST.get('new_price')
        new_stock = request.POST.get('new_stock')

        if new_price:
            product.product_price = float(new_price)  
        if new_stock:
            product.product_stock = int(new_stock)  

        product.save()  

        return redirect('update_stock')   

    return render(request, 'supplier/update_stock.html', {'productos': productos})


def delete_product(request):
    """
    Vista que permite a un proveedor eliminar un producto.
    Participantes:
    Almanza Quezada Andres Yahir
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica que el método de solicitud sea POST.
        2. Obtiene el producto mediante `product_id` y lo elimina.
        3. Redirige a la vista de actualización de stock.

    Returns:
        HttpResponse: Redirige a la vista 'update_stock' después de eliminar el producto.
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')  
        product = get_object_or_404(Product, id_product=product_id)  
        product.delete() 
        return redirect('update_stock') 


def add_product(request):
    """
    Vista que permite a un proveedor agregar un nuevo producto.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el proveedor está autenticado mediante la sesión.
        2. Si el método es POST:
            - Valida el formulario `AgregarProductoForm`.
            - Asocia el producto al proveedor autenticado y lo guarda.
        3. Si el método no es POST, muestra un formulario vacío.

    Returns:
        HttpResponse: Renderiza la plantilla 'supplier/add_product.html' con el formulario.
    """
    supplier_id = request.session.get('supplier_id')
    
    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    if request.method == 'POST':
        form = AgregarProductoForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            try:
                supplier = Supplier.objects.get(user__id_user=supplier_id)
                product.supplier = supplier  
                product.save()
                messages.success(request, 'Producto agregado correctamente.')
                return redirect('supplier_menu')
            except Supplier.DoesNotExist:
                form.add_error(None, 'No se encontró un proveedor asociado a este usuario.')
    else:
        form = AgregarProductoForm()
    
    return render(request, 'supplier/add_product.html', {'form': form})

def log_out(request):
    """
    Vista que cierra la sesión de un proveedor.
    Participantes:

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Elimina la información de sesión del proveedor.
        2. Muestra un mensaje de éxito.
        3. Redirige al índice.

    Returns:
        HttpResponse: Redirige a la página de inicio después de cerrar la sesión.
    """
    try:
        del request.session['supplier_id']
    except KeyError:
        pass  

    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('index')

from django.contrib import messages

def add_supplier_payment_method(request):
    """
    Vista que permite a un proveedor agregar o actualizar su método de pago para retiros.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Recupera al proveedor autenticado mediante el ID almacenado en la sesión.
        2. Obtiene o crea un registro de método de pago (`SupplierPaymentMethodModel`) asociado al proveedor.
        3. Si el método de solicitud es POST:
            - Valida el formulario `SupplierPaymentMethodForm`.
            - Actualiza o guarda los datos del método de pago.
            - Muestra un mensaje de éxito (nuevo método o actualización).
        4. Si el método no es POST, inicializa un formulario con los datos existentes del método de pago.
        5. Renderiza la plantilla para que el proveedor pueda agregar o editar su método de pago.

    Returns:
        HttpResponse: Renderiza la plantilla 'supplier/editar_retiro.html' con el formulario para agregar o editar el método de pago.

    Manejo de mensajes:
        - Muestra un mensaje de éxito si el método de pago se agrega o actualiza correctamente.

    Dependencias:
        - `Supplier`: Modelo que representa al proveedor.
        - `SupplierPaymentMethodModel`: Modelo que almacena los métodos de pago de los proveedores.
        - `SupplierPaymentMethodForm`: Formulario utilizado para capturar los datos del método de pago.
        - `messages`: Para mostrar mensajes flash al usuario.

    Ejemplo de uso:
        - Un proveedor accede a esta vista para registrar un correo de PayPal asociado a sus retiros.
        - Puede actualizar este método de pago en cualquier momento.

    """
    supplier_id = request.session.get('supplier_id')
    supplier = Supplier.objects.get(user__id_user=supplier_id)

    # Obtiene o crea un método de pago asociado al proveedor
    payment_method, created = SupplierPaymentMethodModel.objects.get_or_create(supplier=supplier)

    if request.method == 'POST':
        form = SupplierPaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            supplier_payment = form.save(commit=False)
            supplier_payment.supplier = supplier
            supplier_payment.save()
            if created:
                messages.success(request, "Metodo de pago agregado correctamente")
            else:
                messages.success(request, "Metodo de pago actualizado correctamente.")
            return redirect('retirar_saldo')  
    else:
        form = SupplierPaymentMethodForm(instance=payment_method)

    return render(request, 'supplier/editar_retiro.html', {'form': form})


def confirmacion_retiro(request):
    """
    Muestra la confirmación de un retiro solicitado por un proveedor.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/confirmacion_retiro.html`.
    """
    return render(request, 'supplier/confirmacion_retiro.html')

@login_required
def configurar_datos(request):
    """
    Permite a un usuario actualizar su configuración personal.

    Participantes:
    Almanza Quezada Andres Yahir 215993

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Si el método es POST, valida y guarda los datos enviados mediante el formulario.
        2. Si no, muestra el formulario prellenado con los datos actuales del usuario.

    Returns:
        HttpResponse: Renderiza la plantilla `supplier/configurar_datos.html` con el formulario.
    """
    if request.method == 'POST':
        form = ActualizarDatosForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('configurar_datos')
    else:
        form = ActualizarDatosForm(instance=request.user)

    return render(request, 'supplier/configurar_datos.html', {'form': form})
