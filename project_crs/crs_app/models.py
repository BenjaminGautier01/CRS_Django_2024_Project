
from django.utils import timezone
from django.db import models


# Create your models here.
class Message(models.Model):
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=150)
    message = models.TextField()
    sent_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.full_name


class CandlestickPattern(models.Model):
    candlestick_pattern_name = models.CharField(max_length=150)
    candlestick_image = models.ImageField()
    candlestick_pattern_text = models.TextField(max_length=500)

    def __str__(self):
        return self.candlestick_pattern_name
