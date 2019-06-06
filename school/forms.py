from django import forms
from .models import Customer, Record, Subject
import dateutil
from dateutil.relativedelta import relativedelta
import datetime
today = datetime.date.today()
last_month = datetime.date.today() - relativedelta(months=1)
two_month_ago = datetime.date.today() - relativedelta(months=2)
three_month_ago = datetime.date.today() - relativedelta(months=3)
MONTHS_CHOICE = (
    (str(today)[:-3], str(today.year) + '年' + str(today.month) + '月'),
    (str(last_month)[:-3], str(last_month.year) + '年' + str(last_month.month) + '月'),
    (str(two_month_ago)[:-3], str(two_month_ago.year) + '年' + str(two_month_ago.month) + '月'),
    (str(three_month_ago)[:-3], str(three_month_ago.year) + '年' + str(three_month_ago.month) + '月'),
)
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'sex', 'age']

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['study_date', 'study_hour']
        widgets = {
            'study_date': forms.SelectDateWidget
        }
class MonthForm(forms.Form):
    請求月 = forms.ChoiceField(widget=forms.Select, choices=MONTHS_CHOICE)
