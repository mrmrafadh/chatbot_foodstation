import asyncio
from chatbot_graph import ChatbotGraph

chatbot = ChatbotGraph()   # create an instance

user_input = input("Enter your message: ")
result = asyncio.run(chatbot.process_message_async(user_input))

print(result["messages"][-1].content)
