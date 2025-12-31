import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        print("\n=== REQUEST ===")
        print(f"URL: {self._endpoint}")
        print(f"Headers: {headers}")
        print(f"Body: {json.dumps(request_data, indent=2)}")

        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data
        )

        # 4. Get content from response, print it and return message with assistant role and content
        print("\n=== RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        response_json = response.json()
        if not response_json.get("choices"):
            raise Exception("No choices in response found")
        content = response_json["choices"][0]["message"]["content"]
        print(f"\n=== ASSISTANT RESPONSE ===")
        print(content)

        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }

        print("\n=== STREAMING REQUEST ===")
        print(f"URL: {self._endpoint}")
        print(f"Headers: {headers}")
        print(f"Body: {json.dumps(request_data, indent=2)}")
        print("\n=== STREAMING RESPONSE ===")
        # 3. Create empty list called 'contents' to store content snippets
        contents = []
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._endpoint,
                json=request_data,
                headers=headers
            ) as response:
                print(f"Status Code: {response.status}")
                async for line in response.content:
                    # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
                    #    chunks, collect them and return as assistant message
                    decoded_line = line.decode('utf-8').strip()
                    content_chunk, is_done = self._get_content_snippet(decoded_line)

                    if is_done:
                        break

                    if content_chunk is not None:
                        contents.append(content_chunk)
        print()

        return Message(role=Role.AI, content="".join(contents))



    def _get_content_snippet(self, decoded_line: str) -> tuple[str | None, bool]:
        if not decoded_line.startswith("data: "):
            return None, False

        data = decoded_line[6:]

        if data == "[DONE]":
            print("\n[DONE]")
            return None, True

        chunk = json.loads(data)
        print(f"\n--- CHUNK ---\n{json.dumps(chunk, indent=2)}\n")
        content_chunk = chunk["choices"][0]["delta"].get("content", "")
        return content_chunk, False