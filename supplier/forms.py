from django import forms
from product.models import Supplier, Product, SupplierPaymentMethodModel


class SupplierForm(forms.ModelForm):
    """
    Formulario para gestionar información básica de un proveedor.

    Campos:
        - user_email: Email del usuario asociado al proveedor.
        - user_password: Contraseña del usuario (opcional).
        - supplier_name: Nombre de la empresa proveedora.
        - supplier_address: Dirección de la empresa.
        - supplier_state: Estado donde se encuentra la empresa.
        - supplier_city: Ciudad donde se encuentra la empresa.
        - supplier_zip_code: Código postal de la empresa.

    Notas:
        - Este formulario incluye campos adicionales no presentes en el modelo `Supplier` (email y password).
    """
    user_email = forms.EmailField()
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False  # No requerido, solo si desean cambiar la contraseña
    )

    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_state', 'supplier_city', 'supplier_zip_code']

        
        


class SupplierPaymentMethodForm(forms.ModelForm):
    """
    Formulario para gestionar métodos de pago del proveedor.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Campos:
        - supplier_payment_method: Método de pago (ej. PayPal).
        - supplier_payment_email: Correo asociado al método de pago.
        - supplier_payment_name: Nombre asociado al método de pago.

    Notas:
        - Las etiquetas (`labels`) personalizan cómo se muestran los nombres de los campos en la interfaz.
    """
    class Meta:
        model = SupplierPaymentMethodModel
        fields = ['supplier_payment_method', 'supplier_payment_email', 'supplier_payment_name']
        labels = {
            'supplier_payment_method': 'Payment Method',
            'supplier_payment_email': 'PayPal Email',
            'supplier_payment_name': 'PayPal Account Name'
        }

from django.contrib.auth.models import User
class ActualizarDatosForm(forms.ModelForm):
    """
    Formulario para actualizar los datos básicos de un usuario.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Campos:
        - first_name: Nombre del usuario.
        - last_name: Apellido del usuario.
        - email: Correo electrónico del usuario.

    Notas:
        - Basado en el modelo `User` proporcionado por Django.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AgregarProductoForm(forms.ModelForm):
    """
    Formulario para agregar o editar un producto.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Campos:
        - product_name: Nombre del producto.
        - product_description: Descripción del producto.
        - product_price: Precio del producto.
        - product_stock: Cantidad disponible en inventario.
        - product_image: Imagen del producto.
        - product_width: Ancho del producto.
        - product_height: Alto del producto.
        - product_thickness: Grosor del producto.
        - product_material: Material del producto (opciones predefinidas).

    Validaciones personalizadas:
        - product_name: Máximo 50 caracteres.
        - product_description: Máximo 100 caracteres.
        - product_price: Entre 0.01 y 9999.
        - product_stock: Entre 1 y 9999.
        - product_width, product_height, product_thickness: Entre 0.01 y 9999.
        - product_image: Solo formatos JPG y PNG.

    Notas:
        - Las opciones para el campo `product_material` están predefinidas como una lista de tuplas.
        - Los widgets se usan para estilizar los campos en el frontend.
    """
    MATERIAL_CHOICES = [
        ('Metal', 'Metal'),
        ('Acero', 'Acero'),
        ('Aluminio', 'Aluminio'),
        ('Bronce', 'Bronce'),
    ]

    product_material = forms.ChoiceField(
        choices=MATERIAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control cantidad'})
    )

    class Meta:
        model = Product
        fields = [
            'product_name', 'product_description', 'product_price', 'product_stock',
            'product_image', 'product_width', 'product_height', 'product_thickness', 'product_material'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control cantidad'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control cantidad', 'rows': 1}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_stock': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control cantidad'}),
            'product_width': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_height': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
            'product_thickness': forms.NumberInput(attrs={'class': 'form-control cantidad'}),
        }
        labels = {
            'product_name': 'Nombre del Producto',
            'product_description': 'Descripción del Producto',
            'product_price': 'Precio',
            'product_stock': 'Cantidad en Inventario',
            'product_image': 'Imagen del Producto',
            'product_width': 'Ancho del Producto',
            'product_height': 'Alto del Producto',
            'product_thickness': 'Grosor del Producto',
            'product_material': 'Material del Producto',
        }

    def clean_product_name(self):
        name = self.cleaned_data.get('product_name')
        if len(name) > 50:
            raise forms.ValidationError("El nombre del producto no puede tener más de 50 caracteres.")
        return name

    def clean_product_description(self):
        description = self.cleaned_data.get('product_description')
        if len(description) > 100:
            raise forms.ValidationError("La descripción debe ser menor a 100 caracteres.")
        return description

    def clean_product_price(self):
        price = self.cleaned_data.get('product_price')
        if price <= 0 or price > 9999:
            raise forms.ValidationError("El precio debe ser mayor a 0 y no exceder 9999.")
        return price

    def clean_product_stock(self):
        stock = self.cleaned_data.get('product_stock')
        if stock <= 0 or stock > 9999:
            raise forms.ValidationError("La cantidad en inventario debe ser mayor a 0 y no exceder 9999.")
        return stock

    def clean_product_width(self):
        width = self.cleaned_data.get('product_width')
        if width < 0.01 or width > 9999:
            raise forms.ValidationError("El ancho debe ser al menos 0.01 y no exceder 9999.")
        return width

    def clean_product_height(self):
        height = self.cleaned_data.get('product_height')
        if height < 0.01 or height > 9999:
            raise forms.ValidationError("El alto debe ser al menos 0.01 y no exceder 9999.")
        return height

    def clean_product_thickness(self):
        thickness = self.cleaned_data.get('product_thickness')
        if thickness < 0.01 or thickness > 9999:
            raise forms.ValidationError("El grosor debe ser al menos 0.01 y no exceder 9999.")
        return thickness

    def clean_product_image(self):
        image = self.cleaned_data.get('product_image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Solo se permiten archivos de imagen JPG y PNG.")
        return image

class ActualizarProductosForm(forms.ModelForm):
    """
    Formulario para actualizar el precio y la cantidad en inventario de un producto.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Modelo relacionado:
        - Product

    Campos:
        - product_price: Precio del producto.
        - product_stock: Cantidad en inventario del producto.

    Uso:
        - Permite a los usuarios modificar solo el precio y el inventario de un producto existente.
    """
    class Meta:
        model = Product
        fields = ['product_price', 'product_stock']


class WithdrawForm(forms.Form):
    """
    Formulario para realizar retiros de saldo.
    Participantes:
    Almanza Quezada Andres Yahir 215993
    Campos:
        - cantidad: Cantidad a retirar (mínimo 0.01).

    Características:
        - Campo `cantidad` validado para aceptar solo valores mayores o iguales a 0.01.
        - Usa un widget personalizado para estilizar el campo como un campo numérico en el frontend.
        - Incluye un atributo `step` para garantizar precisión en cantidades decimales.

    Uso:
        - Este formulario es utilizado para permitir a los usuarios especificar el monto a retirar.
    """
    cantidad = forms.FloatField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True,
            'step': '0.01'
        }),
        label="Cantidad a Retirar"
    )