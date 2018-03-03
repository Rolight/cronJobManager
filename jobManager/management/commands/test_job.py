import datetime
import json
import pprint

from django.core.management.base import BaseCommand, CommandError

from jobManager.models import Job
from jobManager.core import Scheduler


class Command(BaseCommand):
    help = 'Test single job'

    def add_arguments(self, parser):
        parser.add_argument('margs', nargs='+', type=str)

    def handle(self, *args, **options):
        option = options['margs']
        module_name = option[0]
        args = option[1:]
        kwargs = {}
        while len(args) > 0:
            kwargs[args[0]] = args[1]
            args = args[2:]
        print(module_name)
        pprint.pprint(kwargs)
        job = Job.objects.create(
            job_name=module_name,
            module_name=module_name,
            job_args=json.dumps(kwargs),
            run_at=datetime.datetime.now() + datetime.timedelta(seconds=5)
        )
        sch = Scheduler(jobs=[job])
        sch.run()
