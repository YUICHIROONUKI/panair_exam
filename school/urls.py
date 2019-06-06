from django.urls import path

from . import views

app_name = 'school'
urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customers, name='customers'),
    path('new_user/', views.new_user, name='new_user'),
    path('create_user/', views.create_user, name='create_user'),
    path('edit_user/<int:id>', views.edit_user, name='edit_user'),
    path('lesson_records/', views.lesson_records, name='lesson_records'),
    path('new_record/', views.new_record, name='new_record'),
    path('edit_record/<int:id>', views.edit_record, name='edit_record'),
    path('billings/', views.billings, name='billings'),
    path('report/', views.report, name='report'),
]