from db_config import db_config
from typing import List, Tuple, Optional
import contextlib
from collections import defaultdict
import json
from decimal import Decimal


class DB_extract_price_data:
    """Database connection class for handling price inquiries."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connection = db_config.db_conn()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close resources."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    @staticmethod
    def _build_search_query(dish_name: str, restaurant_name: Optional[str] = None) -> Tuple[str, tuple]:
        """Build the appropriate SQL query based on parameters."""
        base_query = """
            SELECT
                m.`food_name` AS food_name,
                m.variant AS variant,
                m.`size` AS size,
                m.`price`,
                r.`name` AS restaurant_name,
                CASE
                    WHEN m.`available_from` <= CURTIME() AND m.`available_until` >= CURTIME()
                    THEN 'Available Now'
                    ELSE 'Not Available Now'
                END AS food_availability,
                CASE
                    WHEN r.`opening_time` <= CURTIME() AND r.`closing_time` >= CURTIME()
                    THEN 'Open Now'
                    ELSE 'Closed Now'
                END AS restaurant_status,
                CONCAT(TIME_FORMAT(m.`available_from`, '%H:%i'), ' - ', 
                       TIME_FORMAT(m.`available_until`, '%H:%i')) AS available_time
            FROM `food_items` m
            JOIN `restaurants` r ON m.`restaurant_id` = r.`restaurant_id`
            WHERE m.`food_name` LIKE %s
        """

        if restaurant_name:
            base_query += " AND r.`name` LIKE %s"
            parameters = (f"%{dish_name}%", f"%{restaurant_name}%")
        else:
            parameters = (f"%{dish_name}%",)

        base_query += " ORDER BY r.`name` ASC, m.`price` ASC;"

        return base_query, parameters

    @staticmethod
    def convert_decimal(obj):
        if isinstance(obj, dict):
            return {k: DB_extract_price_data.convert_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DB_extract_price_data.convert_decimal(i) for i in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj


    @staticmethod
    def _format_results(results: List[Tuple], variant: Optional[str] = None,
                        size: Optional[str] = None) -> List[Tuple]:
        """Format and filter query results."""
        keys = ['dish', 'variant', 'size', 'price', 'restaurant',
                'availability', 'restaurant_status', 'available_time']
        # Convert to list of dictionaries
        formatted_data = [dict(zip(keys, item)) for item in results]

        # Filter by variant if specified
        if variant:
            variant_lower = variant.lower().strip()
            formatted_data = [
                item for item in formatted_data
                if item.get('variant', '').lower().strip() == variant_lower
            ]

        # Filter by size if specified
        # if size:
        #     size_lower = size.lower().strip()
        #     formatted_data = [
        #         item for item in formatted_data
        #         if item.get('size', '').lower().strip() == size_lower
        #     ]

        # Convert back to list of tuples
        # print(f"check {formatted_data}")
        grouped = defaultdict(list)
        for item in formatted_data:
            restaurant = item.pop('restaurant')  # remove to avoid duplication inside
            grouped[restaurant].append(item)
        grouped_by_restaurant = dict(grouped)
        grouped_by_restaurant = DB_extract_price_data.convert_decimal(grouped_by_restaurant)
        print(grouped_by_restaurant)
        return json.dumps(grouped_by_restaurant, indent=2, ensure_ascii=False)



    @classmethod
    def db_price_inquiry(cls, dish_name: str, restaurant_name: Optional[str] = None,
                         variant: Optional[str] = None, size: Optional[str] = None) -> List[Tuple]:
        """
        Query database for food prices with optional filtering.

        Args:
            dish_name: Name of the dish to search for
            restaurant_name: Name of the restaurant (optional)
            variant: Specific variant to filter by (optional)
            size: Specific size to filter by (optional)

        Returns:
            List of tuples containing price information
        """
        if not dish_name:
            raise ValueError("Dish name is required")

        query, parameters = cls._build_search_query(dish_name, restaurant_name)
        try:
            with cls() as db:
                db.cursor.execute(query, parameters)
                results = db.cursor.fetchall()
                return cls._format_results(results, variant, size)

        except Exception as e:
            # Log the error (consider adding proper logging)
            print(f"Database query failed: {e}")
            raise


# Example usage:
if __name__ == "__main__":
    try:
        # Search across all restaurants
        results = DB_extract_price_data.db_price_inquiry(
            dish_name="Kotthu",
            restaurant_name=None,
            variant="beef"
        )
        # print(results)
        # Search specific restaurant
        results = DB_extract_price_data.db_price_inquiry(
            dish_name="kotthu",
            restaurant_name="Mum’s Food",
            variant="beef"
        )
        # print(results)
    except Exception as e:
        print(f"Error: {e}")