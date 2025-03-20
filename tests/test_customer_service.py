"""
Tests for the customer service.
"""
import os
import pandas as pd
import pytest
from pathlib import Path
from src.services.customer_service import CustomerService
from src.models.contact import ContactInfo

@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    file_path = tmp_path / "test_customer_requests.csv"
    yield file_path
    
    # Cleanup
    if file_path.exists():
        os.unlink(file_path)

def test_save_contact_request(temp_csv_file):
    """Test saving a human representative request."""
    # Create service with test file
    service = CustomerService(requests_file=str(temp_csv_file))
    
    # Create contact info
    contact_info = ContactInfo(
        full_name="John Doe",
        email="john@example.com",
        phone_number="555-123-4567",
        phone="555-123-4567",
        preferred_contact_method="email"
    )
    
    # Save the request
    result = service.save_contact_request(contact_info)
    
    # Check that the operation was successful
    assert result is True
    
    # Check that the file was created
    assert temp_csv_file.exists()
    
    # Check that the data was saved correctly
    df = pd.read_csv(temp_csv_file)
    assert len(df) == 1
    assert df.iloc[0]["full_name"] == "John Doe"
    assert df.iloc[0]["email"] == "john@example.com"
    
def test_save_multiple_requests(temp_csv_file):
    """Test saving multiple requests."""
    service = CustomerService(requests_file=str(temp_csv_file))
    
    # First request
    contact_info1 = ContactInfo(
        full_name="John Doe",
        email="john@example.com",
        phone_number="555-123-4567",
        phone="555-123-4567",
        preferred_contact_method="email"
    )
    service.save_contact_request(contact_info1)
    
    # Second request
    contact_info2 = ContactInfo(
        full_name="Jane Smith",
        email="jane@example.com",
        phone_number="555-987-6543",
        phone="555-987-6543",
        preferred_contact_method="phone"
    )
    service.save_contact_request(contact_info2)
    
    # Check that both records were saved
    df = pd.read_csv(temp_csv_file)
    assert len(df) == 2
    assert "Jane Smith" in df["full_name"].values

def test_get_pending_requests_count(temp_csv_file):
    """Test getting count of pending requests."""
    service = CustomerService(requests_file=str(temp_csv_file))
    
    # Add some test requests
    contact_info = ContactInfo(
        full_name="John Doe",
        email="john@example.com",
        phone_number="555-123-4567",
        phone="555-123-4567"
    )
    service.save_contact_request(contact_info)
    
    # Get the count
    count = service.get_pending_requests_count()
    
    # Check that the count is correct
    assert count == 1 