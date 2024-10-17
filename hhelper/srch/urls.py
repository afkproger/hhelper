from django.contrib import admin
from django.urls import path
from srch import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hhelper/indicators', views.IndicatorView.as_view(), name='indicators'),
    path('hhelper/registration', views.StaffRegistrationView.as_view(), name='registration'),
    path('hhelper/stafflog', views.StaffLogView.as_view(), name='get_staff'),
    path('hhelper/tasks/<int:staff_id>/', views.TasksView.as_view(), name='get_tasks_for_staff'),
    path('hhelper/tasks', views.TasksView.as_view(), name='create_task'),
]
