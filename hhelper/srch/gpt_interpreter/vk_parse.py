import json
import random
from typing import Union, TypedDict

import asyncio
from typing import Dict, Any
import aiohttp
import requests
from typing import List, Optional

import os
from typing import Optional

import vk


class Parsing:

    def __init__(self, user_id):
        TOKEN = "f99e6956f99e6956f99e6956ccfabead59ff99ef99e69569e93e1709c9c876af276a32e"
        VERSION = "5.199"
        self.connection = vk.API(TOKEN, v=VERSION)
        self.user_id = user_id
        self.FIELDS = "about, activities, bdate, books, can_see_audio, can_write_private_message, career, city, connections, contacts, counters, country, domain, education, exports, followers_count, has_mobile, has_photo, home_town, interests, is_no_index, last_seen, military, nickname, occupation, online, personal, photo_200, quotes, relatives, relation, schools, sex, site, status, universities, verified"
        self.__wall = None

    def parse_user_wall(self):
        self.__wall = self.connection.wall.get(owner_id=self.user_id, filter=all, count=100, extended=1,
                                               fields=self.FIELDS)

    def extract_names_and_cities(self, data, key):
        return {
            (
                item["name"],
                self.get_city_name(item["city"]) if "city" in item else "N/A"
            )
            for item in data if "name" in item
        }

    def get_city_name(self, city_id):
        try:
            city_info = self.connection.database.getCitiesById(city_ids=city_id)
            if city_info and isinstance(city_info, list) and len(city_info) > 0:
                return city_info[0].get("title", f"Unknown city {city_id}")
            return f"Unknown city {city_id}"
        except Exception as e:
            return f"Error fetching city {city_id}: {e}"

    def get_group_name(self, group_id):
        try:
            group_info = self.connection.groups.getById(group_id=group_id)
            if group_info and isinstance(group_info['groups'], list) and len(group_info) > 0:
                return group_info['groups'][0]["name"]
            return f"Unknown group {group_id}"
        except Exception as e:
            return f"Error fetching group {group_id}: {e}"

    def parse_user_info(self):
        # Получение информации о пользователе с нужными полями
        user_info = self.connection.users.get(user_id=self.user_id, fields="schools,universities,education,career")

        # Если данные о пользователе получены, форматируем их
        if user_info:
            user_info = user_info[0]  # Если вернулся список, берем первый элемент

            # Форматируем поля для университетов и школ
            formatted_data = {
                "career": {
                    (
                        career_item.get("position", ""),
                        self.get_group_name(career_item["group_id"]) if "group_id" in career_item else "N/A",
                        self.get_city_name(career_item["city_id"]) if "city_id" in career_item else "N/A"
                    )
                    for career_item in user_info.get("career", [])
                },
                "universities": self.extract_names_and_cities(user_info.get("universities", []), "universities"),
                "schools": self.extract_names_and_cities(user_info.get("schools", []), "schools")
            }

            return formatted_data

        return {}

    def parse_subscriptions(self):
        try:
            subscriptions_info = self.connection.users.getSubscriptions(user_id=self.user_id, extended=1, count=100)
            # Извлечение названий подписок
            formatted_subscriptions = {
                item["name"]
                for item in subscriptions_info.get("items", [])
            }
            return formatted_subscriptions
        except Exception as e:
            return f"Error fetching subscriptions: {e}"

    def parse_user_posts(self):
        self.parse_user_wall()
        try:
            posts = {
                item["text"]
                for item in self.__wall['items'] if len(item['text']) != 0
            }

            return posts
        except Exception as e:
            return f"Error fetching posts: {e}"


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


class YandexGPTBase:
    """
    This class is used to interact with the Yandex GPT API, providing asynchronous and synchronous methods to send requests and poll for their completion.
    """

    @staticmethod
    async def send_async_completion_request(
            headers: Dict[str, str],
            payload: Dict[str, Any],
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    ) -> str:
        """
        Sends an asynchronous request to the Yandex GPT completion API.

        Parameters
        ----------
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM), content type, and x-folder-id (YandexCloud catalog ID).
        payload : Dict[str, Any]
            Dictionary with the model URI, completion options, and messages.
        completion_url : str
            URL of the completion API.

        Returns
        -------
        str
            ID of the completion operation to poll.
        """
        # Making the request
        async with aiohttp.ClientSession() as session:
            async with session.post(completion_url, headers=headers, json=payload) as resp:
                # If the request was successful, return the ID of the completion operation
                # Otherwise, raise an exception
                if resp.status == 200:
                    data = await resp.json()
                    return data['id']
                else:
                    raise Exception(f"Failed to send async request, status code: {resp.status}")

    @staticmethod
    async def poll_async_completion(
            operation_id: str,
            headers: Dict[str, str],
            timeout: int = 5,
            poll_url: str = 'https://llm.api.cloud.yandex.net/operations/'
    ) -> Dict[str, Any]:
        """
        Polls the status of an asynchronous completion operation until it completes or times out.

        Parameters
        ----------
        operation_id : str
            ID of the completion operation to poll.
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM).
        timeout : int
            Time in seconds after which the operation is considered timed out.
        poll_url : str
            Poll URL.

        Returns
        -------
        Dict[str, Any]
            Completion result.
        """
        # Polling the completion operation for the specified amount of time
        async with aiohttp.ClientSession() as session:
            end_time = asyncio.get_event_loop().time() + timeout
            while True:
                # Check if the operation has timed out and if so, raise an exception
                if asyncio.get_event_loop().time() > end_time:
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
                # Polling the operation
                async with session.get(f"{poll_url}{operation_id}", headers=headers) as resp:
                    # If the request was successful, return the completion result
                    # Otherwise, raise an exception
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('done', False):
                            return data
                    else:
                        raise Exception(f"Failed to poll operation status, status code: {resp.status}")
                await asyncio.sleep(1)

    @staticmethod
    def send_sync_completion_request(
            headers: Dict[str, str],
            payload: Dict[str, Any],
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ) -> Dict[str, Any]:
        """
        Sends a synchronous request to the Yandex GPT completion API.

        Parameters
        ----------
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM), content type, and x-folder-id (YandexCloud catalog ID).
        payload : Dict[str, Any]
            Dictionary with the model URI, completion options, and messages.
        completion_url : str
            URL of the completion API.

        Returns
        -------
        Dict[str, Any]
            Completion result.
        """
        # Making the request
        response = requests.post(completion_url, headers=headers, json=payload)
        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send sync request, status code: {response.status_code}")


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


