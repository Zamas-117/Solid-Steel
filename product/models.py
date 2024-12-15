from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.timezone import now


class UserRole(models.TextChoices):
    """
    Define los roles de usuario disponibles en el sistema.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Choices:
        - SUPPLIER: Representa un proveedor.
        - CLIENT: Representa un cliente.
    """
    SUPPLIER = 'Supplier', 'Supplier'
    CLIENT = 'Client', 'Client'

class UserAuthProvider(models.TextChoices):
    """
    Define los métodos de autenticación de usuario disponibles.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Choices:
        - INTERNAL: Autenticación interna.
        - FACEBOOK: Autenticación con Facebook.
        - IOS: Autenticación en dispositivos iOS.
    """
    INTERNAL = 'Internal', 'Internal'
    FACEBOOK = 'Facebook', 'Facebook'
    IOS = 'iOS', 'iOS'

class PaymentMethod(models.TextChoices):
    """
    Define los métodos de pago disponibles.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Choices:
        - STRIPE: Pago mediante Stripe.
        - PAYPAL: Pago mediante PayPal.
    """
    STRIPE = 'Stripe', 'Stripe'
    PAYPAL = 'Paypal', 'Paypal'

class PaymentStatus(models.TextChoices):
    """
    Representa los estados posibles de un pago.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Choices:
        - COMPLETED: Pago completado.
        - PENDING: Pago pendiente.
        - FAILED: Pago fallido.
    """
    COMPLETED = 'Completed', 'Completed'
    PENDING = 'Pending', 'Pending'
    FAILED = 'Failed', 'Failed'

class SupplierPaymentMethod(models.TextChoices):
    """
    Define los métodos de pago aceptados por los proveedores.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Choices:
        - PAYPAL: Pago mediante PayPal.
        - STRIPE: Pago mediante Stripe.
    """
    PAYPAL = 'Paypal', 'Paypal'
    STRIPE = 'Stripe', 'Stripe'

