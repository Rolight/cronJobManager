from django.core.management.base import BaseCommand, CommandError
from jobManager.core import Scheduler


class Command(BaseCommand):
    help = 'Run all jobs at once.'

    def handle(self, *args, **options):
        sch = Scheduler()
        sch.run()
