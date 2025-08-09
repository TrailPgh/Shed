import logging

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


class ImageGps:
    def __init__(self, lat, lon, altitude):
        self.lat = lat
        self.lon = lon
        self.altitude = altitude

    # @staticmethod
    def from_image_bytes(inMemoryUploadedFile):
        try:
            # logger.info(
            #     f"inMemoryUploadedFile: {type(inMemoryUploadedFile)}: {inMemoryUploadedFile.__repr__()}"
            # )
            image = Image.open(inMemoryUploadedFile)
            # logger.info(f"image: {type(image)}: {image.__repr__()}")

            exif = image.getexif()
            if exif is None:
                # image has no exif data
                return None
            # logger.info(f"exif_data: {type(exif)}: {exif.__repr__()}")

            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if gps_ifd is None:
                # image has no GPS info
                return None
            logger.info(
                f"gps_ifd: {type(gps_ifd)}: gps_ifd[ExifTags.GPS.GPSLongitude]: {gps_ifd[ExifTags.GPS.GPSLongitude]}"
            )

        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    # @staticmethod
    # def from_dict(data):
    #     return ImageGps(data["lat"], data["lon"], data["altitude"])


# def from_image_bytes(image_bytes):
#     # return ImageGps()
#     return None
