import logging

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


class ImageGps:
    def __init__(self, pil_image):
        self.lat = None
        self.lon = None
        self.image = pil_image
        if self.image is None:
            return
        self.exif = self.get_exif(self.image)
        if self.exif is None:
            return
        self.gps_ifd = self.get_gps_ifd(self.exif)
        if self.gps_ifd is None:
            return
        self.lat = self.get_lat(self.gps_ifd)
        self.lon = self.get_lon(self.gps_ifd)
        logger.debug(f"{__name__}.__init__: {self.__dict__}")

    def get_lat(self, gps_ifd):
        gps_lat = gps_ifd.get(ExifTags.GPS.GPSLatitude)
        gps_lat_ref = gps_ifd.get(ExifTags.GPS.GPSLatitudeRef)
        return self.convert_lat_coords(gps_lat, gps_lat_ref)

    def get_lon(self, gps_ifd):
        gps_lon = gps_ifd.get(ExifTags.GPS.GPSLongitude)
        gps_lon_ref = gps_ifd.get(ExifTags.GPS.GPSLongitudeRef)
        return self.convert_lon_coords(gps_lon, gps_lon_ref)

    def get_exif(self, image):
        try:
            return image.getexif()
        except Exception as e:
            logger.error(f"{__name__}: Error getting exif from image: {e}")
            return None

    def get_gps_ifd(self, exif):
        try:
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            return gps_ifd
        except Exception as e:
            logger.error(f"{__name__}: Error processing image: {e}")
            return None

    @staticmethod
    def from_image_bytes(inMemoryUploadedFile):
        pil_image = Image.open(inMemoryUploadedFile)
        return ImageGps(pil_image)
        # try:
        #     pil_image = Image.open(inMemoryUploadedFile)
        #     return ImageGps(pil_image)
        # except Exception as e:
        #     logger.error(
        #         f"{__name__}: Error getting PilImage: {type(e)}: {e.__str__()}"
        #     )
        #     return None

    @staticmethod
    def convert_lat_coords(gps_lat, gps_lat_ref):
        lat_dms = gps_lat
        lat_ref = gps_lat_ref
        latitude = ImageGps.convert_to_degrees(lat_dms)
        if lat_ref == "S":
            latitude = -latitude
        return latitude

    @staticmethod
    def convert_lon_coords(gps_lon, gps_lon_ref):
        lon_dms = gps_lon
        lon_ref = gps_lon_ref
        longitude = ImageGps.convert_to_degrees(lon_dms)
        if lon_ref == "W":
            longitude = -longitude
        return longitude

    @staticmethod
    def convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1]) / 60
        s = float(value[2]) / 3600
        return d + m + s
