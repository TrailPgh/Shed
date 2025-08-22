from unittest.mock import patch, MagicMock

from PIL import ExifTags as PIL_ExifTags
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.test import TestCase, RequestFactory, SimpleTestCase

from . import views


class ViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # --- rcv_image_html ---

    def test_rcv_image_html_get_renders(self):
        request = self.factory.get("/gps/rcv_image_html")
        response = views.rcv_image_html(request)
        self.assertEqual(response.status_code, 200)

    def test_rcv_image_html_post_with_valid_image_sets_lat_lon(self):
        # Prepare a fake uploaded file
        file_bytes = b"fake-image-bytes"
        uploaded = SimpleUploadedFile(
            "photo.jpg", file_bytes, content_type="image/jpeg"
        )

        # Mock ImageGps.from_image_bytes to return an object with lat/lon
        mock_image = MagicMock()
        mock_image.lat = 37.42
        mock_image.lon = -122.08

        with patch.object(views.ImageGps, "from_image_bytes", return_value=mock_image):
            post_data = QueryDict(mutable=True)
            post_data.update({"file": uploaded})
            request = self.factory.post("/gps/rcv_image_html", data=post_data)
            response = views.rcv_image_html(request)
            self.assertEqual(response.status_code, 200)
            # Check the rendered content includes coordinates (the view logs and sets context with lat/lon)
            self.assertIn(b"37.42", response.content)
            self.assertIn(b"-122.08", response.content)

    # --- rcv_image_mms ---

    def test_rcv_image_mms_get_renders(self):
        # For GET, the view renders a template (no Twilio creds needed)
        request = self.factory.get("/gps/image_via_mms")
        response = views.rcv_image_mms(request)
        self.assertEqual(response.status_code, 200)

    def test_rcv_image_mms_post_no_media_returns_empty_response(self):
        # Patch Twilio creds defined at module import time
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):
            # Fake MessagingResponse to avoid requiring twilio package
            class FakeMsgResp:
                def __init__(self):
                    self.messages = []

                def message(self, text):
                    self.messages.append(text)

                def __str__(self):
                    # Mimic TwiML serialization
                    return "<Response>{}</Response>".format(
                        "".join(f"<Message>{m}</Message>" for m in self.messages)
                    )

            with patch.object(views, "MessagingResponse", FakeMsgResp):
                post_data = {
                    "To": "+15551234567",
                    "From": "+15557654321",
                    "NumMedia": "0",
                    "Body": "hello",
                }
                request = self.factory.post("/gps/image_via_mms", data=post_data)
                response = views.rcv_image_mms(request)
                self.assertEqual(response.status_code, 200)
                # No media should produce an empty response (no <Message> tags)
                self.assertIn(b"<Response>", response.content)
                self.assertNotIn(b"<Message>", response.content)

    def test_rcv_image_mms_post_with_image_and_gps_replies_with_coords(self):
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):

            class FakeMsgResp:
                def __init__(self):
                    self.messages = []

                def message(self, text):
                    self.messages.append(text)

                def __str__(self):
                    return "<Response>{}</Response>".format(
                        "".join(f"<Message>{m}</Message>" for m in self.messages)
                    )

            # Mock network retrieval of media
            fake_resp = MagicMock()
            fake_resp.status_code = 200
            fake_resp.content = b"binary-image-contents"

            mock_image = MagicMock()
            mock_image.lat = 40.0
            mock_image.lon = -75.0

            with patch.object(views, "MessagingResponse", FakeMsgResp), patch(
                "requests.get", return_value=fake_resp
            ), patch.object(
                views.ImageGps, "from_image_bytes", return_value=mock_image
            ):
                post_data = {
                    "To": "+15551234567",
                    "From": "+15557654321",
                    "NumMedia": "1",
                    "Body": "photo",
                    "MediaUrl0": "https://example.com/media/image.jpg",
                }
                request = self.factory.post("/gps/image_via_mms", data=post_data)
                response = views.rcv_image_mms(request)
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    b"Image received, GPS coords detected: 40.0, -75.0",
                    response.content,
                )

    # --- rcv_image_email ---

    def test_rcv_image_email_get_renders(self):
        request = self.factory.get("/gps/image_via_email")
        response = views.rcv_image_email(request)
        self.assertEqual(response.status_code, 200)

    def test_rcv_image_email_post_no_attachment(self):
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):
            # Avoid sending an actual email
            with patch.object(views.EmailReply, "send", return_value=None):
                post_data = {
                    "to": "gps@example.com",
                    "from": "user@example.com",
                    "subject": "No attachment",
                    "text": "",
                    "html": "",
                    "attachments": "0",
                    "attachment-info": "",
                }
                request = self.factory.post("/gps/image_via_email", data=post_data)
                response = views.rcv_image_email(request)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"No attachment detected.", response.content)

    def test_rcv_image_email_post_with_image_and_gps(self):
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):
            with patch.object(views.EmailReply, "send", return_value=None):
                uploaded = SimpleUploadedFile(
                    "photo.jpg", b"fake-image", content_type="image/jpeg"
                )
                mock_image = MagicMock()
                mock_image.lat = 12.34
                mock_image.lon = 56.78
                mock_image.__class__ = views.ImageGps

                with patch.object(
                    views.ImageGps, "from_image_bytes", return_value=mock_image
                ):
                    post_data = {
                        "to": "gps@example.com",
                        "from": "user@example.com",
                        "subject": "Here is a photo",
                        "text": "",
                        "html": "",
                        "attachments": "1",
                        "attachment-info": "{}",
                    }
                    request = self.factory.post(
                        "/gps/rcv_image_email",
                        data=post_data,
                        FILES={"attachment1": uploaded},
                    )
                    request.FILES["attachment1"] = uploaded
                    response = views.rcv_image_email(request)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        b"GPS latitude, longitude: 12.34, 56.78", response.content
                    )

    def test_rcv_image_email_post_with_non_image_attachment(self):
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):
            with patch.object(views.EmailReply, "send", return_value=None):
                uploaded = SimpleUploadedFile(
                    "doc.txt", b"not-an-image", content_type="text/plain"
                )
                with patch.object(
                    views.ImageGps, "from_image_bytes", return_value=None
                ):
                    post_data = {
                        "to": "gps@example.com",
                        "from": "user@example.com",
                        "subject": "Non-image",
                        "text": "",
                        "html": "",
                        "attachments": "1",
                        "attachment-info": "{}",
                    }
                    request = self.factory.post(
                        "/gps/image_via_email",
                        data=post_data,
                        FILES={"attachment1": uploaded},
                    )
                    request.FILES["attachment1"] = uploaded
                    response = views.rcv_image_email(request)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        b"Attached media does not appear to be an image.",
                        response.content,
                    )

    def test_rcv_image_email_post_with_image_but_no_gps(self):
        with patch.object(views, "TWILIO_ACCOUNT_SID", "sid"), patch.object(
            views, "TWILIO_AUTH_TOKEN", "token"
        ):
            with patch.object(views.EmailReply, "send", return_value=None):
                uploaded = SimpleUploadedFile(
                    "photo.jpg", b"fake-image", content_type="image/jpeg"
                )
                mock_image = MagicMock()
                mock_image.lat = None
                mock_image.lon = None
                mock_image.__class__ = views.ImageGps
                with patch.object(
                    views.ImageGps, "from_image_bytes", return_value=mock_image
                ):
                    post_data = {
                        "to": "gps@example.com",
                        "from": "user@example.com",
                        "subject": "No GPS",
                        "text": "",
                        "html": "",
                        "attachments": "1",
                        "attachment-info": "{}",
                    }
                    request = self.factory.post(
                        "/gps/image_via_email",
                        data=post_data,
                        FILES={"attachment1": uploaded},
                    )
                    request.FILES["attachment1"] = uploaded
                    response = views.rcv_image_email(request)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b"GPS info missing or incomplete.", response.content)

    # --- get_inputs_from_email ---

    def test_get_inputs_from_email_reads_post_fields(self):
        post_data = {
            "to": "gps@example.com",
            "from": "user@example.com",
            "subject": "subj",
            "text": "body",
            "html": "<p>body</p>",
            "attachments": "2",
            "attachment-info": '{"attachment1":{}}',
        }
        request = self.factory.post("/gps/image_via_email", data=post_data)
        result = views.get_inputs_from_email(request)
        self.assertEqual(
            result,
            (
                "gps@example.com",
                "user@example.com",
                "subj",
                "body",
                "<p>body</p>",
                2,
                '{"attachment1":{}}',
            ),
        )

    # --- result_message ---

    def test_result_message_success(self):
        msg = views.result_message(views.EmailProcessState.Success, lat=1.23, lon=4.56)
        self.assertEqual(msg, "GPS latitude, longitude: 1.23, 4.56")

    def test_result_message_no_attachment(self):
        msg = views.result_message(views.EmailProcessState.NoAttachment)
        self.assertEqual(msg, "No attachment detected.")

    def test_result_message_unsupported_state_raises(self):
        # EmailProcessState.Unset is not mapped and should raise KeyError
        with self.assertRaises(KeyError):
            views.result_message(views.EmailProcessState.Unset)


