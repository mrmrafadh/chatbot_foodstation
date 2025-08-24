from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from config import Config
import json


class LLMService:
    """Service class for handling LLM operations"""

    def __init__(self):
        """Initialize the LLM service with model configuration"""
        self.llm = init_chat_model(Config.MODEL_NAME)
        self._setup_prompts()

    def _setup_prompts(self):
        """Setup prompt templates for different operations"""

        # Intent Classification Prompt
        self.intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a multilingual AI assistant for Foodstation.lk, a food delivery platform offering dishes from multiple restaurants. You understand languages including Sinhala (Singlish) and Tamil (Tanglish). Process user messages using these steps:

Step 1: Message Rewriting
Transform the user's latest message into a standalone query:
- If the message refers to chat history, rephrase it into a complete, self-contained sentence.
- Preserve the original meaning and intent.

Step 2: Classification
Classify the rewritten message into ONE category only:
- greeting: User saying hello, hi, good morning, etc.
- restaurant_info: User asking about restaurant menus, details, hours, location, or status (open/closed).
- dish_info: User asking about the price of specific dishes, dish availability, or where to find a specific dish.
- order: User expressing intent to place a food order.
- general_inquiry: User asking about food recommendations, operating hours, food categories, or general suggestions.
- Unknown: Message is unclear or unrelated to food delivery or the above categories.

Step 3: Fallback Response
Generate a response only for these cases:
- greeting: Respond politely (e.g., "Hi! How can I help you with Foodstation.lk today?").
- Unknown: Ask for clarification (e.g., "Could you clarify how I can assist you with Foodstation.lk?").
- All other cases: Set to null.

Output Requirements:
Return only this JSON format:
{{
    "corrected_input": "rewritten message or original",
    "category": "exact category name from list above",
    "fallback_response": "response text or null"
}}

Critical Rules:
1. Output must be valid JSON only.
2. No additional text or explanations.
3. Use exact category names as listed.
4. Set empty fields to null (not empty string).