class UserAccount(models.Model):
    """
    Modelo que representa las cuentas de usuario en el sistema.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_user: Identificador único de usuario.
        - user_email: Correo electrónico del usuario (único).
        - user_password: Contraseña cifrada del usuario.
        - user_role: Rol del usuario (Supplier o Client).
        - user_auth_provider: Método de autenticación utilizado.
        - user_auth_provider_id: ID del proveedor de autenticación externa.
    """
    id_user = models.AutoField(primary_key=True)
    user_email = models.EmailField(max_length=255, unique=True)
    user_password = models.CharField(max_length=255, null=True, blank=True)
    user_role = models.CharField(max_length=20, choices=UserRole.choices)
    user_auth_provider = models.CharField(max_length=20, choices=UserAuthProvider.choices, default=UserAuthProvider.INTERNAL)
    user_auth_provider_id = models.CharField(max_length=255, null=True, blank=True)

    def set_password(self, raw_password):
        """
        Establece la contraseña cifrada del usuario.
        """
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Verifica si una contraseña coincide con la contraseña cifrada del usuario.
        """
        return check_password(raw_password, self.user_password)

    def __str__(self):
        return self.user_email

class Supplier(models.Model):
    """
    Modelo que representa un proveedor en el sistema.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_supplier: Identificador único del proveedor.
        - balance: Saldo actual del proveedor.
        - supplier_name: Nombre del proveedor.
        - supplier_rating: Calificación promedio del proveedor.
        - supplier_address: Dirección del proveedor.
        - supplier_state: Estado del proveedor.
        - supplier_city: Ciudad del proveedor.
        - supplier_zip_code: Código postal del proveedor.
        - user: Relación con el modelo UserAccount (rol Supplier).
    """
    id_supplier = models.AutoField(primary_key=True)
    balance = models.FloatField(default=0.0)
    supplier_name = models.CharField(max_length=50)
    supplier_rating = models.FloatField(default=0)
    supplier_address = models.CharField(max_length=100)
    supplier_state = models.CharField(max_length=50)
    supplier_city = models.CharField(max_length=50)
    supplier_zip_code = models.CharField(max_length=10)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, limit_choices_to={'user_role': UserRole.SUPPLIER})

    def __str__(self):
        return self.supplier_name

class Client(models.Model):
    """
    Modelo que representa un cliente en el sistema.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_client: Identificador único del cliente.
        - user: Relación con el modelo UserAccount (rol Client).
        - client_first_name: Nombre del cliente.
        - client_last_name: Apellido del cliente.
        - client_phone: Teléfono del cliente.
    """
    id_client = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, limit_choices_to={'user_role': UserRole.CLIENT})
    client_first_name = models.CharField(max_length=50)
    client_last_name = models.CharField(max_length=50)
    client_phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.client_first_name} {self.client_last_name}"

class ClientAddress(models.Model):
    """
    Modelo que representa una dirección asociada a un cliente.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_address: Identificador único de la dirección.
        - client: Relación con el modelo Client.
        - client_address: Dirección física del cliente.
        - client_city: Ciudad de la dirección.
        - client_state: Estado de la dirección.
        - client_zip_code: Código postal de la dirección.
        - client_address_additional_information: Información adicional sobre la dirección.
    """
    id_address = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    client_address = models.CharField(max_length=100)
    client_city = models.CharField(max_length=50)
    client_state = models.CharField(max_length=50)
    client_zip_code = models.IntegerField()
    client_address_additional_information = models.CharField(max_length=150)

    def __str__(self):
        return self.client_address


class Product(models.Model):
    """
    Modelo que representa un producto en el sistema.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_product: Identificador único del producto.
        - product_name: Nombre del producto.
        - product_description: Descripción del producto.
        - product_price: Precio del producto (en centavos).
        - product_stock: Cantidad disponible del producto.
        - product_image: Imagen asociada al producto.
        - product_width: Ancho del producto.
        - product_height: Altura del producto.
        - product_thickness: Grosor del producto.
        - product_material: Material del producto.
        - supplier: Relación con el modelo Supplier (proveedor del producto).
    """
    id_product = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_description = models.CharField(max_length=100)
    product_price = models.IntegerField(default=0)
    product_stock = models.IntegerField(default=0)
    product_image = models.ImageField("Product Image", upload_to='media/products_images/', null=False)
    product_width = models.FloatField(default=0)
    product_height = models.FloatField(default=0)
    product_thickness = models.FloatField(default=0)
    product_material = models.CharField(max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

    def get_display_price(self):
        """
        Obtiene el precio del producto en formato decimal.
        """
        return "{0:.2f}".format(self.product_price / 100)


class Order(models.Model):
    """
    Modelo que representa una orden de compra realizada por un cliente.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_order: Identificador único de la orden.
        - client: Relación con el modelo Client.
        - address: Relación con el modelo ClientAddress (dirección de envío).
        - order_date: Fecha en que se realizó la orden.
    """
    id_order = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.ForeignKey(ClientAddress, on_delete=models.CASCADE)
    order_date = models.DateTimeField()

    def __str__(self):
        return f"Order {self.id_order}"


class OrderItem(models.Model):
    """
    Modelo que representa un ítem dentro de una orden.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_order_item: Identificador único del ítem.
        - order: Relación con el modelo Order.
        - product: Relación con el modelo Product.
        - quantity: Cantidad del producto en la orden.
        - price_at_purchase: Precio del producto en el momento de la compra.
    """
    id_order_item = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_purchase = models.FloatField()

    def __str__(self):
        return f"Order Item {self.id_order_item}"

class Shipment(models.Model):
    """
    Modelo que representa un envío asociado a una orden.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_shipment: Identificador único del envío.
        - order: Relación con el modelo Order.
        - shipment_tracking_number: Número de seguimiento del envío.
        - shipment_carrier: Empresa transportadora.
        - shipment_status: Estado actual del envío.
        - shipment_date: Fecha en que se realizó el envío.
        - shipment_estimated_delivery_date: Fecha estimada de entrega.
        - shipment_actual_delivery_date: Fecha real de entrega.
    """
    id_shipment = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipment_tracking_number = models.CharField(max_length=50)
    tracker_id = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    shipment_carrier = models.CharField(max_length=50)
    shipment_status = models.CharField(max_length=50)
    shipment_date = models.DateTimeField()
    shipment_estimated_delivery_date = models.DateTimeField()
    shipment_actual_delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipment {self.id_shipment}"
    
class TrackingEvent(models.Model):
    
    """
    Model Name: TrackingEvent
    File: models.py
    Author: Berenice Flores Hernández

    Descripción:
        Este modelo registra eventos de seguimiento de envíos asociados a una expedición específica.
        Cada evento captura el estado del envío, la fecha y hora de ocurrencia, y detalles opcionales.

    Campos:
        - shipment: ForeignKey que relaciona el evento con un envío específico mediante el modelo Shipment.
        - status: CharField para almacenar el estado del evento (por ejemplo, "En tránsito", "Entregado").
        - occurrence_datetime: DateTimeField que indica cuándo ocurrió el evento.
        - details: TextField opcional para almacenar detalles adicionales del evento.
        - milestone: CharField opcional para almacenar un hito específico del estado del envío.

    Métodos:
        - __str__: Retorna una representación legible del objeto, mostrando el estado y la fecha y hora del evento.

    Notas:
        - Este modelo se utiliza para registrar eventos específicos de seguimiento de envíos.
        - Es crucial para integrar con APIs externas como Ship24 para sincronizar eventos de estado del envío.

    """
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=50)
    occurrence_datetime = models.DateTimeField()
    details = models.TextField(null=True, blank=True)  # Para almacenar detalles adicionales
    milestone = models.CharField(max_length=50, null=True, blank=True)  # Para statusMilestone

    def __str__(self):
        return f"Evento {self.status} - {self.occurrence_datetime}"
    
class HistorialCompras(models.Model):
    
    """
    Model Name: HistorialCompras
    File: models.py
    Author: Berenice Flores Hernández

    Descripción:
        Este modelo registra el historial de compras de un cliente, detallando cada transacción realizada.
        Cada entrada incluye el cliente asociado, nombre del producto, cantidad comprada, precio unitario,
        total de la compra y fecha de pago.

    Campos:
        - client: ForeignKey que relaciona la compra con un cliente específico mediante el modelo Client.
        - product_name: CharField para almacenar el nombre del producto comprado.
        - quantity: IntegerField para indicar la cantidad comprada del producto.
        - price: FloatField para el precio unitario del producto en la transacción.
        - total: FloatField para el monto total de la compra.
        - payment_date: DateTimeField que indica cuándo se realizó el pago de la compra.

    Métodos:
        - __str__: Retorna una representación legible del objeto, mostrando el cliente y la fecha de pago del historial.

    Notas:
        - Este modelo es esencial para mantener un registro histórico de todas las compras realizadas por cada cliente.
        - Facilita análisis y seguimiento de patrones de compra y comportamiento del cliente a lo largo del tiempo.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()
    payment_date = models.DateTimeField()

    def __str__(self):
        return f"Historial de {self.client} - {self.payment_date}"

