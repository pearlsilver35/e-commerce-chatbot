"""
Tests for the return policy agent.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.return_policy_agent import ReturnPolicyAgent
from src.services.policy_service import PolicyService
from src.models.openai_model import OpenAIModel

@pytest.fixture
def mock_model():
    """Create a mock LLM model."""
    mock = MagicMock(spec=OpenAIModel)
    # Mock the generate response to return a predictable response
    mock.generate_response.return_value = "Here is the return policy information you requested."
    return mock

@pytest.fixture
def mock_policy_service():
    """Create a mock policy service."""
    mock = MagicMock(spec=PolicyService)
    mock.get_general_return_policy.return_value = "You can return most items within 30 days of purchase for a full refund."
    mock.get_return_exceptions.return_value = "Some items like clearance and perishable goods cannot be returned."
    mock.get_refund_policy.return_value = "Refunds will be issued to the original form of payment, such as credit card."
    return mock

@pytest.fixture
def return_policy_agent(mock_model, mock_policy_service):
    """Create a ReturnPolicyAgent with mock services."""
    return ReturnPolicyAgent(llm=mock_model, policy_service=mock_policy_service)

def test_handle_general_return_policy(return_policy_agent, mock_model):
    """Test handling a general return policy query."""
    # Call the handle method with return policy intent
    query = "What is the return policy for items I buy?"
    messages = []
    
    result = return_policy_agent.handle(query, messages)
    
    # Verify the model was called
    mock_model.generate_response.assert_called_once()
    
    # Check the response
    assert result == "Here is the return policy information you requested."

def test_can_handle(return_policy_agent, mock_model):
    """Test that the agent can correctly identify messages it can handle."""
    # Setting return values for each call separately instead of side_effect
    mock_model.generate_response.return_value = "yes" 
    
    # Messages about return policies
    assert return_policy_agent.can_handle("What's your return policy?")
    
    # Reset and change the response for the next call
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "yes"
    assert return_policy_agent.can_handle("Can I return an item after 2 weeks?")
    
    # Reset and change the response for non-handled messages
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "no"
    assert not return_policy_agent.can_handle("What's the status of my order?")
    
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "no"
    assert not return_policy_agent.can_handle("I want to speak to a human.")

def test_handle_with_history(return_policy_agent, mock_model):
    """Test handling a query with conversation history."""
    # Reset and set the return value
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "Information about returns with history."
    
    # Create a history
    history = [
        {"role": "user", "content": "Hello, I have a question about returns."},
        {"role": "assistant", "content": "I'd be happy to help with return questions."}
    ]
    
    # Call handle with history
    query = "Can I return opened items?"
    result = return_policy_agent.handle(query, history)
    
    # Verify model was called
    mock_model.generate_response.assert_called_once()
    
    # Check the response
    assert result == "Information about returns with history."

def test_handle_non_returnable_items_query(return_policy_agent, mock_model):
    """Test handling a query about non-returnable items."""
    # Reset and set the return value
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "Information about non-returnable items."
    
    # Call the handle method
    query = "Are there any items that cannot be returned?"
    messages = []
    
    result = return_policy_agent.handle(query, messages)
    
    # Verify the model was called
    mock_model.generate_response.assert_called_once()
    
    # Check the response
    assert result == "Information about non-returnable items."

def test_handle_refund_process_query(return_policy_agent, mock_model):
    """Test handling a query about the refund process."""
    # Reset and set the return value
    mock_model.reset_mock()
    mock_model.generate_response.return_value = "Information about the refund process."
    
    # Call the handle method
    query = "How will I get my refund?"
    messages = []
    
    result = return_policy_agent.handle(query, messages)
    
    # Verify the model was called
    mock_model.generate_response.assert_called_once()
    
    # Check the response
    assert result == "Information about the refund process." 