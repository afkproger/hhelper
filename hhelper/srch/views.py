import asyncio
import os

from django.http import HttpResponse
from rest_framework.response import Response
import json
from django.http import JsonResponse
from hhelper import settings
from .models import StaffMembers, Indicators, Tasks, Profession
from .serializers import StaffSerializer, IndicatorsSerializer, StaffLogSerializer, TaskSerializer, StaffTaskSerializer, \
    ResponsesProfilesSerializers
from rest_framework.views import APIView


def index(request):
    return HttpResponse("Начало положено")


class TaskCreateView(APIView):
    def post(self, request):
        staff_pk = request.data.get('staff_pk')
        description = request.data.get('description')

        try:
            staff_member = StaffMembers.objects.get(id=staff_pk)
            print(staff_member)
            task = Tasks.objects.create(description=description, staff_member=staff_member)
            return Response(TaskSerializer(task).data)
        except StaffMembers.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=404)


class TasksDetailView(APIView):
    def post(self, request):
        staff_id = request.data.get('staff_id')

        try:
            staff_member = StaffMembers.objects.get(id=staff_id)
            return Response(StaffTaskSerializer(staff_member).data)
        except StaffMembers.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=404)


class TaskDeleteView(APIView):
    def post(self, request):
        task_id = request.data.get("task_id")
        try:
            Tasks.objects.get(id=task_id).delete()
            return Response({'success': True})
        except Tasks.DoesNotExist:
            return Response({'error': 'Task member not found'}, status=404)


class QuestionsView(APIView):
    def post(self, request):
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

        # gpt_interpreter = MakeQuestions(response_data)
        # questions = gpt_interpreter.get_response()
        # return Response(questions)
        return Response(response_data)


class StaffRegistrationView(APIView):
    def post(self, request):
        staff = StaffSerializer(data=request.data)

        try:
            staff.is_valid(raise_exception=True)
            staff.save()
            return Response({'success': True})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=400)


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


class IndicatorsCreateView(APIView):
    def get(self, request):
        indicators = Indicators.objects.all()
        return Response(IndicatorsSerializer(indicators, many=True).data)

    def post(self, request):
        indicators = request.data.get('indicators')
        try:
            for indicator in indicators:
                Indicators.objects.create(name=indicator['name'])  # Изменено здесь
            return Response({'ans': 'Создано успешно'})

        except Exception as e:
            return Response({'error': f'Ошибка при создании: {str(e)}'}, status=400)  # Улучшено сообщение об ошибке


class SearchView(APIView):
    def get(self, request):
        json_file_path = os.path.join(settings.BASE_DIR, 'srch', 'example_data', 'search_candidate_data.json')

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return JsonResponse(data, status=200)

        except FileNotFoundError:
            return JsonResponse({"error": "File not found."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)


class ResponsesView(APIView):
    def get(self, request):
        try:
            resp_profiles = Profession.objects.all()
            return Response(ResponsesProfilesSerializers(resp_profiles, many=True).data)
        except Exception as ex:
            return Response({'error': ex})
