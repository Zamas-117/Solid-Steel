from django import forms
from product.models import Client, ClientAddress
import re
from django.core.exceptions import ValidationError

class ClientForm(forms.ModelForm):
    user_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo'})
    )
    user_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}),
        required=False
    )
    client_first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    client_last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    client_phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = Client
        fields = ['client_first_name', 'client_last_name', 'client_phone']


class ClientAddressForm(forms.ModelForm):
    """
    Formulario para gestionar la dirección de un cliente.
    Participantes:
    Cesar Omar Rodarte Andrade
    Andres Yahir Almanza Quezada
    Modelo relacionado:
        - ClientAddress

    Campos:
        - client_address: Dirección principal del cliente.
        - client_city: Ciudad donde reside el cliente.
        - client_state: Estado donde reside el cliente.
        - client_zip_code: Código postal de la dirección.
        - client_address_additional_information: Información adicional sobre la dirección.

    Validaciones personalizadas:
        - client_address:
            - Solo permite letras, números, espacios y el símbolo '#'.
        - client_city:
            - Solo permite letras y espacios.
        - client_state:
            - Solo permite letras (no números ni caracteres especiales).
        - client_zip_code:
            - Debe contener solo dígitos y tener al menos 5 caracteres.
        - client_address_additional_information:
            - Longitud máxima de 100 caracteres.
            - Solo permite letras, números y espacios.

    Widgets:
        - Estiliza los campos utilizando `form-control cantidad` para integrar con un diseño frontend basado en Bootstrap.
        - Incluye marcadores de posición (`placeholder`) para guiar al usuario al completar el formulario.

    Uso:
        - Este formulario es utilizado para capturar y validar la información de dirección de un cliente en aplicaciones relacionadas con e-commerce o gestión de usuarios.

    Notas:
        - Las validaciones personalizadas aseguran que los datos ingresados sean consistentes y estén en el formato esperado.
        - Los mensajes de error guían al usuario para corregir problemas en la entrada de datos.
    """
    class Meta:
        model = ClientAddress
        fields = [
            'client_address',
            'client_city',
            'client_state',
            'client_zip_code',
            'client_address_additional_information'
        ]
        widgets = {
            'client_address': forms.TextInput(attrs={
                'class': 'form-control cantidad',
                'placeholder': 'Ingrese la dirección'
            }),
            'client_city': forms.TextInput(attrs={
                'class': 'form-control cantidad',
                'placeholder': 'Ingrese la ciudad'
            }),
            'client_state': forms.TextInput(attrs={
                'class': 'form-control cantidad',
                'placeholder': 'Ingrese el estado'
            }),
            'client_zip_code': forms.NumberInput(attrs={
                'class': 'form-control cantidad',
                'placeholder': 'Ingrese el código postal'
            }),
            'client_address_additional_information': forms.TextInput(attrs={
                'class': 'form-control cantidad',
                'placeholder': 'Información adicional'
            }),
        }

    def clean_client_address(self):
        address = self.cleaned_data['client_address']
        if not re.match(r'^[a-zA-Z0-9#\s]+$', address):
            raise ValidationError("La dirección solo puede contener letras, números, espacios y el símbolo #.")
        return address

    def clean_client_city(self):
        city = self.cleaned_data['client_city']
        if not re.match(r'^[a-zA-Z\s]+$', city):
            raise ValidationError("La ciudad solo puede contener letras y espacios.")
        return city

    def clean_client_state(self):
        state = self.cleaned_data['client_state']
        if not state.isalpha():
            raise ValidationError("El estado solo puede contener letras.")
        return state

    def clean_client_zip_code(self):
        zip_code = str(self.cleaned_data['client_zip_code'])
        if not zip_code.isdigit() or len(zip_code) < 5:
            raise ValidationError("El código postal debe tener al menos 5 dígitos.")
        return zip_code

    def clean_client_address_additional_information(self):
        additional_info = self.cleaned_data['client_address_additional_information']
        if len(additional_info) > 100:
            raise ValidationError("La información adicional no debe exceder los 100 caracteres.")
        if not re.match(r'^[a-zA-Z0-9\s]+$', additional_info):
            raise ValidationError("La información adicional solo puede contener letras y números.")
        return additional_info
