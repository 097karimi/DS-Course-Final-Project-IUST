from django.db import models

# Create your models here.

class StockData(models.Model):
    stock_symbol = models.CharField(max_length=10)
    topic = models.CharField(max_length=100)
    signal = models.CharField(max_length=50)
    local_time = models.DateTimeField()
    open = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.BigIntegerField()
    SMA_5 = models.FloatField()
    EMA_10 = models.FloatField()
    delta = models.FloatField()
    gain = models.FloatField()
    loss = models.FloatField()
    avg_gain_10 = models.FloatField()
    avg_loss_10 = models.FloatField()
    rs = models.FloatField()
    RSI_10 = models.FloatField()

    def __str__(self):
        return self.stock_symbol

