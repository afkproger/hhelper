import asyncio
from typing import Dict, Any

import aiohttp
import requests


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