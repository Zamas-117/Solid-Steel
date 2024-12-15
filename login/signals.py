from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from product.models import UserAccount, UserRole
from django.contrib import messages

#El archivo sirve para que los clientes se puedan reconocer como clientes de Google
@receiver(user_signed_up)
def create_user_account_on_signup(sender, request, user, **kwargs):
    
    """
    Crea un registro en UserAccount cuando un usuario se registra con Google y le da el rol de cliente.

    Template Name: Creación de cuenta de usuario en registro con Google
    File: signals.py
    Author: Berenice Flores Hernández

    Descripción:
        Esta función se activa cuando un usuario se registra con su cuenta de Google.
        Crea automáticamente un registro en la base de datos de UserAccount asignándole el rol de CLIENTE.

    Características principales:
        - Crea o actualiza el registro de usuario en UserAccount.
        - Asigna automáticamente el rol de cliente (CLIENTE) al usuario registrado.
        - Muestra un mensaje de éxito si se crea la cuenta correctamente.

    Notas:
        - La función utiliza la señal user_signed_up de Django Allauth para detectar el registro de usuarios.
        - Requiere que el modelo UserAccount y UserRole estén definidos correctamente en product.models.
    """
    
    account, created = UserAccount.objects.get_or_create(
        user_email=user.email,
        defaults={
            'user_role': UserRole.CLIENT,  # Asigna el rol CLIENT automáticamente
        }
    )
    if created:
        messages.success(request, 'Se ha creado tu cuenta correctamente.')

@receiver(user_logged_in)
def ensure_user_account_exists_on_login(sender, request, user, **kwargs):
    
    """
    Asegura que el usuario tenga un registro en UserAccount al iniciar sesión y sincroniza la sesión.

    Template Name: Asegurar cuenta de usuario al iniciar sesión
    File: signals.py
    Author: Berenice Flores Hernández

    Descripción:
        Esta función verifica que exista un registro en UserAccount para el usuario que inicia sesión.
        Si no existe, crea automáticamente un nuevo registro asignándole el rol de CLIENTE y sincroniza la sesión del usuario.

    Características principales:
        - Verifica y crea un registro en UserAccount si no existe para el usuario que inicia sesión.
        - Asigna automáticamente el rol de cliente (CLIENTE) si se crea un nuevo registro.
        - Sincroniza la sesión del usuario con los datos de UserAccount, incluyendo ID, correo electrónico y rol.

    Notas:
        - Utiliza la señal user_logged_in de Django Allauth para detectar el inicio de sesión de usuarios.
        - Es crucial que la sesión del usuario se sincronice correctamente para mantener la coherencia de los datos.
    """
    
    account, created = UserAccount.objects.get_or_create(
        user_email=user.email,
        defaults={
            'user_role': UserRole.CLIENT,  # Asigna el rol CLIENT automáticamente si no existe
        }
    )

    # Sincronizar la sesión con los datos del usuario
    request.session['user_id'] = account.id_user
    request.session['user_email'] = account.user_email
    request.session['user_role'] = account.user_role
