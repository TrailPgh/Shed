from django.shortcuts import render


def index(request):
    return render(request, 'gps/index.html')


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
    return render(request, 'gps/upload_image.html')