class ImageGpsTests(SimpleTestCase):
    def test_dms_tuple_to_decimal(self):
        from .lib.ImageGps import ImageGps

        # 10° 30' 0" = 10.5
        self.assertAlmostEqual(
            ImageGps.dms_tuple_to_decimal((10, 30, 0)), 10.5, places=6
        )
        # 0° 0' 30" = 0.008333...
        self.assertAlmostEqual(
            ImageGps.dms_tuple_to_decimal((0, 0, 30)), 0.0083333, places=6
        )

    def test_convert_dms_to_dd_applies_refs(self):
        from .lib.ImageGps import ImageGps

        # N/E keeps positive
        lat, lon = ImageGps.convert_dms_to_dd((37, 25, 12), "N", (122, 4, 48), "E")
        self.assertAlmostEqual(lat, 37.42, places=2)
        self.assertAlmostEqual(lon, 122.08, places=2)
        # S/W makes negative
        lat, lon = ImageGps.convert_dms_to_dd((37, 25, 12), "S", (122, 4, 48), "W")
        self.assertAlmostEqual(lat, -37.42, places=2)
        self.assertAlmostEqual(lon, -122.08, places=2)

    def test_get_lat_lon_extracts_and_converts(self):
        from .lib.ImageGps import ImageGps

        g = PIL_ExifTags.GPS
        gps_ifd = {
            g.GPSLatitude: (37, 25, 12),
            g.GPSLongitude: (122, 4, 48),
            g.GPSLatitudeRef: "N",
            g.GPSLongitudeRef: "W",
        }
        img = ImageGps(pil_image=None)
        lat, lon = img.get_lat_lon(gps_ifd)
        self.assertAlmostEqual(lat, 37.42, places=2)
        self.assertAlmostEqual(lon, -122.08, places=2)

    def test_get_exif_success_and_failure(self):
        from .lib.ImageGps import ImageGps

        # Success path
        image_mock = MagicMock()
        exif_mock = MagicMock()
        image_mock.getexif.return_value = exif_mock
        img = ImageGps(pil_image=None)
        self.assertIs(img.get_exif(image_mock), exif_mock)
        # Failure path
        image_mock.getexif.side_effect = Exception("boom")
        self.assertIsNone(img.get_exif(image_mock))

    def test_get_gps_ifd_success_and_failure(self):
        from .lib.ImageGps import ImageGps

        exif_mock = MagicMock()
        gps_dict = {"x": 1}
        exif_mock.get_ifd.return_value = gps_dict
        img = ImageGps(pil_image=None)
        self.assertIs(img.get_gps_ifd(exif_mock), gps_dict)
        # Failure path
        exif_mock.get_ifd.side_effect = Exception("gps error")
        self.assertIsNone(img.get_gps_ifd(exif_mock))

    def test_from_image_bytes_success_sets_lat_lon(self):
        from .lib.ImageGps import ImageGps

        g = PIL_ExifTags.GPS

        # Prepare mocks for PIL.Image.open -> image -> exif -> gps_ifd chain
        image_mock = MagicMock()
        exif_mock = MagicMock()
        gps_ifd = {
            g.GPSLatitude: (37, 25, 12),
            g.GPSLongitude: (122, 4, 48),
            g.GPSLatitudeRef: "N",
            g.GPSLongitudeRef: "W",
        }
        exif_mock.get_ifd.return_value = gps_ifd
        image_mock.getexif.return_value = exif_mock

        with patch("gps.lib.ImageGps.Image.open", return_value=image_mock):
            obj = ImageGps.from_image_bytes(b"fake-bytes")
            self.assertIsNotNone(obj)
            self.assertIsInstance(obj, ImageGps)
            self.assertAlmostEqual(obj.lat, 37.42, places=2)
            self.assertAlmostEqual(obj.lon, -122.08, places=2)

    def test_from_image_bytes_failure_returns_none(self):
        from .lib.ImageGps import ImageGps

        with patch("gps.lib.ImageGps.Image.open", side_effect=Exception("bad image")):
            self.assertIsNone(ImageGps.from_image_bytes(b"not-an-image"))
