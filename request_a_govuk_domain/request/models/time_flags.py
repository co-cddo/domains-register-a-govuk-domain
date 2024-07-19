from django.db import models


class TimeFlag(models.Model):
    """
    An Admin can change the times on application status, defaults below
    1. More Information more than 5 days change to On-hold.
    2. On-hold more than 60 days change to Closed.
    """

    on_hold_days = models.IntegerField(default=5)
    to_close_days = models.IntegerField(default=60)

    def __str__(self):
        return "More Information and On-hold flags"
