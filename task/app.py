import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT, MODEL_ID, STREAM_RESPONSE
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    #TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    client = DialClient(deployment_name=MODEL_ID)
    # 1.2. Create CustomDialClient
    custom_client = CustomDialClient(deployment_name=MODEL_ID)
    # 2. Create Conversation object
    conversation = Conversation()
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    system_message = input("Enter system prompt (or press Enter to use default): ")
    if not system_message:
        system_message = DEFAULT_SYSTEM_PROMPT
    conversation.messages.append(Message(role=Role.SYSTEM, content=system_message))
    # 4. Use infinite cycle (while True) and get user message from console
    while True:
        user_input = input("You: ")
        # 5. If user message is `exit` then stop the loop
        if user_input.lower() == "exit":
            print("Exiting the chat.")
            break
        # 6. Add user message to conversation history (role 'user')
        conversation.add_message(Message(role=Role.USER, content=user_input))
        # 7. If `stream` param is true -> call DialClient#stream_completion()
        #    else -> call DialClient#get_completion()
        if STREAM_RESPONSE:
            response = await client.stream_completion(conversation.messages)
        else:
            response = custom_client.get_completion(conversation.messages)
        # 8. Add generated message to history
        conversation.add_message(response)
        print(f"Assistant: {response.content}")
    # 9. Test it with DialClient and CustomDialClient

    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response

    raise NotImplementedError


asyncio.run(
    start(True)
)
