from django import forms
from difi.models import stock_value

class DateInput(forms.DateInput):
    input_type = 'date'

class UpperForm(forms.ModelForm):
    class Meta:
        model = stock_value  # 사용할 모델
        fields = ['startDate', 'endDate', 'stock_name', 'ticker']  # QuestionForm에서 사용할 Question 모델의 속성
        widgets = {
            'startDate': DateInput(),
            'endDate' : DateInput(),
        }