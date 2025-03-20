"""
Shared fixtures for pytest tests.
"""
import pytest
import tempfile
import os
import shutil
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after the test
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_orders_df():
    """Create a sample orders DataFrame."""
    return pd.DataFrame({
        "order_id": ["ORD-123", "ORD-456", "ORD-789"],
        "customer_name": ["John Doe", "Jane Smith", "Sam Brown"],
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "status": ["delivered", "processing", "shipped"],
        "items": ["Laptop, Mouse", "Headphones", "Keyboard"],
        "total_price": [1200.0, 150.0, 80.0],
        "shipping_address": ["123 Main St", "456 Oak Ave", "789 Pine Ln"],
        "email": ["john@example.com", "jane@example.com", "sam@example.com"]
    })

@pytest.fixture
def mock_llm():
    """Create a mock LLM model."""
    mock = MagicMock()
    mock.generate_response.return_value = "This is a mock response from the LLM."
    return mock 