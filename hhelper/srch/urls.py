from django.contrib import admin
from django.urls import path
from srch import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hhelper/indicators/', views.IndicatorView.as_view(), name='indicators'),
    path('hhelper/registration', views.StaffRegistrationView.as_view(), name='registration'),
    path('hhelper/stafflog', views.StaffLogView.as_view(), name='get_staff')
]
