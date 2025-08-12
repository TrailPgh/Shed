import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

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
def upload_image(request):
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
            logger.debug(f"{__name__}: {lat} {lon}")
            ctx = {"form": form, "lat": lat, "lon": lon}
    return render(request, "gps/upload_image.html", ctx)


@csrf_exempt
def rcv_mms_image(request):
    logger.debug(f"{__name__}.rcv_mms_image: request: {request.__str__()}")
    # Create a new Twilio MessagingResponse
    resp = MessagingResponse()
    resp.message("The Robots are coming! Head for the hills!")
    return HttpResponse(str(resp))
