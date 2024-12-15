from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .forms import SupplierLoginForm
from product.models import UserAccount, UserRole,PasswordReset, UserRole, UserAuthProvider  # Asegúrate de que este es tu modelo correcto

def supplier_login(request):
    """
    Vista que maneja el inicio de sesión de los proveedores.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene los datos enviados por el formulario de inicio de sesión.

    Lógica:
        1. Verifica si el método de la solicitud es POST.
        2. Valida los datos del formulario de inicio de sesión.
        3. Busca al usuario con el correo proporcionado y el rol de proveedor.
        4. Verifica la contraseña del usuario.
        5. Si las credenciales son válidas:
            - Guarda el rol y el ID del proveedor en la sesión.
            - Redirige al menú del proveedor.
        6. Si no, muestra mensajes de error específicos.

    Returns:
        HttpResponse: Renderiza la plantilla `home/supplier_login.html` con el formulario de inicio de sesión,
        o redirige al menú del proveedor si el inicio de sesión es exitoso.
    """
    
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Buscar el usuario con el rol de 'Supplier'
            try:
                user = UserAccount.objects.get(user_email=email, user_role=UserRole.SUPPLIER)
                
                # Verificar la contraseña usando el método 'check_password' del modelo UserAccount
                if user.check_password(password):
                    # Aquí no usamos 'login()' de Django, sino que manejamos la sesión manualmente
                    request.session['user_role'] = user.user_role
                    request.session['supplier_id'] = user.id_user  # Guardar el ID del usuario en la sesión
                    #messages.success(request, 'Has iniciado sesión correctamente')
                    return redirect('supplier_menu')  # Redirigir al panel de proveedor
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except UserAccount.DoesNotExist:
                messages.error(request, 'Proveedor no encontrado con ese correo')
    else:
        form = SupplierLoginForm()

    return render(request, 'home/supplier_login.html', {'form': form})



# Vista para el login de usuarios normales (clientes)
def client_login(request):
    """
    Vista que maneja el inicio de sesión de los clientes.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene los datos enviados por el formulario de inicio de sesión.

    Lógica:
        1. Verifica si el método de la solicitud es POST.
        2. Valida los datos del formulario de inicio de sesión.
        3. Busca al usuario con el correo proporcionado y el rol de cliente.
        4. Verifica la contraseña del usuario si utiliza autenticación interna.
        5. Si las credenciales son válidas:
            - Guarda el rol y el ID del cliente en la sesión.
            - Redirige a la lista de productos.
        6. Si no, muestra mensajes de error específicos.

    Returns:
        HttpResponse: Renderiza la plantilla `home/client_login.html` con el formulario de inicio de sesión,
        o redirige a la lista de productos si el inicio de sesión es exitoso.
    """
    
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # Buscar al usuario por su correo y rol de cliente
                user = UserAccount.objects.get(user_email=email, user_role=UserRole.CLIENT)

                # Verificar si el usuario es del proveedor interno
                if user.user_auth_provider == UserAuthProvider.INTERNAL:
                    # Verificar la contraseña si el proveedor es 'INTERNAL'
                    if user.check_password(password):
                        request.session['user_role'] = user.user_role
                        request.session['user_id'] = user.id_user  # Guardar el ID en la sesión
                        #messages.success(request, 'Has iniciado sesión correctamente.')
                        return redirect('product_list')  # Redirigir a la lista de productos
                    else:
                        messages.error(request, 'Contraseña incorrecta.')
                else:
                    # Si el usuario es de Google, no necesita contraseña
                    request.session['user_id'] = user.id_user  # Guardar el ID en la sesión
                    #messages.success(request, 'Inicio de sesión exitoso con Google.')
                    return redirect('product_list')  # Redirigir a la lista de productos

            except UserAccount.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
    else:
        form = SupplierLoginForm()

    return render(request, 'home/client_login.html', {'form': form})


