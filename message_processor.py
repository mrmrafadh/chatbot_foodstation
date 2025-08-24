import asyncio
from typing import Dict, Any
from models import State, Item, MessageContent
from llm_service import LLMService
import json

class MessageProcessor:
    """Service class for processing user messages"""
    
    def __init__(self):
        """Initialize the message processor with LLM service"""
        self.llm_service = LLMService()
    
    async def process_user_message(self, state: State) -> Dict[str, Any]:
        """Process user message and update state"""
        print("Starting message processing...")
        
        # Get the latest user message
        messages = state.get("messages", [])
        if not messages:
            return {"error": "No messages found in state"}
        
        # Extract user input from the last message
        last_message = messages[-1]
        user_input = self._extract_message_content(last_message)
        
        # Get chat history (you can implement this based on your needs)
        chat_history = self._get_chat_history(messages)
        
        try:
            # Run intent classification and entity extraction concurrently
            intent_task = self.llm_service.classify_intent(user_input, chat_history)
            entity_task = self.llm_service.extract_entities(user_input, chat_history)
            
            intent_result, entity_result = await asyncio.gather(intent_task, entity_task)

            print("Processing completed successfully")
            
            # Create entities dictionary if dish is found
            entities_dict = {}
            if entity_result.get("dish"):
                item = Item(
                    dish=entity_result["dish"][0],
                    variant=entity_result.get("variant", ""),
                    size=entity_result.get("size"),
                    qty=int(entity_result.get("order_qty", 1)) if entity_result.get("order_qty") else 1
                )
                entities_dict = {"item1": item}
            
            # Create message content
            message_content = MessageContent(
                input=user_input,
                corrected_input=intent_result.get("corrected_input", user_input),
                restaurant_name=entity_result.get("restaurant")[0],
                entities=entities_dict
            )
            
            # Return updated state
            return {
                "message_type": intent_result.get("category", "general_inquiry"),
                "message_content": message_content,
                "is_awaiting_selection": False,
            }
            
        except Exception as e:
            print(f"Error in process_user_message: {e}")
            # Return error state but don't break the graph
            return {
                "message_type": "general_inquiry",
                "message_content": MessageContent(
                    input=user_input,
                    corrected_input=user_input,
                    restaurant_name=None,
                    entities={}
                ),
                "error": str(e)
            }
    
    def _extract_message_content(self, message) -> str:
        """Extract content from message object"""
        if hasattr(message, 'content'):
            return message.content
        elif isinstance(message, dict):
            return str(message.get('content', ''))
        else:
            return str(message)
    
    def _get_chat_history(self, messages: list) -> list:
        """Extract chat history from messages (implement based on your needs)"""
        # For now, return empty list
        # You can implement this to extract previous messages
        return []
    
    def route_by_message_type(self, state: State) -> str:
        """Route messages based on their type"""
        message_type = state.get("message_type", "general_inquiry")
        return message_type