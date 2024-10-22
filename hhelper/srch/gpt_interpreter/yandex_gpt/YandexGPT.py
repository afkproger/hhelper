from typing import Dict, Any, Union, List, TypedDict

from YandexGPTBase import YandexGPTBase
from YandexGPTConfigManagerBase import YandexGPTConfigManagerBase

class YandexGPTMessage(TypedDict):
    role: str
    text: str


class YandexGPT(YandexGPTBase):
    """
    Extends the YandexGPTBase class to interact with the Yandex GPT API using a simplified configuration manager.
    This class allows for easier configuration of API requests and includes both synchronous and asynchronous methods.
    """
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]]
    ) -> None:
        """
        Initializes the YandexGPT class with a configuration manager.

        Parameters
        ----------
        config_manager : Union[YandexGPTConfigManagerBase, Dict[str, Any]]
            Config manager or a dictionary containing:
            1) completion_request_model_type_uri_field
               ("gpt://{self.config_manager.catalog_id}/{self.config_manager.model_type}/latest")
            2) completion_request_catalog_id_field (self.config_manager.catalog_id)
            3) completion_request_authorization_field ("Bearer {iam_token}" or "Api-Key {api_key}")
        """
        self.config_manager = config_manager

    def _create_completion_request_headers(self) -> Dict[str, str]:
        """
        Creates headers for sending a completion request to the API.

        Returns
        -------
        Dict[str, str]
            Dictionary with authorization credentials, content type, and x-folder-id (YandexCloud catalog ID).
        """
        return {
            "Content-Type": "application/json",
            "Authorization": self.config_manager.completion_request_authorization_field,
            "x-folder-id": self.config_manager.completion_request_catalog_id_field
        }

    def _create_completion_request_payload(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False
    ) -> Dict[str, Any]:
        """
        Creates the payload for sending a completion request.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Controls the randomness of the completion, from 0 (deterministic) to 1 (random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream option for the API, currently not supported in this implementation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing the model URI, completion options, and messages.
        """
        return {
            "modelUri": self.config_manager.completion_request_model_type_uri_field,
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }

    async def get_async_completion(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
            timeout: int = 5
    ) -> str:
        """
        Sends an asynchronous completion request to the Yandex GPT API and polls for the result.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Randomness of the completion, from 0 (deterministic) to 1 (most random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Indicates whether streaming is enabled; currently not supported in this implementation.
        completion_url : str
            URL to the Yandex GPT asynchronous completion API.
        timeout : int
            Time in seconds after which the operation is considered timed out.

        Returns
        -------
        str
            The text of the completion result.

        Raises
        ------
        Exception
            If the completion operation fails or times out.
        """
        # Making the request and obtaining the ID of the completion operation
        headers: Dict[str, str] = self._create_completion_request_headers()
        payload: Dict[str, Any] = self._create_completion_request_payload(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        completion_request_id: str = await self.send_async_completion_request(
            headers=headers,
            payload=payload,
            completion_url=completion_url
        )

        # Polling the completion operation
        completion_response: Dict[str, Any] = await self.poll_async_completion(
            operation_id=completion_request_id,
            headers=headers,
            timeout=timeout
        )

        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if completion_response.get('error', None):
            raise Exception(f"Failed to get completion: {completion_response['error']}")
        else:
            return completion_response['response']['alternatives'][0]['message']['text']

    def get_sync_completion(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
    ):
        """
        Sends a synchronous completion request to the Yandex GPT API and returns the result.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Randomness of the completion, from 0 (deterministic) to 1 (most random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Indicates whether streaming is enabled; currently not supported in this implementation.
        completion_url : str
            URL to the Yandex GPT synchronous completion API.

        Returns
        -------
        str
            The text of the completion result.

        Raises
        ------
        Exception
            If the completion request fails.
        """
        # Making the request
        headers: Dict[str, str] = self._create_completion_request_headers()
        payload: Dict[str, Any] = self._create_completion_request_payload(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        completion_response: Dict[str, Any] = self.send_sync_completion_request(
            headers=headers,
            payload=payload,
            completion_url=completion_url
        )

        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if completion_response.get('error', None):
            raise Exception(f"Failed to get completion: {completion_response['error']}")
        else:
            return completion_response['result']['alternatives'][0]['message']['text']