from typing import Dict, Any
from langgraph.graph import add_messages
from models import State
from db_config import db_config

class MessageHandlers:
    """Collection of message handler functions"""
    
    @staticmethod
    def handle_greeting(state: State) -> Dict[str, Any]:
        """Handle greeting messages"""
        response_text = "Hello! Welcome to Foodstation.lk! How can I help you with food delivery today?"
        response = state.get("fallback_response") or response_text
        return {
            "messages": add_messages(
                state["messages"], 
                [{"role": "assistant", "content": response}]
            )
        }
    
    @staticmethod
    def handle_order(state: State) -> Dict[str, Any]:
        """Handle order messages"""
        message_content = state.get("message_content")
        
        if message_content and message_content.entities:
            # Extract order details
            items = []
            for key, item in message_content.entities.items():
                items.append(f"- {item.dish} ({item.variant}) - Size: {item.size} - Qty: {item.qty}")
            
            items_text = "\n".join(items) if items else "No specific items detected"
            restaurant = message_content.restaurant_name or "Not specified"
            
            response = f"""I'll help you with your order! Here's what I understood:

Restaurant: {restaurant}
Items:
{items_text}

Would you like to proceed with this order or make any changes?"""
        else:
            response = "I'd be happy to help you place an order! Could you please tell me what you'd like to order?"
        
        return {
            "messages": add_messages(
                state["messages"], 
                [{"role": "assistant", "content": response}]
            )
        }
    
    @staticmethod
    def handle_dish_info(state: State) -> Dict[str, Any]:
        """Handle dish information requests"""
        message_content = state.get("message_content")
        
        if message_content and message_content.entities:
            dish_name = message_content.entities.get("dish")
            restaurant_name = message_content.restaurant_name

            if not dish_name:
                return {
                    "messages": add_messages(
                        state["messages"],
                        [{"role": "assistant", "content": "Please give me a valid dish name"}]
                        )}

            if len(dish_name) > 1 or len(restaurant_name) > 1:
                fallback_message = "I can only check one dish at a time. Here’s the info for this dish."

                # Get dish name from entities
                dish_name = dish_name[0]
                restaurant_name = restaurant_name[0]

                if dish_name & restaurant_name:
                    response = f"You're asking about {dish_name}"
                    if restaurant_name:
                        response += f" from {restaurant_name}"
                    response += ". Let me get that information for you!"
                else:
                    response = "I'd be happy to help you with dish information! Which dish would you like to know about?"
            else:
                response = "I can help you with dish information! Which dish are you interested in?"

            return {
                "messages": add_messages(
                    state["messages"],
                    [{"role": "assistant", "content": response}]
                )
            }
    
    @staticmethod
    def handle_restaurant_info(state: State) -> Dict[str, Any]:
        """Handle restaurant information requests"""
        message_content = state.get("message_content")
        restaurant_name = message_content.restaurant_name if message_content else None
        
        if restaurant_name:
            response = f"You're asking about {restaurant_name}. Let me get their information for you!"
        else:
            response = "I can help you with restaurant information! Which restaurant would you like to know about?"
        
        return {
            "messages": add_messages(
                state["messages"], 
                [{"role": "assistant", "content": response}]
            )
        }
    
    @staticmethod
    def handle_general_inquiry(state: State) -> Dict[str, Any]:
        """Handle general inquiry messages"""
        response = """I'm here to help you with food delivery! I can assist you with:

🍽️ Finding restaurants and their menus
🥘 Getting information about dishes and prices  
📦 Placing food orders
⏰ Restaurant hours and availability
🔍 Food recommendations

What would you like to know?"""
        
        return {
            "messages": add_messages(
                state["messages"], 
                [{"role": "assistant", "content": response}]
            )
        }