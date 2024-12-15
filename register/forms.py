from django import forms
from product.models import Supplier, UserAccount,Client  # Importamos los modelos
from django.contrib.auth.hashers import make_password  # Para encriptar contraseñas


#REGISTRO PARA EL SUPPLIER
class SupplierRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'})) 
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    
    # Nuevos campos para cargar las imágenes
    identificacion = forms.ImageField(required=True)
    foto_actual = forms.ImageField(required=False)
    
    
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'supplier_address', 'supplier_city', 'supplier_zip_code', 'supplier_state']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_address': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_city': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_state': forms.TextInput(attrs={'class': 'form-control'}),
            'balance':0,
        }

    def save(self, commit=True):
        # Creamos primero un nuevo usuario (UserAccount)
        user = UserAccount(
            user_email=self.cleaned_data['email'],
            user_password=make_password(self.cleaned_data['password']),  # Encriptamos la contraseña
            user_role='Supplier'  # Aquí especificamos que es un Supplier
        )
        if commit:
            user.save()

        # Guardamos la información del proveedor (Supplier)
        supplier = super(SupplierRegisterForm, self).save(commit=False)
        supplier.user = user  # Relacionamos el proveedor con el usuario
        if commit:
            supplier.save()
        return supplier
    
#REGISTRO PARA EL USUARIO
class ClientRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    
    identificacion = forms.ImageField(required=True)
    foto_actual = forms.ImageField(required=False)
    
    class Meta:
        model = Client
        fields = ['client_first_name', 'client_last_name', 'client_phone']
        widgets = {
            'client_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Crear un nuevo usuario (UserAccount) con el rol de Cliente
        user = UserAccount(
            user_email=self.cleaned_data['email'],
            user_password=make_password(self.cleaned_data['password']),  # Encriptamos la contraseña
            user_role='Client'  # Aquí especificamos que es un cliente
        )
        if commit:
            user.save()

        # Guardamos la información del cliente (Client)
        client = super(ClientRegisterForm, self).save(commit=False)
        client.user = user  # Relacionamos el cliente con el usuario
        if commit:
            client.save()
        return client