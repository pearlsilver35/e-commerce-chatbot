# E-commerce Chatbot Tests

This directory contains the test suite for the e-commerce customer support chatbot application.

## Test Structure

The tests are organized to match the structure of the main application:

- `test_app.py` - Tests for the main Streamlit application
- `test_conversation_service.py` - Tests for the conversation persistence service
- `test_customer_service.py` - Tests for customer service functions
- `test_order_service.py` - Tests for order management
- `test_policy_service.py` - Tests for return policy information
- `test_return_policy_agent.py` - Tests for the return policy agent

## Running Tests

### With Docker

The simplest way to run tests is using Docker:

```bash
# Run all tests
docker-compose run test

# Run a specific test file
docker-compose run test pytest tests/test_order_service.py -v

# Run a specific test
docker-compose run test pytest tests/test_order_service.py::test_get_order_status_existing_order -v
```

### Without Docker

To run tests locally without Docker:

```bash
# Ensure you're in the project root directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_order_service.py -v

# Run a specific test
pytest tests/test_order_service.py::test_get_order_status_existing_order -v
```

## Test Coverage

To generate a test coverage report:

```bash
# With Docker
docker-compose run test pytest tests/ --cov=src --cov-report=term-missing

# Without Docker
pytest tests/ --cov=src --cov-report=term-missing
```

## Adding New Tests

When adding new tests:

1. Follow the existing pattern of test files matching the application's structure
2. Use fixtures from `conftest.py` for common test setup
3. Make sure to write both positive and negative test cases
4. Use mocks for external dependencies to keep tests fast and reliable 