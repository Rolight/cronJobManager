import sched
import time
import logging
import json
import threading
import datetime

from imp import importlib

from jobManager.models import Job
from django.conf import settings

logger = logging.getLogger(settings.LOGGER_NAME)


class WorkThread(threading.Thread):

    def __init__(self, name, timeout, *args, **kwargs):
        super().__init__()
        self.work_thread = threading.Thread(*args, **kwargs)
        self.work_thread.setDaemon(True)
        self.timeout = timeout
        self.name = name

    def start(self):
        start_time = datetime.datetime.now()
        logger.info('start job %s thread at %s.' % (
            self.name, start_time))
        self.work_thread.start()
        self.work_thread.join(timeout=self.timeout)
        if self.work_thread.is_alive():
            logger.error(
                'job %s(started at %s) runtime reached timeout, force kill it.'
                % (self.name, start_time))
        else:
            logger.info(
                'job %s finished at %s.'
                % (self.name, datetime.datetime.now()))


class Scheduler:

    def __init__(self, jobs=None):
        if jobs is None:
            jobs = Job.objects.all()
        self.stopped = False
        self.init_scheduler(jobs)

    def run_job(self, job, first=True):
        try:
            job = Job.objects.get(pk=job.id)
            job_args = json.loads(job.job_args)
            if not isinstance(job_args, dict):
                raise ValueError('job_args invalid')
            job_script = importlib.import_module(
                settings.JOB_SCRIPT_PATH.format(
                    module_name=job.module_name
                ))

            job_thread = None
            if not first:
                job_thread = WorkThread(
                    name=job.job_name,
                    timeout=job.timeout,
                    target=job_script.run,
                    args=(job, ),
                    kwargs=job_args
                )
                job_thread.start()

            # add next schedule
            self.scheduler.enter(
                delay=job.delay if first else job.run_every,
                priority=settings.JOB_PRIORIRY,
                action=self.run_job,
                argument=(job, False),
            )
            logger.info('schedule job %s success!' % job.job_name)

        except Exception as e:
            logger.error('schedule job %s error: %s' % (
                job.job_name, str(e)
            ))

    def init_scheduler(self, jobs):
        logger.info('Schedule %d Jobs.' % len(jobs))

        self.scheduler = sched.scheduler(time.time, time.sleep)
        for job in jobs:
            self.run_job(job)

        logger.info('Initilize scheduler finished, Job Queue:\n%s' %
                    self.scheduler.queue)

    def run(self, run_every=settings.JOB_TICK_TOCK):
        while True:
            self.scheduler.run(blocking=False)
            if self.stopped:
                break
            time.sleep(run_every)
