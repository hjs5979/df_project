from django.db import models

# Create your models here.
class stock_info(models.Model):
    ticker = models.TextField()
    stock_name = models.TextField()
    
    # def __str__(self):
    #     return self.subject

class stock_ts(models.Model):
    date = models.DateField()
    close = models.IntegerField()
    change = models.DecimalField(max_digits=19, decimal_places=6)
    ticker = models.ForeignKey(stock_info, on_delete=models.CASCADE)
    
class stock_value(models.Model):
    ticker = models.ForeignKey(stock_info, on_delete=models.CASCADE, related_name = 'stock_info_ticker')
    stock_name = models.ForeignKey(stock_info, on_delete=models.CASCADE, related_name = 'stock_info_stock_name')
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    startDate_close = models.IntegerField(null=True)
    endDate_close = models.IntegerField(null=True)
    quantity = models.IntegerField(null=True)
    start_value = models.IntegerField(null=True)
    end_value = models.IntegerField(null=True)
    ugl = models.IntegerField(null=True)
    return_rate = models.DecimalField(null=True, max_digits=19, decimal_places=4)
    weight = models.DecimalField(null=True, max_digits=19, decimal_places=4)

class result(models.Model):
    total_start_value = models.IntegerField()
    total_start_value = models.IntegerField()
    pf_err = models.DecimalField(max_digits=19, decimal_places=4)
    pf_risk = models.DecimalField(max_digits=19, decimal_places=4)
    total_ugl = models.IntegerField()
    total_rr = models.DecimalField(max_digits=19, decimal_places=4)
    
    
    
    
    