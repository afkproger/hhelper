from django.contrib.auth import authenticate
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import StaffMembers, Indicators, Tasks
from .serializers import StaffSerializer, IndicatorsSerializer, StaffLogSerializer, TaskSerializer
from rest_framework.views import APIView


# Create your views here.


def index(request):
    return HttpResponse("Начало положено")


class TasksView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Сохраняем новую задачу
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Возвращаем созданный объект
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Возвращаем ошибки валидации

    def get(self, request, staff_id):
        try:
            # Получаем все задачи, связанные с данным сотрудником
            tasks = Tasks.objects.filter(assigned_to=staff_id)

            if not tasks.exists():
                return Response({'error': 'Tasks not found'}, status=404)

            serialized_tasks = TaskSerializer(tasks, many=True).data
            return Response(serialized_tasks)
        except StaffMembers.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=404)


class QuestionsView(APIView):
    def post(self, request, task_id):
        job_title = request.data.get('job_title')
        indicator_ids = request.data.get('indicators', [])

        # Получаем показатели по переданным id
        indicators = Indicators.objects.filter(id__in=indicator_ids)

        # Извлекаем названия показателей
        indicator_names = [indicator.name for indicator in indicators]

        # Формируем ответ в нужном формате
        response_data = {
            "indicators": indicator_names,
            "job_title": job_title
        }

        return Response(response_data)


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


class IndicatorView(APIView):
    def get(self, request):
        indicators = Indicators.objects.all()
        serialized_indicators = IndicatorsSerializer(indicators, many=True).data
        return Response(serialized_indicators)

    def post(self, request):
        serializer = IndicatorsSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'post': serializer.data})
