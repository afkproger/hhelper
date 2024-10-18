from django.contrib import admin
from .models import StaffMembers, Indicators, Tasks, Question

admin.site.register(StaffMembers)
admin.site.register(Indicators)
admin.site.register(Tasks)
admin.site.register(Question)
