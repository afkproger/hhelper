import asyncio
from srch.gpt_interpreter.yandex_gpt import YandexGPTThread


class MakeQuestions:

    def __init__(self, config_manager, data):
        self.job_title = None
        self.config_manager = config_manager
        self.data = data

    def prepare_data(self):
        self.indicators = []

        for indicator in self.data['indicators']:
            self.indicators.append(indicator)

        self.job_title = self.data['job_title']

    def prepare_gpt_messages(self):
        user_input = (
            f"У нас есть ряд показателей, которые важны для должности {self.job_title}: {', '.join(self.indicators)}.\n"
            "Сформируй список вопросов, которые можно задать специалисту на собеседовании для оценки каждого показателя.\n"
            "Ответ должен быть строкой, где вопросы идут через запятую. Всего 3 вопроса."
        )

        system_message = (
            "Вы — AI-ассистент, который помогает составить вопросы для собеседования. "
            "На основе указанных показателей и должности, сформируйте список вопросов. "
            "Ответ должен быть только строкой, где вопросы перечислены через запятую."
        )

        messages = [
            {'role': 'system', 'text': system_message},
            {'role': 'user', 'text': user_input}
        ]
        return messages

    async def get_response(self):
        messages = self.prepare_gpt_messages()

        # Инициализация YandexGPTThread с нужными конфигурациями
        yandex_gpt_thread = YandexGPTThread(config_manager=self.config_manager, messages=messages)

        try:
            await yandex_gpt_thread.run_async()  # Асинхронный запуск GPT
            response_data = yandex_gpt_thread.result()[-1]['text']  # Получение ответа
        except Exception as e:
            response_data = f"Ошибка выполнения GPT: {str(e)}"

        return response_data
