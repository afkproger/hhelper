import io

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import StaffMembers, Tasks, Indicators


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['id', 'description', 'status']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMembers
        fields = "__all__"


class StaffTaskSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = StaffMembers
        fields = ('login', 'tasks')


class StaffLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMembers
        fields = ['pk', 'full_name', 'login', 'email']


class IndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicators
        fields = ['id', 'name']
