import os
import json
from django.conf import settings
from srch.models import Profession, Profile


def load_data():
    json_file_path = os.path.join(settings.BASE_DIR, 'srch', 'example_data', 'responses_candidates_data.json')
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for category_data in data['categories']:
            category, created = Profession.objects.get_or_create(title=category_data['title'])
            for profile_data in category_data['profiles']:
                Profile.objects.get_or_create(
                    profession=category,  # Изменил category на profession
                    name=profile_data['name'],
                    vk_url=profile_data.get('vk_url', ''),  # Установка пустой строки по умолчанию
                    vk_id=profile_data['vk_id'],
                    hh_url=profile_data.get('hh_url', ''),  # Установка пустой строки по умолчанию
                    score=profile_data.get('score', 0)  # Установка 0 по умолчанию
                )
#python manage.py shell и вот так грузим


