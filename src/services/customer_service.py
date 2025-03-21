"""
Customer service implementation.
"""
import logging
import os
from typing import Dict, Optional, List
import pandas as pd
from pathlib import Path
from datetime import datetime

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
        # Resolve to absolute path when in docker container
        if requests_file.startswith('/'):
            self.requests_file = Path(requests_file)
        else:
            # Use relative path from current directory
            self.requests_file = Path(os.path.abspath(requests_file))
            
        logger.info(f"Customer requests file path: {self.requests_file}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.requests_file), exist_ok=True)
        self._load_requests()
    
    def _load_requests(self) -> None:
        """Load customer requests from CSV file."""
        try:
            if self.requests_file.exists():
                logger.info(f"Loading existing customer requests from {self.requests_file}")
                self.requests_df = pd.read_csv(self.requests_file)
                logger.info(f"Loaded {len(self.requests_df)} existing customer requests")
            else:
                # Create empty DataFrame with required columns
                logger.info(f"Customer requests file not found, creating new file at {self.requests_file}")
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
            logger.info(f"Attempting to save contact request for {contact_info.full_name}")
            
            # Make sure we have the required fields
            if not contact_info.full_name or not contact_info.email or not contact_info.phone_number:
                logger.error("Missing required contact information")
                return False
                
            # Reload requests to ensure we have the latest data
            self._load_requests()
            
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
            
            # Make sure directory exists with proper permissions
            dirname = os.path.dirname(self.requests_file)
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True, mode=0o777)
                logger.info(f"Created directory with full permissions: {dirname}")
            
            # Make sure the file path is good
            logger.info(f"Saving to file: {self.requests_file} (exists: {self.requests_file.exists()})")
            
            # Save to CSV
            self.requests_df.to_csv(self.requests_file, index=False)
            logger.info(f"Saved contact request for {contact_info.full_name} to {self.requests_file}")
            
            # Set file permissions to ensure it's readable/writable
            try:
                os.chmod(self.requests_file, 0o666)  # Read/write for everyone
                logger.info(f"Set file permissions to read/write for file: {self.requests_file}")
            except Exception as perm_err:
                logger.warning(f"Could not set file permissions: {str(perm_err)}")
            
            # Verify the file was actually saved
            if self.requests_file.exists():
                file_size = os.path.getsize(self.requests_file)
                logger.info(f"File size after save: {file_size} bytes")
                
            return True
        except Exception as e:
            logger.error(f"Error saving contact request: {str(e)}", exc_info=True)
            return False
    
    def get_pending_requests_count(self) -> int:
        """Get the number of pending customer requests."""
        try:
            return len(self.requests_df)
        except Exception:
            return 0 