import asyncio
import os
import random
from django.http import HttpResponse
from django.template.defaultfilters import title
from rest_framework.response import Response
import json
from django.http import JsonResponse
from hhelper import settings
from .gpt_interpreter.make_questions import MakeQuestions
from .models import StaffMembers, Indicators, Tasks, Profession, StaffProfessionIndicators, Profile, StaffProfilesScores
from .serializers import StaffSerializer, IndicatorsSerializer, StaffLogSerializer, TaskSerializer, StaffTaskSerializer, \
    ResponsesProfilesSerializers
from rest_framework.views import APIView
from srch.gpt_interpreter.vk_parse import Parsing, PersonAnalysis
from .calculate.effectivenesscalculator import Score


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
        profession_id = request.data.get('profession_id')
        staff_member_id = request.data.get('staff_id')  # или получите ID из данных запроса, если это необходимо
        try:
            # Получаем профессию по profession_id
            profession = Profession.objects.get(id=profession_id)

            # Извлекаем связанные индикаторы для конкретного сотрудника и профессии
            indicators = StaffProfessionIndicators.objects.filter(
                staff_member_id=staff_member_id,
                profession=profession
            ).select_related('indicator')

            # Извлекаем названия показателей
            indicator_names = [indicator.indicator.name for indicator in indicators]

            # Формируем ответ в нужном формате
            response_data = {
                "indicators": indicator_names,
                "job_title": profession.title
            }

            # return Response(response_data)

            gpt_interpreter = MakeQuestions(response_data)
            questions = gpt_interpreter.get_response()
            return Response({'questions': questions})

        except Profession.DoesNotExist:
            return Response({"error": "Profession not found."}, status=404)


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
    def post(self, request):
        profession_title = request.data.get('profession_title')
        try:
            resp_profiles = Profession.objects.filter(title=profession_title)
            print(resp_profiles)
            return Response(ResponsesProfilesSerializers(resp_profiles, many=True).data)
        except Exception as ex:
            return Response({'error': ex})


class ProfessionIndicatorsSetupView(APIView):
    def post(self, request):
        staff_member_id = request.data.get('staff_id')
        profession_id = request.data.get('profession_id')
        indicator_ids = request.data.get('indicators', [])

        try:
            profession = Profession.objects.get(id=profession_id)
            indicators = Indicators.objects.filter(id__in=indicator_ids)

            # Удаляем все старые записи для данного сотрудника и профессии
            StaffProfessionIndicators.objects.filter(staff_member_id=staff_member_id,
                                                     profession=profession).delete()

            # Создаем новые записи в промежуточной таблице
            for indicator in indicators:
                StaffProfessionIndicators.objects.create(
                    staff_member_id=staff_member_id,
                    profession=profession,
                    indicator=indicator
                )

            return Response({"message": "Indicators successfully added to the profession."}, status=200)

        except Profession.DoesNotExist:
            return Response({"error": "Profession not found."}, status=404)

        except Indicators.DoesNotExist:
            return Response({"error": "Some indicators were not found."}, status=404)


class CalculationScoreView(APIView):
    def post(self, request):
        staff_id = request.data.get('staff_id')
        profession_id = request.data.get('profession_id')
        try:
            # Получаем профессию по profession_id
            profession = Profession.objects.get(id=profession_id)

            # Извлекаем связанные индикаторы для конкретного сотрудника и профессии
            indicators = StaffProfessionIndicators.objects.filter(
                staff_member_id=staff_id,
                profession=profession
            ).select_related('indicator')

            profiles_data = Profile.objects.filter(profession=profession).values_list('id', 'vk_id')
            # Преобразуем в словарь с ключами vk_id и значениями id
            profiles_dict = {vk_id: profile_id for profile_id, vk_id in profiles_data}
            indicator_names = [indicator.indicator.name for indicator in indicators]

            indicators_data = {
                "indicators": indicator_names
            }
            response_data = {
                "created_scores": []
            }

            for vk_id in profiles_dict.keys():
                parser = Parsing(int(vk_id))
                indicators_value = PersonAnalysis(user_info=parser.parse_user_info(),
                                                  subscriptions=parser.parse_subscriptions(),
                                                  posts=parser.parse_user_posts(), data=indicators_data)
                # indicators_value = [random.uniform(-1, 1) for _ in range(3)]
                score = int((1 / Score.get_score(indicators_value.get_response())) * 100)
                profile_id = profiles_dict.get(vk_id)

                # Проверка наличия profile_id перед созданием записи
                if profile_id is not None:
                    created_score = StaffProfilesScores.objects.create(
                        staff_member_id=staff_id,
                        profile_id=profile_id,
                        score=score
                    )
                    # Добавляем данные созданной записи в response_data
                    response_data["created_scores"].append({
                        "staff_member_id": created_score.staff_member_id,
                        "profile_id": created_score.profile_id,
                        "score": created_score.score
                    })
                else:
                    response_data["created_scores"].append({
                        "error": f"Profile not found for vk_id {vk_id}"
                    })

            return Response(response_data)
        except Profession.DoesNotExist:
            return Response({"error": "Profession not found."}, status=404)


class ProfessionProfileScoresView(APIView):
    def post(self, request):
        staff_id = request.data.get('staff_id')
        profession_id = request.data.get('profession_id')

        # Проверяем, что идентификаторы переданы
        if not staff_id or not profession_id:
            return JsonResponse({"error": "Missing staff_id or profession_id."}, status=400)

        try:
            # Получаем профессию и проверяем, что она существует
            profession = Profession.objects.get(id=profession_id)

            # Получаем профили, связанные с профессией
            profiles = Profile.objects.filter(profession=profession).prefetch_related('staffprofilesscores_set')

            response_data = {
                "profession": {
                    "id": profession.id,
                    "title": profession.title,
                },
                "profiles": []
            }

            # Для каждого профиля получаем его данные и score
            for profile in profiles:
                # Получаем score для конкретного сотрудника и профиля
                score_entry = StaffProfilesScores.objects.filter(
                    staff_member_id=staff_id,
                    profile=profile
                ).first()

                profile_data = {
                    "profile_id": profile.id,
                    "profile_name": profile.name,
                    "vk_url": profile.vk_url,
                    "hh_url": profile.hh_url,
                    "score": int(score_entry.score) if score_entry else None  # Отбрасываем значения после точки
                }
                response_data["profiles"].append(profile_data)

            return JsonResponse(response_data)

        except Profession.DoesNotExist:
            return JsonResponse({"error": "Profession not found."}, status=404)
