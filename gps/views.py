import logging
from io import BytesIO

import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from shed.settings import INSTALLED_APPS, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from .forms import ImageUploadForm
from .lib.ImageGps import ImageGps

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "gps/index.html")


##
# Image Upload background info.
# The typical size of a photo taken with an iPhone varies, but generally
# ranges from 2 to 8 MB. Factors like the specific iPhone model, camera
# settings (like HDR or Live Photos), and the content of the image
# (e.g., detailed scenes vs. a blank sky) can affect the file size.
# For example, a photo with a lot of detail might be closer to 3.7 MB,
# while a simpler image could be around 1 MB.
# iPhones use HEIC (High Efficiency Image Format) by default, which tends
# to produce smaller file sizes than JPEG.
# While most newer iPhones have a 12MP sensor, the file size can still vary
# depending on the scene and settings.
# Features like HDR and Live Photos can increase the file size.
def rcv_image_html(request):
    form = ImageUploadForm()
    image = ImageGps(None)
    lat = None
    lon = None
    ctx = {"form": form, "lat": lat, "lon": lon}
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = ImageGps.from_image_bytes(request.FILES["file"])
            lat = image.lat
            lon = image.lon
            logger.debug(f"{__name__}.rcv_image_html: {lat} {lon}")
            ctx = {"form": form, "lat": lat, "lon": lon}
    return render(request, "gps/upload_image.html", ctx)


@csrf_exempt
def rcv_image_mms(request):
    logger.info(f"{__name__}.rcv_image_mms: request: {request.body}")

    if TWILIO_ACCOUNT_SID is None or TWILIO_AUTH_TOKEN is None:
        raise Exception("Twilio Account SID or AuthToken not set.")

    if request.method != "POST":
        return render(request, "gps/image_via_mms.html")

    to = request.POST.get("To", "")
    num_media = int(request.POST.get("NumMedia", ""))
    from_ = request.POST.get("From", "")
    body = request.POST.get("Body", "")
    media_url = request.POST.get("MediaUrl0", "")
    logger.info(
        f"{__name__}.rcv_image_mms: \n to: {to}, \n from_: {from_}, \n numMedia: {num_media}, \n body: {body}, \n mediaUrl: {media_url}"
    )
    INSTALLED_APPS.append("twilio")
    resp = MessagingResponse()
    if num_media > 0:
        logger.info(f"{__name__}.rcv_image_mms: media detected...")
        r = requests.get(
            media_url,
            auth=(
                TWILIO_ACCOUNT_SID,
                TWILIO_AUTH_TOKEN,
            ),
        )
        if r.status_code == 200:
            logger.info(f"{__name__}.rcv_image_mms: MMS media retrieved...")
            image = ImageGps.from_image_bytes(BytesIO(r.content))
            if image is not None:
                logger.info(
                    f"{__name__}.rcv_image_mms: MMS media appears to be an image..."
                )
                lat = image.lat
                lon = image.lon
                logger.debug(f"{__name__}.rcv_image_mms: lat, lon: {lat}, {lon}")
                if lat and lon:
                    resp.message(f"Image received, GPS coords detected: {lat}, {lon}")
                else:
                    resp.message(f"Image received, no GPS info found.")

    return HttpResponse(str(resp), content_type="application/xml")


@csrf_exempt
def rcv_image_email(request):
    # logger.info(f"{__name__}.rcv_image_email: request: {request.body}")

    if TWILIO_ACCOUNT_SID is None or TWILIO_AUTH_TOKEN is None:
        raise Exception("Twilio Account SID or AuthToken not set.")

    if request.method != "POST":
        return render(request, "gps/image_via_email.html")

    INSTALLED_APPS.append("twilio")
    to = request.POST.get("to", "")
    from_ = request.POST.get("from", "")
    subject = request.POST.get("subject", "")
    text = request.POST.get("text", "")
    html = request.POST.get("html", "")
    attachments_count = int(request.POST.get("attachments", ""))
    attachment_info = request.POST.get("attachment-info", "")
    logger.info(
        f"{__name__}.rcv_image_email: \n to: {to}, \n from_: {from_}, \n subject: {subject}, \n text: {text}, \n html: {html}, \n attachments_count: {attachments_count}, \n attachment-info: {attachment_info}"
    )
    logger.info(request.POST.keys())
    resp = MessagingResponse()
    if attachments_count > 0:
        logger.info(f"{__name__}.rcv_image_email: attachments detected...")
        logger.info(request.FILES)
        in_memory_file = request.FILES["attachment1"]
        image = ImageGps.from_image_bytes(in_memory_file)
        if image is not None:
            logger.info(
                f"{__name__}.rcv_image_mms: MMS media appears to be an image..."
            )
            lat = image.lat
            lon = image.lon
            logger.debug(f"{__name__}.rcv_image_mms: lat, lon: {lat}, {lon}")
            if lat and lon:
                resp.message(f"Image received, GPS coords detected: {lat}, {lon}")
            else:
                resp.message(f"Image received, no GPS info found.")
    else:
        resp.message("We received it. No attachments found.")
    return HttpResponse(str(resp), content_type="application/xml")
