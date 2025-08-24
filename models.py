from typing import TypedDict, Annotated, Literal, Dict, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage

# Pydantic Models for Data Structure
class Item(BaseModel):
    """Model for individual food items"""
    dish: Optional[str] = Field(None, description="Name of the dish")
    variant: Optional[str] = Field(None, description="Variant of the dish")
    size: Optional[str] = Field(None, description="Size of the dish")
    qty: int = Field(..., ge=1, description="Quantity must be at least 1")

class MessageContent(BaseModel):
    """Model for processed message content"""
    input: str = Field(..., description="Original user input")
    corrected_input: str = Field(..., description="Corrected/processed input")
    restaurant_name: Optional[str] = Field(None, description="Restaurant name if mentioned")
    entities: Dict[str, Item] = Field(default_factory=dict, description="Extracted entities")

class OrderState(BaseModel):
    """Model for current order state"""
    current_available_dishes: Optional[List[str]] = None
    current_available_variants: Optional[List[str]] = None
    current_available_sizes: Optional[List[str]] = None
    current_selected_variant: Optional[str] = None
    current_selected_size: Optional[str] = None
    current_dish_info: Optional[str] = None

class CartItem(BaseModel):
    """Model for cart items"""
    id: Optional[str] = None
    dish: Optional[str] = None
    variant: Optional[str] = None
    size: Optional[str] = None
    qty: Optional[int] = Field(None, ge=1)
    price: Optional[float] = Field(None, ge=0)
    total_price: Optional[float] = Field(None, ge=0)

class MessageClassifier(BaseModel):
    """Model for message classification"""
    message_type: Literal["greeting", "dish_info", "restaurant_info", "order", "general_inquiry"] = Field(
        ..., description="Classify the message intent"
    )
    message_content: Optional[MessageContent] = Field(
        None, description="The content of the message"
    )

# TypedDict for Graph State
class State(TypedDict):
    """Main state for the conversation graph"""
    messages: Annotated[List[AnyMessage], add_messages]
    message_type: Optional[Literal["greeting", "dish_info", "restaurant_info", "order", "general_inquiry"]]
    message_content: Optional[MessageContent]
    is_awaiting_selection: bool
    order_state: Optional[OrderState]
    cart: Optional[List[CartItem]]
    next: Optional[str]  # For routing decisions