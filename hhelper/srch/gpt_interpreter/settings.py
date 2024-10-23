from srch.gpt_interpreter.yandex_gpt import YandexGPTConfigManagerForAPIKey


class Settings:

    def __init__(self, catalog_id="b1ggortl5q1ss3iehd1c", api_key="AQVNwIbx4Px8Rx5dwZE7l3PXAtpapTO_qIp9p56-",
                 model_name="yandexgpt"):
        # Инициализируем конфиг для GPT и создаём YandexGPTThread
        self.config_manager = YandexGPTConfigManagerForAPIKey(model_name, catalog_id,
                                                              api_key)

    def get_config(self):
        return self.config_manager
