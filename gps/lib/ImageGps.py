import logging

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


class ImageGps:
    @staticmethod
    def from_image_bytes(inMemoryUploadedFile):
        try:
            pil_image = Image.open(inMemoryUploadedFile)
            return ImageGps(pil_image)
        except Exception as e:
            logger.error(
                f"{__name__}: Error getting PilImage: {type(e)}: {e.__str__()}"
            )
            return None

    def __init__(
        self,
        pil_image: Image = None,
    ):
        self.lat = None
        self.lon = None
        self.exif = None
        self.gps_ifd = None
        self.image = pil_image
        if self.image is None:
            return

        self.exif = self.get_exif(self.image)
        logger.info(f"{__name__}.__init__: exif: {self.exif.__str__()}")
        if self.exif is None or not self.exif:
            return

        self.gps_ifd = self.get_gps_ifd(self.exif)
        logger.info(f"{__name__}.__init__: gps_ifd: {self.gps_ifd.__str__()}")
        if self.gps_ifd is None or not self.gps_ifd:
            return

        self.lat, self.lon = self.get_lat_lon(self.gps_ifd)
        logger.info(f"{__name__}.__init__: {self.__dict__}")

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

    def get_lat_lon(self, gps_ifd):
        lat_dms = gps_ifd.get(ExifTags.GPS.GPSLatitude)
        lon_dms = gps_ifd.get(ExifTags.GPS.GPSLongitude)
        lat_ref = gps_ifd.get(ExifTags.GPS.GPSLatitudeRef)
        lon_ref = gps_ifd.get(ExifTags.GPS.GPSLongitudeRef)
        return self.convert_dms_to_dd(lat_dms, lat_ref, lon_dms, lon_ref)

    ##
    # convert from a tuple of (d, m, s) to decimal degrees
    @staticmethod
    def convert_dms_to_dd(gps_lat, gps_lat_ref, gps_lon, gps_lon_ref):
        latitude = ImageGps.dms_tuple_to_decimal(gps_lat)
        longitude = ImageGps.dms_tuple_to_decimal(gps_lon)
        if gps_lat_ref == "S":
            latitude = -latitude
        if gps_lon_ref == "W":
            longitude = -longitude
        return latitude, longitude

    ##
    # convert from a tuple of (d, m, s) to decimal degrees
    @staticmethod
    def dms_tuple_to_decimal(value):
        d = float(value[0])
        m = float(value[1]) / 60
        s = float(value[2]) / 3600
        return d + m + s
