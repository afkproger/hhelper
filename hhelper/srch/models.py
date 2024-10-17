from django.db import models
import uuid


class Indicators(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StaffMembers(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    login = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    indicators = models.ManyToManyField(Indicators, blank=True)

    def __str__(self):
        return self.full_name


class Tasks(models.Model):
    job_title = models.CharField(max_length=255)  # Название работы (например, программист, менеджер и т.д.)
    description = models.TextField()  # Описание задачи
    assigned_to = models.ForeignKey(StaffMembers, on_delete=models.CASCADE,
                                    related_name='tasks')  # Внешний ключ к сотруднику
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания задачи
    updated_at = models.DateTimeField(auto_now=True)  # Дата последнего обновления задачи

    def __str__(self):
        return self.job_title