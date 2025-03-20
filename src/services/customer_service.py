"""
Customer service implementation.
"""
import logging
from typing import Dict, Optional, List
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

from src.models.contact import ContactInfo

logger = logging.getLogger(__name__)

class CustomerService:
    """Service for managing customer information and support requests."""
    
    def __init__(self, requests_file: str = "data/customer_requests.csv"):
        """
        Initialize customer service.
        
        Args:
            requests_file: Path to the customer requests CSV file
        """
        self.requests_file = Path(requests_file)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.requests_file), exist_ok=True)
        self._load_requests()
    
    def _load_requests(self) -> None:
        """Load customer requests from CSV file."""
        try:
            if self.requests_file.exists():
                self.requests_df = pd.read_csv(self.requests_file)
            else:
                # Create empty DataFrame with required columns
                self.requests_df = pd.DataFrame(columns=[
                    "timestamp",
                    "full_name",
                    "email",
                    "phone_number"
                ])
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(self.requests_file), exist_ok=True)
                self.requests_df.to_csv(self.requests_file, index=False)
                logger.info(f"Created new requests file at {self.requests_file}")
        except Exception as e:
            logger.error(f"Error loading customer requests: {str(e)}")
            self.requests_df = pd.DataFrame(columns=[
                "timestamp",
                "full_name",
                "email",
                "phone_number"
            ])
    
    def save_contact_request(self, contact_info: ContactInfo) -> bool:
        """
        Save a customer contact request to CSV file.
        
        Args:
            contact_info: Contact information to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Create new request row
            new_request = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(),
                "full_name": contact_info.full_name,
                "email": contact_info.email,
                "phone_number": contact_info.phone_number
            }])
            
            # Append to DataFrame
            if hasattr(self, 'requests_df'):
                self.requests_df = pd.concat([self.requests_df, new_request], ignore_index=True)
            else:
                self.requests_df = new_request
            
            # Make sure directory exists
            os.makedirs(os.path.dirname(self.requests_file), exist_ok=True)
            
            # Save to CSV
            self.requests_df.to_csv(self.requests_file, index=False)
            logger.info(f"Saved contact request for {contact_info.full_name} to {self.requests_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving contact request: {str(e)}")
            return False
    
    def get_pending_requests_count(self) -> int:
        """Get the number of pending customer requests."""
        try:
            return len(self.requests_df)
        except Exception:
            return 0 