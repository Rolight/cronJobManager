from unittest import mock

from django.test import TestCase
from django.conf import settings

from jobManager.postman import email


class PostmanTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_email(self):
        with mock.patch('jobManager.postman.send_mail') as mk:
            call_args = {
                'receiver': 'rolights@163.com',
                'subject': 'haohaohao',
                'message': 'haohaohao',
            }
            expect_args = {
                'subject': call_args['subject'],
                'message': call_args['message'],
                'from_email': settings.EMAIL_HOST_USER,
                'recipient_list': [call_args['receiver']],
                'html_message': None
            }
            email(**call_args)
            mk.assert_called_once_with(**expect_args)