class YandexGPTThreadStatus(TypedDict):
    status: str
    last_error_message: Optional[str]


class YandexGPTThread(YandexGPT):
    """
    A thread-based interface for interacting with the Yandex GPT model.

    This class manages asynchronous messaging and maintains the state of conversation threads.
    """

    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]],
            messages: Optional[List[YandexGPTMessage]] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTThread.

        Parameters
        ----------
        config_manager : Union[YandexGPTConfigManagerBase, Dict[str, Any]]
            Configuration manager for the Yandex GPT model.
        messages : Optional[List[YandexGPTMessage]], optional
            Initial list of messages within the thread, by default None.
        """
        super().__init__(config_manager=config_manager)

        if messages:
            self.messages = messages
        else:
            self.messages = []

        self.status = YandexGPTThreadStatus(
            status="created",
            last_error_message=None
        )

    def add_message(
            self,
            role: str,
            text: str
    ) -> None:
        """
        Appends a new message to the conversation thread.

        Parameters
        ----------
        role : str
            The role of the message, typically 'user' or 'assistant'.
        text : str
            The content of the message.
        """
        self.messages.append(YandexGPTMessage(role=role, text=text))

    def __getitem__(self, index):
        """
        Allows retrieval of a message by index from the conversation thread.

        Parameters
        ----------
        index : int
            Index of the message to retrieve.

        Returns
        -------
        YandexGPTMessage
            The message at the specified index.
        """
        return self.messages[index]

    def __len__(self):
        """
        Returns the number of messages in the conversation thread.

        Returns
        -------
        int
            The number of messages.
        """
        return len(self.messages)

    async def run_async(
            self,
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
            timeout: int = 15
    ):
        """
        Runs the thread asynchronously, requesting and appending completion from the Yandex GPT model.

        Parameters
        ----------
        temperature : float
            Sampling temperature, scales the likelihood of less probable tokens. Value from 0 to 1.
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream responses from the API (not currently supported).
        completion_url : str
            URL of the asynchronous completion API.
        timeout : int
            Timeout in seconds for the asynchronous call.

        Raises
        ------
        Exception
            If the thread is already running.
        """
        if self.status["status"] == "running":
            raise Exception("Thread is already running")
        else:
            self.status["status"] = "running"

            try:
                completion_text = await self.get_async_completion(
                    messages=self.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    completion_url=completion_url,
                    timeout=timeout
                )
                self.add_message(role="assistant", text=completion_text)
            except Exception as e:
                self.status["status"] = "error"
                self.status["last_error_message"] = str(e)
            finally:
                self.status["status"] = "idle"

    def run_sync(
            self,
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ):
        """
        Runs the thread synchronously, requesting and appending completion from the Yandex GPT model.

        Parameters
        ----------
        temperature : float
            Sampling temperature, scales the likelihood of less probable tokens. Value from 0 to 1.
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream responses from the API (not currently supported).
        completion_url : str
            URL of the synchronous completion API.

        Raises
        ------
        Exception
            If the thread is already running.
        """
        if self.status["status"] == "running":
            raise Exception("Thread is already running")
        else:
            self.status["status"] = "running"

            try:
                completion_text = self.get_sync_completion(
                    messages=self.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    completion_url=completion_url
                )
                self.add_message(role="assistant", text=completion_text)
            except Exception as e:
                self.status["status"] = "error"
                self.status["last_error_message"] = str(e)
            finally:
                self.status["status"] = "idle"


class PersonAnalysis:
    def __init__(self, user_info, subscriptions, posts, data):
        """Инициализация класса анализа специалиста с подготовкой входных данных."""

        MODEL_NAME = "yandexgpt"
        CATALOG_ID = "b1ggortl5q1ss3iehd1c"
        API_KEY = "AQVNwIbx4Px8Rx5dwZE7l3PXAtpapTO_qIp9p56-"

        # Инициализируем конфиг для GPT и создаём YandexGPTThread
        self.config_manager = YandexGPTConfigManagerForAPIKey(
            model_type=MODEL_NAME, catalog_id=CATALOG_ID, api_key=API_KEY
        )

        # Прямое присвоение множеств
        self.user_info = user_info
        self.subscriptions = subscriptions
        self.posts = posts
        self.data = data

        self.indicators = self._prepare_indicators()
        self.career = self._extract_career(self.user_info)
        self.universities = self._extract_universities(self.user_info)
        self.schools = self._extract_schools(self.user_info)

    def _prepare_indicators(self):
        """Извлекает индикаторы и название должности из входных данных."""
        indicators = self.data.get("indicators", [])
        return indicators

    def _extract_career(self, user_info: set) -> set:
        """Извлекает информацию о карьере пользователя."""
        return {item['group'] for item in user_info if 'group' in item}

    def _extract_universities(self, user_info: set) -> set:
        """Извлекает информацию об университетах пользователя."""
        return {item['name'] for item in user_info if
                'name' in item and 'type' in item and item['type'] == 'university'}

    def _extract_schools(self, user_info: set) -> set:
        """Извлекает информацию о школах пользователя."""
        return {f"{item['name']} ({item.get('city', '')})" for item in user_info if
                'name' in item and 'type' in item and item['type'] == 'school'}

    def _prepare_gpt_messages(self) -> list:
        """Формирует сообщения для запроса к YandexGPT с учетом всех показателей и данных пользователя."""

        indicators_text = "; ".join(
            [f"{indicator}: оцени (1.0 — высокий, -1.0 — низкий)" for
             indicator in self.indicators]
        )

        subscriptions_text = ", ".join(self.subscriptions) if self.subscriptions else "Отсутствуют"
        posts_text = "; ".join(self.posts) if self.posts else "Отсутствуют"
        career_text = ", ".join(self.career) if self.career else "Отсутствует"
        universities_text = ", ".join(self.universities) if self.universities else "Отсутствуют"
        schools_text = ", ".join(self.schools) if self.schools else "Отсутствуют"

        user_input = (
            f"У нас есть несколько показателей, каждый из которых важен для оценки кандидата.\n"
            f"{indicators_text}. Пожалуйста, оцени каждый показатель кандидата, опираясь на представленные данные. "
            "Данные включают подписки, посты, карьерный путь, а также информацию об университетах и школах, указанные ниже.\n\n"
            f"Подписки специалиста: {subscriptions_text}.\n"
            f"Последние посты специалиста: {posts_text}.\n"
            f"Карьера специалиста: {career_text}.\n"
            f"Университеты, в которых обучался специалист: {universities_text}.\n"
            f"Школы, в которых обучался специалист: {schools_text}.\n\n"
            "Твоя задача — присвоить оценку каждому показателю в диапазоне от -1.0 до 1.0, где:\n"
            "- значения около 1.0 отражают высокий уровень, соответствующий показателю;\n"
            "- значения около -1.0 — низкий уровень;\n"
            "Оцени каждый показатель на основе предоставленных данных, не делай предположений на основе информации, отсутствующей в запросе. "
            "Ответ должен быть строго в формате JSON и включать только оценки для каждого показателя, без пояснений, дополнительных данных "
            "или комментариев. Ответ должен строго соответствовать следующему формату:\n"
            "{\n  \"показатель_1\": 0.265,\n  \"показатель_2\": 0.809,\n  \"показатель_3\": -0.733,\n  ...\n}"
            "\nСохрани порядок перечисленных показателей и избегай отклонений от заданного формата."
        )

        system_message = (
            "Вы — AI-ассистент, который помогает оценивать специалистов на основе их подписок, постов, образования, "
            "и карьерного опыта. Каждому показателю поставьте оценку в диапазоне от -1.0 до 1.0, где:\n"
            "- значения около 1.0 указывают на высокий уровень соответствия показателю;\n"
            "- значения около -1.0 — на низкий уровень;\n"
            "Ответ должен быть строго в формате JSON, не добавляйте комментарии, пояснения или что-либо лишнее."
        )

        messages = [
            {'role': 'system', 'text': system_message},
            {'role': 'user', 'text': user_input}
        ]
        return messages

    def get_response(self) -> Dict:
        flag = 1
        while (flag == 1):
            try:
                messages = self._prepare_gpt_messages()
                yandex_gpt_thread = YandexGPTThread(config_manager=self.config_manager, messages=messages)
                yandex_gpt_thread.run_sync()
                response_data = yandex_gpt_thread[-1]['text']
                marks = eval(response_data)
                response = [float(marks[indicator.lower()]) for indicator in self.indicators]
                for i in range(3):
                    if response[i] == 0.0: response[i] += random.random() * (1 + 1) - 1
                flag = 0
                return response
            except Exception as e:
                flag = 1
