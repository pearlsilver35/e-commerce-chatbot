# E-commerce Customer Support Chatbot Documentation

This document contains detailed technical information about the E-commerce Customer Support Chatbot project architecture, development guidelines, and more.

## Architecture

The application follows a clean, modular architecture:

```
src/
├── agents/           # Specialized conversation agents
│   ├── order_status_agent.py
│   ├── return_policy_agent.py
│   └── human_rep_agent.py
├── core/            # Core application components
│   └── config.py    # Configuration management
├── interfaces/      # Abstract base classes
│   ├── agent.py     # Agent interface
│   └── llm.py       # LLM interface
├── models/          # LLM model implementations
│   ├── openai_model.py
│   └── gemini_model.py
├── services/        # Business logic and data access
│   ├── order_service.py
│   ├── policy_service.py
│   └── customer_service.py
└── app.py          # Main application entry point
```

### Key Components

- **Agents**: Specialized handlers for different types of customer queries
- **Services**: Business logic and data access layer
- **Models**: LLM implementations with consistent interfaces
- **Interfaces**: Abstract base classes defining component contracts
- **Core**: Essential application components like configuration

## Technical Features

- **Extensible Design**: Easy to add new agents, models, and services
- **Docker Support**: Easy containerized deployment
- **SOLID Principles**: Application follows modern software design principles
- **Type Hints**: Comprehensive type annotations throughout codebase

## Docker Features

The Docker setup includes:
- Production-ready configuration
- Health checks for service monitoring
- Volume mounting for persistent data
- Automatic service restart
- Test environment for running the test suite

## Usage Details

The chatbot can handle various types of customer queries:

- **Order Status**: Ask about order tracking and status
- **Return Policies**: Get information about returns and refunds
- **Human Representative**: Request to speak with a customer service representative
- **General Queries**: Any other questions will be handled by the LLM model

### UI Features

- Switch between OpenAI and Gemini models using the sidebar
- Clear chat history with a single click
- Persistent conversation history
- Automatic fallback to human representative when needed

## Development Guidelines

### Adding New Agents

1. Create a new agent class in `src/agents/`
2. Implement the `AgentInterface`
3. Add the agent to the list in `src/app.py`

Example:
```python
from interfaces.agent import AgentInterface

class ProductRecommendationAgent(AgentInterface):
    def __init__(self, product_service, llm_model):
        self.product_service = product_service
        self.llm_model = llm_model
        
    def can_handle(self, query: str) -> bool:
        # Logic to determine if this agent can handle the query
        
    def process(self, query: str, context: dict) -> str:
        # Logic to process the query and return a response
```

### Adding New LLM Models

1. Create a new model class in `src/models/`
2. Implement the `LLMInterface`
3. Update the model selection in `src/app.py`

### Adding New Services

1. Create a new service class in `src/services/`
2. Implement the required business logic
3. Inject the service into the appropriate agents

## Testing

### Local Testing
```bash
pytest
```

### Docker Testing
```bash
docker-compose run test
```

### Test Structure

The project includes a comprehensive test suite located in the `/tests` directory:

#### Test Files
- **test_app.py**: Tests for the main application features and UI interactions
- **test_conversation_service.py**: Tests for conversation history and management
- **test_return_policy_agent.py**: Tests for the return policy specialized agent
- **test_customer_service.py**: Tests for customer data and interactions
- **test_policy_service.py**: Tests for policy retrieval and management
- **test_order_service.py**: Tests for order processing and tracking
- **conftest.py**: Contains pytest fixtures and test configuration

The test suite covers:
- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing interactions between components
- **UI Tests**: Testing the Streamlit interface functionality

### Test Configuration

The `conftest.py` file provides common fixtures used across multiple test files, helping to:
- Set up test environments
- Create mock data
- Provide dependency injection for tests
- Reset state between test runs

### Test Documentation

The `/tests/README.md` file contains additional documentation specific to testing, including:
- Test organization principles
- Running tests (with and without Docker)
- Generating test coverage reports
- Guidelines for adding new tests

#### Running Tests

With Docker:
```bash
# Run all tests
docker-compose run test

# Run a specific test file
docker-compose run test pytest tests/test_order_service.py -v

# Run a specific test
docker-compose run test pytest tests/test_order_service.py::test_get_order_status_existing_order -v
```

Without Docker:
```bash
# Ensure you're in the project root directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run all tests
pytest tests/ -v
```

#### Test Coverage

To generate a test coverage report:
```bash
# With Docker
docker-compose run test pytest tests/ --cov=src --cov-report=term-missing

# Without Docker
pytest tests/ --cov=src --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Deployment

### Production Configuration

For production deployment, consider the following:
1. Set up proper API key management
2. Configure logging
3. Set up monitoring and alerts
4. Consider using a CDN for static assets

### Scaling Considerations

- The application can be scaled horizontally by adding more containers
- Consider using a load balancer for high-traffic deployments
- Database sharding may be necessary for large conversation history storage

## Troubleshooting

Common issues and their solutions:
- API key authentication errors: Check environment variables
- Model timeout issues: Adjust request timeout settings
- Memory issues: Check container resource limits 