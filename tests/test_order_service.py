"""
Tests for the order service.
"""
import os
import pandas as pd
import pytest
from pathlib import Path
from src.services.order_service import OrderService

@pytest.fixture
def test_orders_file(tmp_path):
    """Create a temporary orders file for testing."""
    test_file = tmp_path / "test_orders.csv"
    
    # Create test data
    orders_data = pd.DataFrame({
        "order_id": ["ORD-123", "ORD-456", "ORD-789"],
        "customer_name": ["John Doe", "Jane Smith", "Sam Brown"],
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "status": ["delivered", "processing", "shipped"],
        "items": ["Laptop, Mouse", "Headphones", "Keyboard"],
        "total_price": [1200.0, 150.0, 80.0],
        "shipping_address": ["123 Main St", "456 Oak Ave", "789 Pine Ln"],
        "email": ["john@example.com", "jane@example.com", "sam@example.com"],
        "estimated_delivery": ["2023-01-05", "2023-01-10", "2023-01-08"]  # Add this field
    })
    
    orders_data.to_csv(test_file, index=False)
    yield test_file
    
    # Cleanup after tests
    if test_file.exists():
        os.unlink(test_file)

def test_load_orders(test_orders_file):
    """Test that orders are loaded correctly."""
    service = OrderService(orders_file=str(test_orders_file))
    assert len(service.orders_df) == 3
    assert "ORD-123" in service.orders_df["order_id"].values

def test_get_order_status_existing_order(test_orders_file):
    """Test retrieving status for an existing order."""
    service = OrderService(orders_file=str(test_orders_file))
    status = service.get_order_status("ORD-123")
    # Check for a match with the actual format of the response message
    assert "order" in status.lower() and "ord-123" in status.lower()
    assert "delivered" in status.lower() or "status" in status.lower()

def test_get_order_status_nonexistent_order(test_orders_file):
    """Test retrieving status for a non-existent order."""
    service = OrderService(orders_file=str(test_orders_file))
    status = service.get_order_status("ORD-999")
    # Check for a match with the actual format of the response message
    assert "couldn't find" in status.lower() or "not found" in status.lower()
    assert "ord-999" in status.lower() 