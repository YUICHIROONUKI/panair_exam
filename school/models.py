import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
class Costomer(models.Model):
    costomer_name = models.CharField(max_length=20)
    sex = models.CharField(max_length=1)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    def __str__(self):
        return self.costomer_name

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    def __str__(self):
        return self.subject_name

class Record(models.Model):
    costomer = models.ForeignKey(Costomer, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    study_date = models.DateField('date published')
    study_hour = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])