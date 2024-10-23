from django.contrib import admin
from django.urls import path
from srch import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hhelper/indicators/', views.IndicatorsCreateView.as_view()),
    path('hhelper/registration/', views.StaffRegistrationView.as_view(), name='registration'),
    path('hhelper/stafflog/', views.StaffLogView.as_view(), name='get_staff'),
    path('hhelper/tasks/', views.TasksDetailView.as_view(), name='get_tasks'),
    path('hhelper/createtask/', views.TaskCreateView.as_view(), name='create_tasks'),
    path('hhelper/showresponses/', views.ResponsesView.as_view()),
    path('hhelper/makequestions/', views.QuestionsView.as_view())
]
