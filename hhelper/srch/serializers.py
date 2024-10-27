import io

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import StaffMembers, Tasks, Indicators, Profile, Profession


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['id', 'description', 'created_at']


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


class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name', 'vk_url', 'vk_id', 'hh_url')


class ResponsesProfilesSerializers(serializers.ModelSerializer):
    profiles = ProfileSerializers(many=True, read_only=True)

    class Meta:
        model = Profession
        fields = ('id', 'title', 'profiles')