class Payment(models.Model):
    """
    Modelo que representa un pago realizado por un cliente.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_payment: Identificador único del pago.
        - order: Relación con el modelo Order.
        - payment_method: Método de pago utilizado.
        - payment_amount: Monto del pago.
        - payment_date: Fecha en que se realizó el pago.
        - payment_status: Estado del pago (completado, pendiente, fallido).
        - app_user: Relación con el modelo Client (usuario que realizó el pago).
        - payment_bool: Indicador booleano del estado del pago.
        - stripe_checkout_id: ID de la sesión de pago en Stripe.
        - customer_email: Correo electrónico del cliente.
    """
    id_payment = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    app_user = models.ForeignKey(Client, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    customer_email = models.EmailField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id_payment}"


class ShoppingCart(models.Model):
    """
    Modelo que representa un carrito de compras.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_cart: Identificador único del carrito.
        - client: Relación con el modelo Client.
        - product: Relación con el modelo Product.
        - cart_product_quantity: Cantidad del producto en el carrito.
        - cart_added_date: Fecha en que se agregó el producto al carrito.
    """
    id_cart = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_product_quantity = models.IntegerField(default=1)
    cart_added_date = models.DateTimeField()

    def __str__(self):
        return f"Cart {self.id_cart}"


class WishItem(models.Model):
    """
    Modelo que representa un producto en la lista de deseos de un cliente.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_wish: Identificador único del ítem.
        - client: Relación con el modelo Client.
        - product: Relación con el modelo Product.
        - wish_date_added: Fecha en que se agregó el ítem a la lista de deseos.
    """
    id_wish = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    wish_date_added = models.DateTimeField(default=now)

    def __str__(self):
        return f"Wish {self.id_wish}"


