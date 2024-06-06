from django.db import models


class NotificationResponseID(models.Model):
    """
    Model to store the notification response id.

    This is used to track the status of the notification asynchronously, i.e. whether it was delivered/failed
    """

    id = models.CharField(max_length=36, primary_key=True)
