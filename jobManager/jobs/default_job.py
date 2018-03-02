"""
    The default job to report the manager is normal runnning.

"""
import datetime

from django.conf import settings

from jobManager.postman import email


def run(*args, **kwargs):
    receiver = settings.ADMIN_EMAIL
    email(
        receiver,
        subject="Daily Report",
        message="今天也正常在运行呢. \n report at %s." % str(datetime.datetime.now())
    )
