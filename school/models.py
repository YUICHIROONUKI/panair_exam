import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
# 顧客を保存するテーブル↓
class Customer(models.Model):
    SEX_CHOICE = (
        ('男', '男'),
        ('女', '女')
    )
    customer_name = models.CharField('名前', max_length=20)
    sex = models.CharField('性別', max_length=1, choices=SEX_CHOICE)
    age = models.IntegerField('年齢', validators=[MinValueValidator(0), MaxValueValidator(100)])
    def __str__(self):
        return self.customer_name
# レッスンのジャンルを保存するテーブル↓
class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    def __str__(self):
        return self.subject_name
# 受講記録を保存するテーブル↓
class Record(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    study_date = models.DateField('受講日')
    study_hour = models.IntegerField('受講時間(h)', validators=[MinValueValidator(1), MaxValueValidator(12)])