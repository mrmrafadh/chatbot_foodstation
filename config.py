import os
from typing import List

class Config:
    """Configuration settings for the food delivery chatbot"""
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Model Configuration
    MODEL_NAME = "groq:openai/gpt-oss-120b"
    
    # Restaurant List (exact spelling)
    RESTAURANTS = [
        "Kandiah", "Ice Talk", "Bluberry", "Jollybeez", 
        "Mum's Food", "ourselection"
    ]
    
    # Dishes List (exact spelling)
    DISHES = [
        'Kotthu Rotti', 'Cheese Kotthu', 'Dolphin', 'Pittu Kotthu', 'Noodles', 
        'Pasta', 'String Hopper Kotthu', 'Bread Kotthu', 'Rice & Curry', 
        'Schezwan Rice', 'Mongolian Rice', 'Chopsuey Rice', 'Nasi Goreng', 
        'Biriyani', 'Fried Rice', 'Fry', 'Bbq', 'Tandoori', 'Grill', 'Devilled', 
        'Hot Butter', 'Curry', 'Kuruma', 'Parata', 'Mums Special Lime With Mint', 
        'Mums Special', 'Fresh Juice', 'Milk Shakes', 'Ice Cream', 'Nescafe', 
        'Milk Tea', 'Milo', 'Fruit Salad ', 'Wattalappam', 'Biscuit Pudding', 
        'Naan', 'French Fries', 'Soup', 'Salad', 'Mayyer Kelangu Fry', 'Hopper', 
        'Rolls', 'Samosa', 'Corn', 'Vadai', 'Shawarma', 'Bun', 'Kanji / Kenda', 
        'Chips', 'Mixture', 'Manyokka Fry'
    ]
    
    # Size mappings
    SIZE_MAPPINGS = {
        "normal": "Small",
        "half": "Small", 
        "full": "Medium",
        "2 person": "Medium",
        "large": "Large",
        "4 person": "Large"
    }
    
    # Valid message types
    MESSAGE_TYPES = [
        "greeting", "dish_info", "restaurant_info", 
        "order", "general_inquiry"
    ]