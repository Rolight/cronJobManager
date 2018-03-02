from django.db import models


class Job(models.Model):
    job_name = models.CharField(max_length=128)
    log_limits = models.IntegerField(default=1024)
    log = models.TextField()
    # args in JSON format
    job_args = models.TextField()
    module_name = models.CharField(max_length=128)
    # job first run at this time of the day
    run_at = models.DateTimeField()
    # job run every specific seconds
    run_every = models.IntegerField(default=24 * 3600)
    notification_method = models.CharField(max_length=64, default='email', choices=(
        ('email', 'email'),
    ))
    notification_args = models.TextField()
