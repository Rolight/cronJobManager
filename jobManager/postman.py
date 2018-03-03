import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(settings.LOGGER_NAME)


def email(receiver, subject, message, html_message=None):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[receiver],
            html_message=html_message
        )
    except Exception as e:
        logger.error('sending email failed. Message: %s' % e)
