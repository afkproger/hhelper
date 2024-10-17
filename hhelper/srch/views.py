from django.contrib.auth import authenticate
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from .models import StaffMembers, Indicators
from .serializers import StaffSerializer, IndicatorsSerializer, StaffLogSerializer
from rest_framework.views import APIView


# Create your views here.


def index(request):
    return HttpResponse("Начало положено")


class StaffLogView(APIView):
    def post(self, request):
        staff_login = request.data.get('login', None)
        staff_password = request.data.get('password', None)

        try:
            staff = StaffMembers.objects.get(login=staff_login, password=staff_password)
        except StaffMembers.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=404)

        staff_serialized = StaffLogSerializer(staff).data
        return Response(staff_serialized)


class StaffRegistrationView(APIView):
    def post(self, request):
        staff = StaffSerializer(data=request.data)

        try:
            staff.is_valid(raise_exception=True)
            staff.save()
            return Response({'success': True})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=400)

    def get(self, request, *args, **kwargs):
        staff_login = kwargs.get('login', None)
        if not staff_login:
            return Response({"error": "Method GET not allowed"})

        try:
            staff = StaffMembers.objects.get(login=staff_login)
        except StaffMembers.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=404)

        staff_serialized = StaffSerializer(staff).data
        return Response({'staff': staff_serialized})

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method PUT not allowed"})

        try:
            instance = StaffMembers.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exist"})

        serializer = StaffSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"put": serializer.data})


class IndicatorView(APIView):
    def get(self, request):
        indicators = Indicators.objects.all()
        serialized_indicators = IndicatorsSerializer(indicators, many=True).data
        return Response({'indicators': serialized_indicators})

    def post(self, request):
        serializer = IndicatorsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'post': serializer.data})
