import os
from typing import Optional

from yandex_gpt.YandexGPTConfigManagerBase import YandexGPTConfigManagerBase


class YandexGPTConfigManagerForAPIKey(YandexGPTConfigManagerBase):
    """
    Class for configuring the YandexGPT model using an API key. It supports setting model type, catalog ID, and API key
    directly or through environment variables. The class allows for configuration flexibility by providing the option to
    use environmental variables for model type (`YANDEX_GPT_MODEL_TYPE`), catalog ID (`YANDEX_GPT_CATALOG_ID`), and API
    key (`YANDEX_GPT_API_KEY`), which can override the constructor values if set.
    """
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTConfigManagerForAPIKey class.

        Parameters
        ----------
        model_type : Optional[str], optional
            Model type to use.
        catalog_id : Optional[str], optional
            Catalog ID on YandexCloud to use.
        api_key : Optional[str], optional
            API key for authorization.
        """
        # Setting model type, catalog ID and API key from the constructor
        super().__init__(
            model_type=model_type,
            catalog_id=catalog_id,
            api_key=api_key
        )

        # Setting model type, catalog ID and API key from the environment variables if they are set
        self._set_config_from_env_vars()

        # Checking if model type, catalog ID and API key are set
        self._check_config()

    def _set_config_from_env_vars(self) -> None:
        """
        Sets configuration parameters from environment variables if they are not provided in the constructor.
        """
        self.model_type = os.environ.get("YANDEX_GPT_MODEL_TYPE", self.model_type)
        self.catalog_id = os.environ.get("YANDEX_GPT_CATALOG_ID", self.catalog_id)
        self.api_key = os.environ.get("YANDEX_GPT_API_KEY", self.api_key)

    def _check_config(self) -> None:
        """
        Ensures that the necessary configuration parameters are set, raising a ValueError if any are missing.
        """
        if not self.model_type:
            raise ValueError(
                "Model type is not set. You can ether provide it in the constructor or set in YANDEX_GPT_MODEL_TYPE "
                "environment variable"
            )
        elif not self.catalog_id:
            raise ValueError(
                "Catalog ID is not set. You can ether provide it in the constructor or set in YANDEX_GPT_CATALOG_ID "
                "environment variable"
            )
        elif not self.api_key:
            raise ValueError(
                "API key is not set. You can ether provide it in the constructor or set in YANDEX_GPT_API_KEY "
                "environment variable"
            )