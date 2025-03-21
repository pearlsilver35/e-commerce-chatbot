import logging
from typing import Dict, Optional, List, Tuple

from src.core.config import Config
from src.models.openai_model import OpenAIModel
from src.models.gemini_model import GeminiModel
from src.services.order_service import OrderService
from src.services.policy_service import PolicyService
from src.services.customer_service import CustomerService
from src.services.conversation_service import ConversationService
from src.core.session_manager import SessionManager
from src.core.message_processor import MessageProcessor
from src.ui.chat_ui import ChatUI
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class AppFactory:
    """Factory for creating and initializing application components."""
    
    @staticmethod
    def create_app_components() -> Dict:
        """
        Create and initialize all application components.
        
        Returns:
            Dict containing all initialized components
        """
        components = {}
        
        # Initialize config
        config = Config()
        config.validate()
        components['config'] = config
        
        # Preload embedding function
        try:
            logger.info("Preloading ChromaDB embedding function...")
            embedding_functions.DefaultEmbeddingFunction()
            logger.info("ChromaDB embedding function loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to preload embedding function: {str(e)}")
        
        # Initialize services
        components['order_service'] = OrderService(config.ORDERS_FILE)
        components['policy_service'] = PolicyService(config.POLICIES_FILE)
        components['customer_service'] = CustomerService(config.CUSTOMER_REQUESTS_FILE)
        components['conversation_service'] = ConversationService(config)
        
        # Initialize models with error handling
        components['openai_model'], components['gemini_model'] = AppFactory._init_models(config)
        
        # Initialize core components
        components['session_manager'] = SessionManager(default_model=config.DEFAULT_MODEL)
        components['message_processor'] = MessageProcessor(
            components['openai_model'],
            components['gemini_model'],
            components['order_service'],
            components['policy_service'],
            components['customer_service'],
            config
        )
        
        # Initialize UI
        components['ui'] = ChatUI()
        
        return components
    
    @staticmethod
    def _init_models(config: Config) -> Tuple[Optional[OpenAIModel], Optional[GeminiModel]]:
        """
        Initialize language models with error handling.
        
        Args:
            config: Application configuration
            
        Returns:
            Tuple of (openai_model, gemini_model)
        """
        openai_model = None
        gemini_model = None
        
        try:
            openai_model = OpenAIModel(config)
            gemini_model = GeminiModel(config)
            logger.info(f"Default model from config: {config.DEFAULT_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing all models: {str(e)}")
            # Try to initialize just the default model
            if config.DEFAULT_MODEL == "openai":
                try:
                    openai_model = OpenAIModel(config)
                    logger.warning("Failed to initialize Gemini model, but continuing with OpenAI")
                except Exception as e2:
                    logger.error(f"Failed to initialize OpenAI model: {str(e2)}")
                    raise ValueError("Could not initialize required OpenAI model")
            elif config.DEFAULT_MODEL == "gemini":
                try:
                    gemini_model = GeminiModel(config)
                    logger.warning("Failed to initialize OpenAI model, but continuing with Gemini")
                except Exception as e2:
                    logger.error(f"Failed to initialize Gemini model: {str(e2)}")
                    raise ValueError("Could not initialize required Gemini model")
        
        return openai_model, gemini_model
    
    @staticmethod
    def get_available_models(openai_model: Optional[OpenAIModel], gemini_model: Optional[GeminiModel]) -> List[str]:
        """
        Determine which models are available.
        
        Args:
            openai_model: OpenAI model instance or None
            gemini_model: Gemini model instance or None
            
        Returns:
            List of available model names
        """
        available_models = []
        if openai_model:
            available_models.append("openai")
        if gemini_model:
            available_models.append("gemini")
        return available_models 