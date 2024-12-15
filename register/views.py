#Dependencias para reconociminiento de imagne
import boto3
from django.conf import settings
from django.core.files.storage import default_storage
import os

#dependencias previas
from django.shortcuts import render, redirect
from django.contrib import messages

#dependencias de la base de datos
from product.models import Supplier, UserAccount  # Importamos los modelos

#dependencias del los formularios
from .forms import SupplierRegisterForm
from .forms import ClientRegisterForm
from django.http import JsonResponse

#crear un archivo temporal para las imagenes del reconocimiento
if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp')):
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'))
    
# Definir las palabras clave para un documento valido
KEYWORDS = [
    # Comunes en todos los documentos
    "nombre", "apellidos", "sexo", "fecha de nacimiento", "curp", "firma", "domicilio",
    
    # Credencial de Elector (INE - México)
    "clave de elector", "instituto nacional electoral", "credencial para votar", "vigencia",
    "estado", "municipio", "sección", "emisión", "clave única de registro de población",
    
    # Licencia de Conducir (México y Estados Unidos)
    "licencia para conducir", "chofer particular", "estado de chihuahua", "permiso", "número de licencia",
    "driver license", "license number", "restriction", "class", "expires", "birth date",
    
    # Pasaporte (México y Estados Unidos)
    "pasaporte", "passport", "passport number", "country of issuance", "nationality",
    "date of birth", "place of birth", "surname", "given name", "date of issue", "expiry date",
    "passport card", "united states of america", "estados unidos mexicanos",
    
    # Tarjeta de Residencia (Green Card - Estados Unidos)
    "permanent resident", "uscis", "alien number", "resident since", "category",
    "given names", "country of birth", "uscis number",
    
    # Identification Card (Estados Unidos)
    "identification card", "texas", "state id", "id number", "dob", "expiration date",
    "sample", "address", "city", "zip code", "date issued",
    
    # Información adicional para asegurar la detección
    "issued", "expires", "height", "weight", "eyes", "hair", "organ donor", "veteran",
    "category", "identificación oficial", "número de identificación", "estado", "municipio",
    "expedición", "nacionalidad", "identificación", "clase", "restricciones"
]

# Crear cliente de Amazon Rekognition
def create_rekognition_client():
    """
    Crea y configura un cliente de Amazon Rekognition.

    Participantes:
    Cesar Omar Andrade - 215430

    Returns:
        boto3.client: Un cliente configurado para interactuar con Amazon Rekognition.
    """
    return boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
# Función para detectar palabras clave en el texto extraído
def detect_keywords_in_document(image_path, keywords):
    """
    Detecta palabras clave en un documento utilizando OCR de Amazon Rekognition.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        image_path (str): Ruta al archivo de la imagen.
        keywords (list): Lista de palabras clave a buscar.

    Returns:
        bool: `True` si al menos 2 palabras clave son detectadas, de lo contrario, `False`.
    """
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    with open(image_path, 'rb') as image_file:
        response = rekognition.detect_text(Image={'Bytes': image_file.read()})

    # Lista para almacenar todas las palabras detectadas
    detected_words = set()

    # Extraer todas las palabras y líneas detectadas en la imagen
    for text in response['TextDetections']:
        # Convertir el texto detectado a minúsculas para la comparación
        detected_text = text['DetectedText'].lower()
        
        # Agregar cada palabra a detected_words
        if text['Type'] == 'WORD':
            detected_words.add(detected_text)
        elif text['Type'] == 'LINE':
            # Para cada línea completa, revisa si contiene alguna palabra clave
            for keyword in keywords:
                if keyword.lower() in detected_text:  # Coincidencia parcial en línea completa
                    detected_words.add(keyword.lower())  # Agregar solo la palabra clave, no el texto completo

    # Contar el número de palabras clave que aparecen en el texto detectado
    found_keywords = sum(1 for keyword in keywords if keyword.lower() in detected_words)

    # Retorna True si al menos 2 palabras clave son encontradas
    return found_keywords >= 2

# Función para detectar si una imagen contiene un rostro
def detect_face(image_path):
    """
    Detecta rostros en una imagen utilizando Amazon Rekognition.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        image_path (str): Ruta al archivo de la imagen.

    Returns:
        bool: `True` si se detecta al menos un rostro, de lo contrario, `False`.
    """
    rekognition = create_rekognition_client()
    with open(image_path, 'rb') as image_file:
        response = rekognition.detect_faces(
            Image={'Bytes': image_file.read()},
            Attributes=['ALL']
        )
    return len(response['FaceDetails']) > 0

