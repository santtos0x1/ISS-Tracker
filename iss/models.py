from django.db import models
from django.db.models import CharField, FloatField

class IssDumpInfoModel(models.Model):
    velocity = CharField(max_length=40)
    altitude = CharField(max_length=30)
    visibility = CharField(max_length=30)
    longitude = FloatField(max_length=50)
    latitude = FloatField(max_length=50)

    def __str__(self):
        return self.velocity