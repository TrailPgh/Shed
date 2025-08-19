"""
URL configuration for gps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from gps.views import index as gps_index
from gps.views import rcv_image_html, rcv_image_mms, rcv_image_email
from shed.views import index as shed_index

urlpatterns = [
    path("", shed_index, name="index"),
    path("admin/", admin.site.urls),
    path("gps/", gps_index, name="gps"),
    path("gps/rcv_image_html", rcv_image_html, name="rcv_image_html"),
    path("gps/rcv_image_mms", rcv_image_mms, name="rcv_image_mms"),
    path("gps/rcv_image_email", rcv_image_email, name="rcv_image_email"),
]