Example:
User: "hi, how are you"
Rewritten: "Hello, how are you?"
Category: greeting
Output:
{{
    "corrected_input": "Hello, how are you?",
    "category": "greeting",
    "fallback_response": "Hi! How can I help you with Foodstation.lk today?"
}}
            """),
            ("user", "{user_input}"),
        ])

        # Entity Extraction Prompt
        self.entity_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a multilingual AI assistant for Foodstation.lk, a food delivery platform offering dishes from multiple restaurants. You understand languages including Sinhala (Singlish) and Tamil (Tanglish). Process user messages using these steps:

Step 1: Message Rewriting
Transform the user's latest message into a standalone query:
- If the message refers to chat history, rephrase it into a complete, self-contained sentence.
- Preserve the original meaning and intent.

Step 2: Entity Extraction
Extract and correct names using these lists:

Restaurants (exact spelling): Kandiah, Ice Talk, Bluberry, Jollybeez, Mum's Food, ourselection

Dishes (exact spelling): Kotthu Rotti, Cheese Kotthu, Dolphin, Pittu Kotthu, Noodles, Pasta, String Hopper Kotthu, Bread Kotthu, Rice & Curry, Schezwan Rice, Mongolian Rice, Chopsuey Rice, Nasi Goreng, Biriyani, Fried Rice, Fry, Bbq, Tandoori, Grill, Devilled, Hot Butter, Curry, Kuruma, Parata, Mums Special Lime With Mint, Mums Special, Fresh Juice, Milk Shakes, Ice Cream, Nescafe, Milk Tea, Milo, Fruit Salad, Wattalappam, Biscuit Pudding, Naan, French Fries, Soup, Salad, Mayyer Kelangu Fry, Hopper, Rolls, Samosa, Corn, Vadai, Shawarma, Bun, Kanji / Kenda, Chips, Mixture, Manyokka Fry

Extraction Rules:
- Correct misspelled restaurant/dish names to match the lists exactly.
- If no match is found, set to null.
- Extract quantity numbers (e.g., "two" → 2, "three" → 3).
- For Singlish/Tanglish inputs, correct to exact dish/restaurant spelling.
- Extract size as "Small", "Medium", "Large", or "null" if not specified.
- Map size terms: "normal"/"half" → Small (1 person), "full"/"2 person" → Medium (2 people), "large"/"4 person" → Large (4 people). If no size is mentioned, set to "null".
- Always use a list inside restaurant/dish names.

IMPORTANT: Always return a SINGLE JSON object. 
If multiple dishes/restaurants are found, combine them into a single object

Output Requirements:
Return only this JSON format:
{{
    "corrected_input": "rewritten message or original",
    "restaurant": "restaurant name or null",
    "dish": "dish name or null",
    "size": "Small/Medium/Large or null",
    "variant": "variant name or null",
    "order_qty": "number or null"
}}

Critical Rules:
1. Output must be valid JSON only.
2. No additional text or explanations.
3. Restaurant/dish names must match reference lists exactly.
4. Set empty fields to null (not empty string).
5. Extract numbers for quantities (1, 2, 3, etc.).

Example:
User: "price of beef biriyani normal from Kandiah"
Rewritten: "What is the price of beef Biriyani normal from Kandiah?"
Extracted: restaurant = "Kandiah", dish = "Biriyani", size = "Small", variant = "Beef", order_qty = null
Output:
{{
    "corrected_input": "What is the price of beef Biriyani normal from Kandiah?",
    "restaurant": ["Kandiah"],
    "dish": ["Biriyani"],
    "size": "Small",
    "variant": "Beef",
    "order_qty": null
}}
            """),
            ("user", "{user_input}"),
        ])

    async def classify_intent(self, user_input: str, chat_history: list = None, retry: int = 0) -> dict:
        """Classify user intent asynchronously"""
        try:
            print("Started intent classification")
            chain = LLMChain(llm=self.llm, prompt=self.intent_prompt)
            result = await chain.ainvoke({"user_input": user_input})

            # Parse the result
            response_text = result.get("text", "{}").strip()
            print("Intent classified")
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error in intent classification: {e}")
            if retry < 1:
                return await self.classify_intent(user_input, chat_history, retry + 1)
            return {
                "corrected_input": user_input,
                "category": "general_inquiry",
                "fallback_response": None
            }
        except Exception as e:
            print(f"Error in intent classification: {e}")
            if retry < 1:
                return await self.classify_intent(user_input, chat_history, retry + 1)
            return {
                "corrected_input": user_input,
                "category": "general_inquiry",
                "fallback_response": None
            }


    async def extract_entities(self, user_input: str, chat_history: list = None, retry: int = 0) -> dict:
        """Extract entities from user input asynchronously"""
        print("Started extract entities")
        try:
            chain = LLMChain(llm=self.llm, prompt=self.entity_prompt)
            result = await chain.ainvoke({"user_input": user_input})

            # Parse the result
            response_text = result.get("text", "{}").strip()
            # print("Entities extracted")

            parsed_result = json.loads(response_text)

            # Validate that all required keys exist
            required_keys = ["corrected_input", "restaurant", "dish", "size", "variant", "order_qty"]
            for key in required_keys:
                if key not in parsed_result:
                    parsed_result[key] = None

            return parsed_result

        except json.JSONDecodeError as e:
            print(f"JSON parsing error in entity extraction: {e}")
            print(f"Raw response: {response_text if 'response_text' in locals() else 'N/A'}")
            if retry < 2:  # Allow up to 2 retries
                return await self.extract_entities(user_input, chat_history, retry + 1)
            return {
                "corrected_input": user_input,
                "restaurant": None,
                "dish": None,
                "size": None,
                "variant": None,
                "order_qty": None
            }
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            if retry < 2:  # Allow up to 2 retries
                return await self.extract_entities(user_input, chat_history, retry + 1)
            return {
                "corrected_input": user_input,
                "restaurant": None,
                "dish": None,
                "size": None,
                "variant": None,
                "order_qty": None
            }