import datetime

from django.db import models


class Job(models.Model):
    job_name = models.CharField(max_length=128)
    log_limits = models.IntegerField(default=1024)
    log = models.TextField()
    # args in JSON format
    job_args = models.TextField(default='{}')
    module_name = models.CharField(max_length=128)
    # job first run at this time of the day
    run_at = models.DateTimeField()
    # job run every specific seconds
    run_every = models.IntegerField(default=24 * 3600)
    # job cannot run more than timeout seconds
    timeout = models.IntegerField(default=3600)

    def __str__(self):
        return self.job_name + ' run_at %d:%d' % (
            self.run_at.hour, self.run_at.minute) \
            + ' run_every: ' + str(self.run_every)

    def save(self, *args, **kwargs):
        lines = self.log.split('\n')
        if len(lines) > self.log_limits:
            lines = lines[len(lines) - self.log_limits:]
        self.log = '\n'.join(lines)
        super().save(*args, **kwargs)

    @property
    def delay(self):
        """
            Calculate how long does it need to delay
        """
        today = datetime.date.today()
        run_at = self.run_at.replace(
            year=today.year, month=today.month, day=today.day)
        return max(run_at.timestamp() - datetime.datetime.now().timestamp(), 0)

    @property
    def log_lines(self):
        return self.log.split('\n')

    def append_log(self, log_str):
        if len(self.log) == 0:
            self.log = log_str
        else:
            self.log += '\n' + log_str