#funcion que compara las imagenes de la identificacion con la cara en tiempo real
def compare_faces_with_rekognition(identificacion_path, foto_actual_path):
    """
    Compara dos imágenes para determinar si los rostros coinciden.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        identificacion_path (str): Ruta a la imagen de identificación oficial.
        foto_actual_path (str): Ruta a la foto actual capturada o cargada.

    Returns:
        bool: `True` si los rostros coinciden con una similitud mayor al 90%, de lo contrario, `False`.
    """
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    with open(identificacion_path, 'rb') as source_image, open(foto_actual_path, 'rb') as target_image:
        response = rekognition.compare_faces(
            SourceImage={'Bytes': source_image.read()},
            TargetImage={'Bytes': target_image.read()}
        )

    for face_match in response['FaceMatches']:
        similarity = face_match['Similarity']
        if similarity > 90:  # Puedes ajustar el umbral de similitud
            return True
    return False

# Función para verificar que las imágenes no sean las mismas
def are_images_identical(identificacion_path, foto_actual_path):
    """
    Verifica si dos imágenes son idénticas en contenido.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        identificacion_path (str): Ruta a la imagen de identificación oficial.
        foto_actual_path (str): Ruta a la foto actual capturada o cargada.

    Returns:
        bool: `True` si las imágenes son idénticas, de lo contrario, `False`.
    """
    # Compara el contenido binario de los dos archivos
    with open(identificacion_path, 'rb') as img1, open(foto_actual_path, 'rb') as img2:
        return img1.read() == img2.read()


# Definimos para manejar el registro de proveedor
def supplier_register(request):
    """
    Gestiona el registro de proveedores con validación biométrica.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el método de solicitud es POST.
        2. Valida el formulario y guarda las imágenes en almacenamiento temporal.
        3. Realiza validaciones biométricas y de documentos:
            - Detección de palabras clave en la identificación.
            - Detección de rostros en ambas imágenes.
            - Comparación de rostros entre identificación y foto actual.
            - Verifica que las imágenes no sean idénticas.
        4. Guarda al proveedor si las validaciones son exitosas.
        5. Elimina los archivos temporales después de usarlos.

    Returns:
        HttpResponse: Renderiza la plantilla de registro o redirige al login de proveedores si el registro es exitoso.
    """
    if request.method == 'POST':
        
        form = SupplierRegisterForm(request.POST, request.FILES)
        unique_id = request.POST.get('unique_id')
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                # Verifica que la carpeta 'temp' exista
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                # Obtener los archivos de las imágenes
                identificacion_img = request.FILES['identificacion']
                # Define rutas de guardado
                identificacion_path = os.path.join(temp_dir, 'identificacion.jpg')

                # Guarda las imágenes manualmente en la carpeta 'temp'
                with open(identificacion_path, 'wb') as f:
                    f.write(identificacion_img.read())

                # Verificar si la foto actual se tomó con la cámara o si se subió a través del QR
                # Lógica para `foto_actual`
                if 'foto_actual' in request.FILES:  # Si la foto fue tomada con la cámara
                    foto_actual_img = request.FILES['foto_actual']
                    foto_actual_path = os.path.join(temp_dir, 'foto_actual.jpg')
                    with open(foto_actual_path, 'wb') as f:
                        f.write(foto_actual_img.read())
                else:  # Si la foto fue subida mediante el QR
                    foto_actual_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.jpg")
                    if not os.path.exists(foto_actual_path):
                        messages.error(request, 'No se encontró la foto subida. Asegúrate de subir tu foto correctamente, o utilizando el qr.')
                        return render(request, 'home/supplier_register.html', {'form': form})       

                try:
                    # Definir mensajes
                    success_message = 'Proveedor registrado exitosamente'
                    face_mismatch_message = 'Los rostros no coinciden.'
                    invalid_document_message = 'Identificación no válida. Asegúrate de tomar bien la foto y que sea una identificación oficial.'
                
                    # Verificar condiciones
                    if not detect_keywords_in_document(identificacion_path, KEYWORDS):
                        messages.error(request, invalid_document_message)
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not detect_face(identificacion_path):
                        messages.error(request, 'La identificación no muestra bien el rostro.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not detect_face(foto_actual_path):
                        messages.error(request, 'La foto actual no muestra bien el rostro.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif are_images_identical(identificacion_path, foto_actual_path):
                        messages.error(request, 'La foto actual no debe ser la misma que la identificación. Por favor, sube una foto diferente.')
                        return render(request, 'home/supplier_register.html', {'form': form})
                    elif not compare_faces_with_rekognition(identificacion_path, foto_actual_path):
                        messages.error(request, face_mismatch_message)
                        return render(request, 'home/supplier_register.html', {'form': form})
                    else:
                        form.save()
                        
                        messages.success(request, success_message)
                        return redirect('supplier_login')  # Redirigir a la página de inicio de sesión
                
                finally:
                    # Eliminar archivos temporales después de usarlos
                    if os.path.exists(identificacion_path):
                        os.remove(identificacion_path)
                    if os.path.exists(foto_actual_path):
                        os.remove(foto_actual_path)
        else:
            print("Errores del formulario:", form.errors)
            messages.error(request, 'El formulario no es válido. Revisa los datos.')
        
    else:
        form = SupplierRegisterForm()
    return render(request, 'home/supplier_register.html', {'form': form})

def client_register(request):
    """
    Gestiona el registro de clientes con validación biométrica.

    Participantes:
    Cesar Omar Andrade - 215430
    Coauthor: Hugo Abisai Reyes Trejo - 215201
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Verifica si el método de solicitud es POST.
        2. Valida el formulario y guarda las imágenes en almacenamiento temporal.
        3. Realiza validaciones biométricas y de documentos:
            - Detección de palabras clave en la identificación.
            - Detección de rostros en ambas imágenes.
            - Comparación de rostros entre identificación y foto actual.
            - Verifica que las imágenes no sean idénticas.
        4. Guarda al cliente si las validaciones son exitosas.
        5. Elimina los archivos temporales después de usarlos.

    Returns:
        HttpResponse: Renderiza la plantilla de registro o redirige al login de clientes si el registro es exitoso.
    """
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST, request.FILES)
        unique_id = request.POST.get('unique_id')
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                # Crear directorio temporal si no existe
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Obtener imágenes de identificación y foto actual
                identificacion_img = request.FILES['identificacion']
                # Definir rutas temporales para guardar las imágenes
                identificacion_path = os.path.join(temp_dir, 'identificacion.jpg')

                # Guardar las imágenes en las rutas temporales
                with open(identificacion_path, 'wb') as f:
                    f.write(identificacion_img.read())

                                # Verificar si la foto actual se tomó con la cámara o si se subió a través del QR
                # Lógica para `foto_actual`
                if 'foto_actual' in request.FILES:  # Si la foto fue tomada con la cámara
                    foto_actual_img = request.FILES['foto_actual']
                    foto_actual_path = os.path.join(temp_dir, 'foto_actual.jpg')
                    with open(foto_actual_path, 'wb') as f:
                        f.write(foto_actual_img.read())
                else:  # Si la foto fue subida mediante el QR
                    foto_actual_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}.jpg")
                    if not os.path.exists(foto_actual_path):
                        messages.error(request, 'No se encontró la foto subida. Asegúrate de subir tu foto correctamente, o utilizando el qr.')
                        return render(request, 'home/client_register.html', {'form': form})    

                try:
                    # Verificar condiciones
                    if not detect_keywords_in_document(identificacion_path, KEYWORDS):
                        messages.error(request, 'Identificación no válida. Asegúrate de que sea una identificación oficial.')
                    elif not detect_face(identificacion_path):
                        messages.error(request, 'La identificación no muestra claramente el rostro.')
                    elif not detect_face(foto_actual_path):
                        messages.error(request, 'La foto actual no muestra claramente el rostro.')
                    elif are_images_identical(identificacion_path, foto_actual_path):
                        messages.error(request, 'Las imágenes no deben ser idénticas. Sube fotos diferentes.')
                    elif not compare_faces_with_rekognition(identificacion_path, foto_actual_path):
                        messages.error(request, 'Los rostros no coinciden.')
                    else:
                        # Guarda el cliente y muestra mensaje de éxito
                        form.save()
                        messages.success(request, 'Cliente registrado exitosamente')
                        return redirect('client_login')  # Redirige al login de usuarios normales
                finally:
                    # Eliminar archivos temporales después de usarlos
                    if os.path.exists(identificacion_path):
                        os.remove(identificacion_path)
                    if os.path.exists(foto_actual_path):
                        os.remove(foto_actual_path)
        else:
            messages.error(request, 'El formulario no es válido. Revisa los datos.')
    else:
        form = ClientRegisterForm()

    return render(request, 'home/client_register.html', {'form': form})

