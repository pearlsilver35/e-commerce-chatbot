"""
Tests for the policy service.
"""
import pytest
from src.services.policy_service import PolicyService

@pytest.fixture
def policy_service():
    """Create a policy service for testing."""
    return PolicyService()

def test_get_general_return_policy(policy_service):
    """Test getting return policy information."""
    policy = policy_service.get_general_return_policy()
    # Check that the return policy contains key information
    assert "30 days" in policy.lower()
    assert "full refund" in policy.lower()

def test_get_return_exceptions(policy_service):
    """Test getting information about non-returnable items."""
    policy = policy_service.get_return_exceptions()
    # Check that the policy mentions specific non-returnable items
    assert "clearance" in policy.lower()
    assert "perishable" in policy.lower()

def test_get_refund_policy(policy_service):
    """Test getting information about the refund process."""
    policy = policy_service.get_refund_policy()
    # Check that the refund process information is correct
    assert "original form of payment" in policy.lower()
    assert "credit card" in policy.lower()

def test_get_shipping_policy(policy_service):
    """Test getting information about shipping policy."""
    policy = policy_service.get_shipping_policy()
    # Check that shipping policy information exists
    assert policy is not None
    assert len(policy) > 0 