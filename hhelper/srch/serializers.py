import io

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import StaffMembers, Indicators


class StaffSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    login = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        return StaffMembers.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.email = validated_data.get("email", instance.email)
        instance.login = validated_data.get("login", instance.login)
        instance.password = validated_data.get("password", instance.password)
        instance.save()

        return instance


class StaffLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMembers
        fields = ['pk', 'full_name']  # Указываем только нужные поля


class IndicatorsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Indicators.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