def cargar_foto(request, unique_id):
    """
    Permite cargar una foto mediante un identificador único generado dinámicamente para el QR.

    Participantes:
    Cesar Omar Andrade - 215430

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        unique_id (str): Identificador único asociado a la foto.

    Lógica:
        1. Verifica si el método de solicitud es POST y contiene una foto.
        2. Guarda la foto en el almacenamiento con el identificador único como nombre.
        3. Maneja errores durante la carga y muestra mensajes al usuario.

    Returns:
        HttpResponse: Renderiza la plantilla `cargar_foto.html` con el identificador único.
    """
    if request.method == 'POST' and request.FILES.get('foto'):
        foto = request.FILES['foto']
        # Guardar la foto con el nombre de la ID única
        foto_name = f"{unique_id}.jpg"  # Asegúrate de que el nombre esté correcto
        foto_path = os.path.join(settings.MEDIA_ROOT, foto_name)
        
        try:
            default_storage.save(foto_path, foto)
            messages.success(request, 'Foto cargada correctamente, termina de rellenar el formulario!')
        except Exception as e:
            # Manejar cualquier error durante la carga
            messages.error(request, 'La foto no pudo ser cargada correctamente, vuelve a intentarlo.')
            print(f"Error al guardar la foto: {e}")

        return render(request, 'home/cargar_foto.html', {'unique_id': unique_id})
    
    return render(request, 'home/cargar_foto.html', {'unique_id': unique_id})

