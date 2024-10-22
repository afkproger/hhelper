from typing import List, Optional

available_models: List[str] = [
        "yandexgpt",
        "yandexgpt-lite",
        "summarization"
    ]


class YandexGPTConfigManagerBase:
    """
    Base class for YaGPT configuration management. It handles configurations related to model type, catalog ID, IAM
    token, and API key for authorization when making requests to the completion endpoint.
    """
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            iam_token: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTConfigManagerBase class.

        Parameters
        ----------
        model_type : Optional[str], optional
            Model type to use.
        catalog_id : Optional[str], optional
            Catalog ID on YandexCloud to use.
        iam_token : Optional[str], optional
            IAM token for authorization.
        api_key : Optional[str], optional
            API key for authorization.
        """
        self.model_type: Optional[str] = model_type
        self.catalog_id: Optional[str] = catalog_id
        self.iam_token: Optional[str] = iam_token
        self.api_key: Optional[str] = api_key

    @property
    def completion_request_authorization_field(self) -> str:
        """
        Returns the authorization field for the completion request header based on the IAM token or API key.

        Raises
        ------
        ValueError
            If neither IAM token nor API key is set.

        Returns
        -------
        str
            The authorization field for the completion request header in the form of "Bearer {iam_token}" or
            "Api-Key {api_key}".
        """
        # Checking if either iam_token or api_key is set and returning the authorization field string
        if self.iam_token:
            return f"Bearer {self.iam_token}"
        elif self.api_key:
            return f"Api-Key {self.api_key}"
        else:
            raise ValueError("IAM token or API key is not set")

    @property
    def completion_request_catalog_id_field(self) -> str:
        """
        Returns the catalog ID field for the completion request header.

        Raises
        ------
        ValueError
            If catalog_id is not set.

        Returns
        -------
        str
            The catalog ID field for the completion request header.
        """
        # Checking if catalog_id is set and returning the catalog id field string
        if self.catalog_id:
            return self.catalog_id
        else:
            raise ValueError("Catalog ID is not set")

    @property
    def completion_request_model_type_uri_field(self) -> str:
        """
        Returns the model type URI field for the completion request payload.

        Raises
        ------
        ValueError
            If model_type or catalog_id is not set or if model_type is not in the available models.

        Returns
        -------
        str
            The model type URI field for the completion request header in the URI format.
        """
        global available_models

        # Checking if model_type is in available_models
        if self.model_type not in available_models:
            raise ValueError(f"Model type {self.model_type} is not supported. Supported values: {available_models}")

        # Checking if model_type and catalog_id are set and returning the model type URI field string
        if self.model_type and self.catalog_id:
            return f"gpt://{self.catalog_id}/{self.model_type}/latest"
        else:
            raise ValueError("Model type or catalog ID is not set")