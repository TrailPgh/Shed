import logging

from django.core.mail import send_mail
from django.core.mail.message import sanitize_address

from shed.settings import DEFAULT_FROM_EMAIL

logger = logging.getLogger(__name__)


class EmailReply:
    email_from = DEFAULT_FROM_EMAIL

    def __init__(
        self,
        email_to: str = None,
        subject: str = None,
        short_desc: str = None,
    ):
        self.email_to = sanitize_address(email_to, "utf-8")
        self.subject = subject
        self.short_desc = short_desc
        self.body_text = (
            f"We received your email.\n\nHere is what we found: {self.short_desc}\n"
        )
        logger.info(f"{__name__}.__init__: {self.__dict__}")

    def send(self):
        send_mail(
            self.subject,
            self.body_text,
            self.email_from,
            [self.email_to],
            fail_silently=False,
        )
