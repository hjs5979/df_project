from django.db import models

# Create your models here.
class stock(models.Model):
    stock_ticker = models.CharField(max_length=6, primary_key=True)
    stock_name = models.CharField(max_length=50)
    
    # def __str__(self):
    #     return self.subject
    def print_object_details(self):
    # 모델의 메타데이터에서 모든 필드 정보를 가져옵니다.
        fields = self._meta.get_fields()

        # 각 필드의 칼럼명과 값을 출력합니다.
        for field in fields:
            column_name = field.column
            value = getattr(self, field.name)
            print(f"{column_name}: {value}")

class user(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True)
    user_name = models.CharField(max_length=20)
    user_password = models.CharField(max_length=1000)
    user_email = models.CharField(max_length=100)
    def print_object_details(self):
    # 모델의 메타데이터에서 모든 필드 정보를 가져옵니다.
        fields = self._meta.get_fields()

        # 각 필드의 칼럼명과 값을 출력합니다.
        for field in fields:
            column_name = field.column
            value = getattr(self, field.name)
            print(f"{column_name}: {value}")


class stock_value(models.Model):
    stock_ticker = models.ForeignKey(stock, on_delete=models.CASCADE)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    # stock_ticker = models.CharField(max_length=6)
    # user_id = models.CharField(max_length=20)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_date_close = models.IntegerField(null=True)
    end_date_close = models.IntegerField(null=True)
    quantity = models.IntegerField(null=True)
    start_date_close_total = models.IntegerField(null=True)
    end_date_close_total = models.IntegerField(null=True)
    profit_loss = models.IntegerField(null=True)
    return_rate = models.DecimalField(null=True, max_digits=19, decimal_places=4)
    weight = models.DecimalField(null=True, max_digits=19, decimal_places=4)
   
    # 모델의 메타데이터에서 모든 필드 정보를 가져옵니다.
    def print_object_details(self):
    # 모델의 메타데이터에서 모든 필드 정보를 가져옵니다.
        fields = self._meta.get_fields()

        # 각 필드의 칼럼명과 값을 출력합니다.
        for field in fields:
            column_name = field.column
            value = getattr(self, field.name)
            print(f"{column_name}: {value}")

    class Meta:
        unique_together = (('stock_ticker', 'user_id'),)

class stock_timestamp(models.Model):
    date = models.DateField()
    close = models.IntegerField()
    change = models.DecimalField(max_digits=19, decimal_places=6)
    stock_ticker = models.CharField(max_length=6)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('stock_ticker', 'user_id', 'date'),)
# class stock_value(models.Model):
#     ticker = models.TextField()
#     stock_name = models.TextField()
#     startDate = models.DateField(null=True)
#     endDate = models.DateField(null=True)
#     startDate_close = models.IntegerField(null=True)
#     endDate_close = models.IntegerField(null=True)
#     quantity = models.IntegerField(null=True)
#     start_value = models.IntegerField(null=True)
#     end_value = models.IntegerField(null=True)
#     ugl = models.IntegerField(null=True)
#     return_rate = models.DecimalField(null=True, max_digits=19, decimal_places=4)
#     weight = models.DecimalField(null=True, max_digits=19, decimal_places=4)

# class result(models.Model):
#     total_start_value = models.IntegerField()
#     total_start_value = models.IntegerField()
#     pf_err = models.DecimalField(max_digits=19, decimal_places=4)
#     pf_risk = models.DecimalField(max_digits=19, decimal_places=4)
#     total_ugl = models.IntegerField()
#     total_rr = models.DecimalField(max_digits=19, decimal_places=4)
    
    
    
    
    