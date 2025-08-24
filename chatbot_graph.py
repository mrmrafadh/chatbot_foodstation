from langgraph.graph import StateGraph, START, END
from models import State
from message_processor import MessageProcessor
from handlers import MessageHandlers

class ChatbotGraph:
    """Main chatbot graph builder and runner"""
    
    def __init__(self):
        """Initialize the chatbot graph"""
        self.message_processor = MessageProcessor()
        self.handlers = MessageHandlers()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(State)
        
        # Add nodes
        graph.add_node("process_message", self.message_processor.process_user_message)
        graph.add_node("handle_greeting", self.handlers.handle_greeting)
        graph.add_node("handle_order", self.handlers.handle_order)
        graph.add_node("handle_dish_info", self.handlers.handle_dish_info)
        graph.add_node("handle_restaurant_info", self.handlers.handle_restaurant_info)
        graph.add_node("handle_general_inquiry", self.handlers.handle_general_inquiry)
        
        # Set entry point
        graph.add_edge(START, "process_message")
        
        # Add conditional edges based on message_type
        graph.add_conditional_edges(
            "process_message",
            self.message_processor.route_by_message_type,
            {
                "greeting": "handle_greeting",
                "order": "handle_order",
                "dish_info": "handle_dish_info",
                "restaurant_info": "handle_restaurant_info",
                "general_inquiry": "handle_general_inquiry"
            }
        )
        
        # Add edges from handler nodes to END
        graph.add_edge("handle_greeting", END)
        graph.add_edge("handle_order", END)
        graph.add_edge("handle_dish_info", END)
        graph.add_edge("handle_restaurant_info", END)
        graph.add_edge("handle_general_inquiry", END)
        
        return graph.compile()
    
    async def process_message_async(self, user_message: str) -> dict:
        """Process a single message asynchronously"""
        initial_state = {
            "messages": [{"role": "user", "content": user_message}],
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result
    
    def get_last_assistant_message(self, result: dict) -> str:
        """Extract the last assistant message from the result"""
        messages = result.get("messages", [])
        
        # Find the last assistant message
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "assistant":
                return message.get("content", "")
            elif hasattr(message, 'content'):
                # Handle other message types if needed
                return message.content
        
        return "I'm sorry, I couldn't process your message."