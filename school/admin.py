from django.contrib import admin
from .models import Subject, Customer, Record
# Register your models here.
admin.site.register(Subject)
admin.site.register(Customer)
admin.site.register(Record)