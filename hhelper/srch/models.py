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

    def __str__(self):
        return self.full_name


class Tasks(models.Model):
    description = models.TextField(blank=True)  # Описание задачи
    staff_member = models.ForeignKey(StaffMembers, on_delete=models.CASCADE,
                                     related_name='tasks')  # Внешний ключ к сотруднику
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания задачи

    def __str__(self):
        return self.description


class Profession(models.Model):
    indicators = models.ManyToManyField(Indicators, blank=True)
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=255)
    vk_url = models.URLField(blank=True, null=True)
    vk_id = models.CharField(max_length=255, unique=True)
    hh_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class StaffProfilesScores(models.Model):
    staff_member = models.ForeignKey(StaffMembers, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('staff_member', 'profile', 'score')


class StaffProfessionIndicators(models.Model):
    staff_member = models.ForeignKey(StaffMembers, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicators, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('staff_member', 'profession', 'indicator')

    def __str__(self):
        return f"{self.staff_member.full_name} - {self.profession.title} - {self.indicator.name}"
