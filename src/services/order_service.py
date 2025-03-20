"""
Order service implementation.
"""
import logging
from typing import Dict, Optional
import pandas as pd
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class OrderService:
    """Service for handling order-related operations."""
    
    def __init__(self, orders_file: str = "data/orders.csv"):
        """
        Initialize order service.
        
        Args:
            orders_file: Path to the orders CSV file
        """
        self.orders_file = Path(orders_file)
        os.makedirs(os.path.dirname(self.orders_file), exist_ok=True)
        self._load_orders()
    
    def _load_orders(self) -> None:
        """Load orders from CSV file."""
        try:
            if self.orders_file.exists():
                self.orders_df = pd.read_csv(self.orders_file)
                logger.info(f"Loaded {len(self.orders_df)} orders from {self.orders_file}")
            else:
                self.orders_df = pd.DataFrame(columns=[
                    "order_id",
                    "customer_name",
                    "date",
                    "status",
                    "items",
                    "total_price",
                    "shipping_address",
                    "tracking_number",
                    "estimated_delivery"
                ])
                logger.info(f"Creating new orders file at {self.orders_file}")
                self.orders_df.to_csv(self.orders_file, index=False)
        except Exception as e:
            logger.error(f"Error loading orders: {str(e)}")
            self.orders_df = pd.DataFrame(columns=[
                "order_id",
                "customer_name",
                "date",
                "status",
                "items",
                "total_price",
                "shipping_address",
                "tracking_number",
                "estimated_delivery"
            ])
    
    def get_order_status(self, order_id: str) -> str:
        """
        Get the status of an order.
        
        Args:
            order_id: The order ID to look up
            
        Returns:
            str: Order status message
        """
        try:
            order = self.orders_df[self.orders_df["order_id"] == order_id]
            if order.empty:
                return f"I couldn't find an order with ID {order_id}. Please check the order ID and try again."
            
            status = order.iloc[0]["status"]
            estimated_delivery = order.iloc[0]["estimated_delivery"]
            tracking_number = order.iloc[0].get("tracking_number", "Not available")
            
            if status.lower() == "shipped":
                return f"Your order {order_id} has been shipped and is estimated to arrive by {estimated_delivery}. Tracking number: {tracking_number}"
            elif status.lower() == "processing":
                return f"Your order {order_id} is currently being processed. Estimated delivery: {estimated_delivery}. We'll notify you when it ships."
            elif status.lower() == "delivered":
                return f"Your order {order_id} was delivered on {estimated_delivery}. Thank you for shopping with us!"
            elif status.lower() == "cancelled":
                return f"Your order {order_id} has been cancelled. If you have any questions, please contact customer service."
            elif status.lower() == "pending":
                return f"Your order {order_id} is pending payment confirmation. Once confirmed, it will be processed. Estimated delivery: {estimated_delivery}."
            else:
                return f"Your order {order_id} is currently {status}. Estimated delivery: {estimated_delivery}."
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return "I'm sorry, I'm having trouble checking your order status. Please try again later." 