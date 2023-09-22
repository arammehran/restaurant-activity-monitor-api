from django.db import models


class Store(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=100, default="America/Chicago")

    @classmethod
    def get_store_or_none(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return self.name


class BusinessHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 0=Monday, 6=Sunday
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    def __str__(self):
        return self.store.name


class StoreStatus(models.Model):
    activity_choices = [
        ("active", "active"),
        ("inactive", "inactive"),
    ]
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10, choices=activity_choices, default="inactive")

    def __str__(self):
        return "{} -> {}".format(self.store.name, self.status)