class PasswordReset(models.Model):
    """
    Modelo que representa un proceso de restablecimiento de contraseña.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_reset: Identificador único del restablecimiento.
        - user: Relación con el modelo UserAccount.
        - reset_code: Código de restablecimiento generado.
        - reset_expiration_time: Fecha y hora de expiración del código.
    """
    id_reset = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=10)
    reset_expiration_time = models.DateTimeField()

    def __str__(self):
        return f"Password Reset {self.id_reset}"

class SupplierPaymentMethodModel(models.Model):
    """
    Modelo que representa los métodos de pago de un proveedor.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_supplier_payment: Identificador único del método de pago.
        - supplier: Relación uno a uno con el modelo Supplier.
        - supplier_payment_method: Método de pago del proveedor (ejemplo: PayPal).
        - supplier_payment_email: Correo electrónico asociado al método de pago.
        - supplier_payment_name: Nombre del titular asociado al método de pago.
    """
    id_supplier_payment = models.AutoField(primary_key=True)
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='payment_methods')
    supplier_payment_method = models.CharField(
        max_length=20,
        choices=[('PayPal', 'PayPal')]
    )
    supplier_payment_email = models.EmailField(max_length=100)
    supplier_payment_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Supplier Payment {self.id_supplier_payment} - {self.supplier_payment_method}"
    
class SupplierSales(models.Model):
    """
    Modelo que representa las ventas totales de un proveedor.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - Supplier_order_sales: Identificador único de las ventas.
        - supplier: Relación uno a uno con el modelo Supplier.
        - total_sales: Total de ventas acumuladas del proveedor.
    """
    Supplier_order_sales = models.AutoField(primary_key=True)
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)
    total_sales = models.FloatField(default=0)

    def __str__(self):
        return f"Supplier Sales {self.Supplier_order_sales}"

class Recycle(models.Model):
    """
    Modelo que representa un ítem reciclable.
    Participantes:
    Andres Yahir Almanza Quezada 215993
    Attributes:
        - id_recycle: Identificador único del ítem reciclable.
        - recycle_name: Nombre del ítem reciclable.
        - recycle_image: Imagen representativa del ítem reciclable.
        - recycle_description: Descripción del ítem reciclable.
        - recycle_address: Dirección asociada al ítem reciclable.
        - recycle_number: Número de contacto para el reciclaje.
    """
    id_recycle = models.AutoField(primary_key=True)
    recycle_name = models.CharField(max_length=255)
    recycle_image = models.ImageField("Recycle Image", upload_to='static/products_images/', null=False)
    recycle_description = models.CharField(max_length=255)
    recycle_address = models.CharField(max_length=255)
    recycle_number = models.CharField(max_length=20)

    def __str__(self):
        return self.recycle_name
