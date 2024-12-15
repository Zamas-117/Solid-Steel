from django.shortcuts import render, get_object_or_404, redirect
from product.models import Order, Shipment, Payment, ShoppingCart, Client, ClientAddress
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.contrib import messages
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
import re
import time

logger = logging.getLogger(__name__)

@csrf_exempt
def ship24_webhook(request):
    """
    Procesa el webhook de Ship24 y actualiza los datos de los envíos y eventos de seguimiento.

    Autor:
    Berenice Flores Hernández

    Args:
        request (HttpRequest): Objeto de solicitud HTTP.

    Lógica:
        1. Valida la autorización del webhook utilizando el encabezado `Authorization`.
        2. Procesa el payload recibido para extraer datos de seguimiento.
        3. Actualiza los eventos y estados de los envíos correspondientes en la base de datos.

    Returns:
        JsonResponse: Respuesta JSON indicando el resultado del procesamiento del webhook.
    """
    if request.method == "HEAD":
        logger.info("Webhook validado exitosamente con HEAD request.")
        return HttpResponse(status=200)

    if request.method == "POST":
        # Validar autorización
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {settings.SHIP24_WEBHOOK_SECRET}":
            logger.error("Autorización fallida.")
            return JsonResponse({"error": "No autorizado"}, status=401)

        try:
            payload = json.loads(request.body)
            trackings = payload.get("trackings", [])

            for tracking in trackings:
                tracking_number = tracking.get("tracker", {}).get("trackingNumber")
                events = tracking.get("events", [])

                # Buscar el envío asociado
                shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()
                if not shipment:
                    logger.warning(f"Envío no encontrado para: {tracking_number}")
                    continue

                for event in events:
                    status = event.get("status", "").lower()
                    status_milestone = event.get("statusMilestone", "")
                    occurrence_datetime = event.get("occurrenceDatetime", "")

                    try:
                        event_date = make_aware(datetime.fromisoformat(occurrence_datetime))
                    except ValueError:
                        logger.error(f"Fecha inválida: {occurrence_datetime}")
                        continue

                    # Registrar evento
                    if not shipment.events.filter(status=status, occurrence_datetime=event_date).exists():
                        shipment.events.create(
                            status=status,
                            occurrence_datetime=event_date,
                        )
                        logger.info(f"Evento registrado: {status} ({event_date})")

                    # Actualizar estado del envío
                    if status == "shipped":
                        if not shipment.shipment_date or shipment.shipment_date < event_date:
                            shipment.shipment_date = event_date
                            shipment.shipment_status = "Enviado"
                            shipment.save()
                            logger.info(f"Fecha de envío actualizada: {shipment.shipment_date}")

                    elif status == "delivered":
                        if not shipment.shipment_actual_delivery_date or shipment.shipment_actual_delivery_date < event_date:
                            shipment.shipment_actual_delivery_date = event_date
                            shipment.shipment_status = "Entregado"
                            shipment.save()
                            logger.info(f"Fecha de entrega actualizada: {shipment.shipment_actual_delivery_date}")

            return JsonResponse({"message": "Webhook procesado correctamente."}, status=200)

        except json.JSONDecodeError:
            logger.error("Error al parsear el JSON.")
            return JsonResponse({"error": "Payload inválido"}, status=400)
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            return JsonResponse({"error": "Error inesperado"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

def controlar_limite_solicitudes():
    """
    Pausa para cumplir con el límite de solicitudes por segundo de Ship24.
    """
    time.sleep(0.1)  # Pausa de 100ms entre solicitudes

def determinar_courier_code(tracking_number):
    """
    Determina el courierCode basado en el número de seguimiento o mediante reglas definidas.
    """
    couriers = [
        {"code": "dhl", "regex": r"^\d{10}$"},
        {"code": "fedex", "regex": r"^\d{12}$"},
        {"code": "ups", "regex": r"^\d{18}$"},
    ]
    for courier in couriers:
        if re.match(courier["regex"], tracking_number):
            return courier["code"]
    return None  # Retorna None si no se puede determinar el mensajero

def courier_requiere_datos_adicionales(courier_code):
    """
    Verifica si el mensajero requiere datos adicionales como código postal y código de país.
    """
    couriers_requiring_data = ["fedex", "ups"]
    return courier_code in couriers_requiring_data


def actualizar_rastreador_ship24(tracker_id, courier_code):
    """
    Actualiza un tracker existente en Ship24.
    """
    try:
        validate_courier_code(courier_code)
    except ValueError as e:
        logger.error(f"Código de mensajero inválido: {e}")
        return False

    url = f"https://api.ship24.com/public/v1/trackers/{tracker_id}"
    headers = {
        "Authorization": f"Bearer {settings.SHIP24_API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "courierCode": [courier_code],
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Tracker actualizado correctamente: {tracker_id}")
        return True
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Error HTTP al actualizar tracker: {http_err}")
    except Exception as e:
        logger.error(f"Error inesperado al actualizar tracker: {e}")
    return False

# Vista principal de la app shipping
def shipping(request):
    return render(request, 'shipping/shipping.html')


def shipping_actualizar_datos(request):
    return render(request, 'shipping/shipping_actualizar_datos.html')

# Vista para mostrar los pedidos pagados
def paid_orders(request):
    """
    Muestra los pedidos pagados del cliente autenticado y sus envíos pendientes.

    Autor:
    Berenice Flores Hernández

    Args:
        request (HttpRequest): Objeto de solicitud HTTP.

    Lógica:
        1. Verifica que el usuario esté autenticado.
        2. Obtiene los envíos pendientes asociados al cliente autenticado.
        3. Renderiza un template con los datos de los pedidos y envíos pendientes.

    Returns:
        HttpResponse: Renderiza el template `shipment_tracking_info.html`.
    """
    # Obtiene el ID de usuario de la sesión y verifica que esté autenticado
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('client_login')

    # Busca al cliente basado en el ID de usuario
    client = get_object_or_404(Client, user_id=user_id)

    # Filtra envíos pendientes del usuario
    shipments = Shipment.objects.filter(
        order__client=client,
        shipment_status="Pendiente"
    )

    # Determina si existen envíos pendientes
    has_pending_shipments = shipments.exists()

    # Envía los datos de envíos y el indicador de envíos pendientes al template
    return render(request, 'shipping/shipment_tracking_info.html', {
        'shipments': shipments,
        'client': client,
        'has_pending_shipments': has_pending_shipments
    })


# Vista para mostrar detalles de un envío específico y obtener información de Ship24
def shipment_tracking_info(request, tracking_number):
    """
    Muestra los detalles de un envío específico y sus eventos de seguimiento almacenados localmente.

    Autor:
    Berenice Flores Hernández

    Args:
        request (HttpRequest): Objeto de solicitud HTTP.
        tracking_number (str): Número de seguimiento del envío.

    Lógica:
        1. Busca el envío correspondiente al número de seguimiento.
        2. Obtiene los eventos relacionados con el envío.
        3. Renderiza un template con los detalles del envío y sus eventos.

    Returns:
        HttpResponse: Renderiza el template `shipment_info.html`.
    """
    shipment = Shipment.objects.filter(shipment_tracking_number=tracking_number).first()

    if not shipment:
        messages.error(request, "Envío no encontrado")
        return redirect("paid_orders")

    # Obtener los eventos relacionados con el envío
    tracking_events = shipment.events.order_by('-occurrence_datetime')

    return render(request, 'shipping/shipment_info.html', {
        'shipment': shipment,
        'tracking_events': tracking_events,
    })
    
@login_required
def tracking_overview(request):
    """
    Muestra una vista general de los envíos del usuario autenticado.

    Autor:
    Berenice Flores Hernández

    Args:
        request (HttpRequest): Objeto de solicitud HTTP.

    Lógica:
        1. Obtiene los envíos asociados al usuario autenticado.
        2. Renderiza un template con los envíos.

    Returns:
        HttpResponse: Renderiza el template `tracking_overview.html`.
    """
    user_id = request.user.id  # Suponiendo que el usuario está autenticado
    shipments = Shipment.objects.filter(order_clientuser_id_user=user_id)
    return render(request, 'shipping/tracking_overview.html', {'shipments': shipments})

def track_shipment_with_additional_info(shipment, destination_postcode, destination_country_code):
    """
    Realiza el seguimiento de un envío con datos adicionales como código postal y código de país.

    Autor:
    Berenice Flores Hernández

    Args:
        shipment (Shipment): Objeto de envío a rastrear.
        destination_postcode (str): Código postal del destino.
        destination_country_code (str): Código de país del destino.

    Lógica:
        1. Verifica que se proporcionen los datos adicionales requeridos.
        2. Realiza el seguimiento utilizando la API de Ship24.

    Returns:
        dict: Respuesta JSON de la API de Ship24 con los detalles del seguimiento.

    Raises:
        ValueError: Si falta el código postal o el código de país y el mensajero lo requiere.
    """
    if shipment.shipment_carrier == 'CourierCodeRequiereDatosAdicionales':
        if not destination_postcode or not destination_country_code:
            raise ValueError("Se requiere el código postal y el código de país del destinatario.")
    
    # Lógica para hacer el seguimiento con la API de Ship24, con los datos adicionales
    api_url = f"https://api.ship24.com/trackings/{shipment.shipment_tracking_number}"
    data = {
        'destinationPostCode': destination_postcode,
        'destinationCountryCode': destination_country_code,
        # Otros parámetros...
    }
    response = requests.post(api_url, json=data)
    return response.json()

def get_couriers(request):
    """
    Obtiene la lista de mensajeros disponibles desde la API de Ship24.

    Autor:
    Berenice Flores Hernández

    Args:
        request (HttpRequest): Objeto de solicitud HTTP.

    Lógica:
        1. Realiza una solicitud GET a la API de Ship24.
        2. Devuelve la lista de mensajeros o un error en caso de falla.

    Returns:
        JsonResponse: Respuesta JSON con la lista de mensajeros o un mensaje de error.
    """
    url = 'https://api.ship24.com/couriers'
    headers = {
        'Authorization': f'Bearer {settings.SHIP24_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        couriers = response.json()
        return JsonResponse(couriers, safe=False)
    else:
        return JsonResponse({'error': 'Error al obtener los mensajeros'}, status=400)


def validate_courier_code(courier_code):
    """
    Valida si el código de mensajero es válido.

    Autor:
    Berenice Flores Hernández

    Args:
        courier_code (str): Código de mensajero a validar.

    Lógica:
        1. Verifica si el código de mensajero está en la lista de códigos obsoletos.
        2. Si el código es obsoleto, lanza una excepción.

    Raises:
        ValueError: Si el código de mensajero está obsoleto y no debe usarse.
    """
    obsolete_codes = ['ObsoleteCourierCode1', 'ObsoleteCourierCode2']
    if courier_code in obsolete_codes:
        logger.error(f"Código de mensajero inválido: {courier_code}")
        raise ValueError(f"El mensajero {courier_code} está obsoleto y no debe usarse.")
    logger.info(f"Código de mensajero válido: {courier_code}")
