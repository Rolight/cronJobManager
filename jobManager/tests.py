import datetime
import time
import threading
from unittest import mock

from django.test import TestCase, TransactionTestCase
from django.conf import settings

from jobManager.postman import email
from jobManager import models, core


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


class ModelTest(TestCase):

    def setUp(self):
        self.job = models.Job.objects.create(
            job_name='test_job',
            run_at=datetime.datetime.now(),
            timeout=1000)

    def tearDown(self):
        models.Job.objects.all().delete()

    def test_log(self):
        self.job.log_limits = 10
        for i in range(8):
            self.job.append_log('aaa')
        self.job.save()

        self.job = models.Job.objects.get(id=self.job.id)
        self.assertEqual(self.job.log_lines, ['aaa'] * 8)

        for i in range(8):
            self.job.append_log('aaa')
        self.job.save()

        self.job = models.Job.objects.get(id=self.job.id)
        self.assertEqual(self.job.log_lines, ['aaa'] * 10)


# Fake Jobs

class infinite_delay_job:

    @classmethod
    def run(cls, *args, **kwargs):
        while True:
            time.sleep(10000)


class normal_job:

    @classmethod
    def run(cls, job, *args, **kwargs):
        job.append_log('haohaohao')
        job.save()


class fake_jobs_producer:

    def import_module(job_name):
        print('job_name: ', job_name)
        job_lists = {
            settings.JOB_SCRIPT_PATH.format(
                module_name='infinite_job'): infinite_delay_job,
            settings.JOB_SCRIPT_PATH.format(
                module_name='normal_job'): normal_job
        }
        return job_lists[job_name]


class CoreTest(TransactionTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        models.Job.objects.all().delete()

    @mock.patch('jobManager.core.importlib', fake_jobs_producer)
    def test_schedule_job(self):
        now = datetime.datetime.now()
        normal = models.Job(
            job_name='normal_job',
            run_at=now,
            module_name='normal_job',
            run_every=2,
            timeout=10
        )
        infinite = models.Job(
            job_name='infinite_job',
            run_at=now,
            module_name='infinite_job',
            run_every=1,
            timeout=1
        )

        # test infinite delay task
        infinite.save()
        scheduler = core.Scheduler()
        test_thread = threading.Thread(target=scheduler.run)
        test_thread.start()
        time.sleep(5)
        # suppose only one job still alive
        self.assertEqual(len(scheduler.scheduler.queue), 1)
        scheduler.stopped = True
        test_thread.join()

        # test normal task
        normal.save()
        scheduler = core.Scheduler()
        test_thread = threading.Thread(target=scheduler.run)
        test_thread.start()
        time.sleep(10)
        normal = models.Job.objects.get(id=normal.id)
        print(normal.log)
        self.assertTrue(len(normal.log_lines) > 0)
        scheduler.stopped = True
        test_thread.join()