def password_reset_request(request):
    """
    Vista que maneja la solicitud de restablecimiento de contraseña.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene el correo enviado por el formulario.

    Lógica:
        1. Verifica si el método de la solicitud es POST.
        2. Busca al usuario con el correo proporcionado.
        3. Genera un código de restablecimiento y lo almacena en la base de datos.
        4. Envía el código al correo proporcionado.
        5. Guarda el correo en la sesión para futuras vistas.
        6. Redirige a la vista de verificación de código.

    Returns:
        HttpResponse: Renderiza la plantilla `home/reset_password.html`, o redirige a la verificación del código si la solicitud es exitosa.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Limpiar los mensajes previos
        storage = messages.get_messages(request)
        storage.used = True
                
        try:
            user = UserAccount.objects.get(user_email=email)
            # Generar un código de 6 dígitos
            reset_code = get_random_string(6, allowed_chars='0123456789')
            expiration_time = timezone.now() + timedelta(minutes=30)  # Expira en 30 minutos

            # Guardar el código en la base de datos
            PasswordReset.objects.create(
                user=user,
                reset_code=reset_code,
                reset_expiration_time=expiration_time
            )

            # Enviar el código por correo
            send_mail(
                'Código de restablecimiento de contraseña',
                f'Tu código para restablecer la contraseña es: {reset_code}',
                'noreply@solidsteel.com',  
                [email],
                fail_silently=False,
            )

            # Guardar el email en la sesión para futuras vistas
            request.session['reset_email'] = email

            #Mensaje para confirmar que se envio un codigo
            messages.success(request, 'Se envio un codigo a tu correo, favor de verificarlo.')
            # Redirigir al formulario de verificación de código
            return redirect('verify_reset_code')

        except UserAccount.DoesNotExist:
            # Mostrar error si el correo no está registrado
            messages.error(request, 'No se encontro ningun usario intentelo de nuevo.')
            return redirect('password_reset')
            
    return render(request, 'home/reset_password.html')




def verify_reset_code(request):
    """
    Vista que verifica el código de restablecimiento de contraseña enviado al correo del usuario.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene el código enviado por el formulario.

    Lógica:
        1. Recupera el correo del usuario desde la sesión.
        2. Verifica si el código proporcionado es válido y no ha expirado.
        3. Si el código es válido, redirige a la vista para establecer una nueva contraseña.
        4. Si no, muestra un mensaje de error.

    Returns:
        HttpResponse: Renderiza la plantilla `home/verify_code.html` con el resultado de la verificación.
    """
    
    email = request.session.get('reset_email')  # Obtener el correo desde la sesión
    if request.method == 'POST':
        reset_code = request.POST.get('reset_code')

        try:
            # Buscar si existe un código válido y no expirado
            password_reset = PasswordReset.objects.get(
                user__user_email=email,
                reset_code=reset_code,
                reset_expiration_time__gte=timezone.now()
            )
            # Si el código es válido, redirigir a la vista para crear una nueva contraseña
            return redirect('set_new_password')

        except PasswordReset.DoesNotExist:
            # Mostrar error si el código es incorrecto o expirado
            return render(request, 'home/verify_code.html', {'error': 'Código inválido o expirado', 'email': email})
    
    return render(request, 'home/verify_code.html', {'email': email})

def set_new_password(request):
    """
    Vista que permite a los usuarios establecer una nueva contraseña tras verificar el código de restablecimiento.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene la nueva contraseña enviada por el formulario.

    Lógica:
        1. Recupera el correo del usuario desde la sesión.
        2. Valida y guarda la nueva contraseña para el usuario.
        3. Elimina los códigos de restablecimiento asociados al usuario.
        4. Limpia la sesión y muestra un mensaje de éxito.
        5. Redirige al login según el rol del usuario.

    Returns:
        HttpResponse: Renderiza la plantilla `home/set_new_password.html`, o redirige al login del cliente o proveedor.
    """
    email = request.session.get('reset_email')  # Obtener el correo desde la sesión
    if not email:
        return redirect('password_reset_request')  # Si no hay correo en la sesión, redirigir

    if request.method == 'POST':
        new_password = request.POST.get('new_password')

        try:
            # Obtener al usuario por su correo electrónico
            user = UserAccount.objects.get(user_email=email)
            # Obtener el tipo de cliente (rol) del usuario
            client_role = user.user_role
            
            user.set_password(new_password)
            user.save()

            # Borrar los códigos de restablecimiento asociados al usuario después de cambiar la contraseña
            PasswordReset.objects.filter(user=user).delete()

            # Limpiar la sesión
            del request.session['reset_email']
            
            # Limpiar los mensajes previos
            storage = messages.get_messages(request)
            storage.used = True
            
            if client_role=='Client':
                messages.success(request, 'Tu constraseña se cambio correctamente.')
                return redirect('client_login')  # Redirigir al login CLIENTE tras el éxito
            elif client_role=='Supplier':
                messages.success(request, 'Tu constraseña se cambio correctamente.')
                return redirect('client_login')  # Redirigir al login PROOVEDOR tras el éxito
            else:
                messages.error(request, 'No se encontro ningun usario intentelo de nuevo.')
                return redirect('password_reset')
                
                

        except UserAccount.DoesNotExist:
            # Mostrar error si el correo no está en la base de datos
            return render(request, 'home/set_new_password.html', {'error': 'Error al restablecer la contraseña', 'email': email})

    return render(request, 'home/set_new_password.html', {'email': email})
