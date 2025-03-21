import logging
from typing import List, Dict, Optional
from src.models.openai_model import OpenAIModel
from src.models.gemini_model import GeminiModel
from src.agents.order_status_agent import OrderStatusAgent
from src.agents.return_policy_agent import ReturnPolicyAgent
from src.agents.human_rep_agent import HumanRepAgent
from src.services.order_service import OrderService
from src.services.policy_service import PolicyService
from src.services.customer_service import CustomerService
from src.models.contact import ContactInfo
from src.core.config import Config

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Handles processing of chat messages and coordination with agents."""
    
    def __init__(
        self,
        openai_model: Optional[OpenAIModel],
        gemini_model: Optional[GeminiModel],
        order_service: OrderService,
        policy_service: PolicyService,
        customer_service: CustomerService,
        config: Config
    ):
        """Initialize the message processor with required services."""
        self.openai_model = openai_model
        self.gemini_model = gemini_model
        self.order_service = order_service
        self.policy_service = policy_service
        self.customer_service = customer_service
        self.config = config
        
        # Initialize with default model from config
        if config.DEFAULT_MODEL == "gemini":
            if not self.gemini_model:
                raise ValueError("Gemini model is required when DEFAULT_MODEL is 'gemini'")
            self.current_model = self.gemini_model
        else:
            if not self.openai_model:
                raise ValueError("OpenAI model is required when DEFAULT_MODEL is 'openai'")
            self.current_model = self.openai_model
            
        logger.info(f"Initializing message processor with default model: {config.DEFAULT_MODEL}")
        
        self.agents = [
            OrderStatusAgent(self.current_model, self.order_service),
            ReturnPolicyAgent(self.current_model, self.policy_service),
            HumanRepAgent(self.current_model, self.customer_service)
        ]
    
    def switch_model(self, model_name: str) -> None:
        """Switch the current language model."""
        if model_name == "gemini":
            if not self.gemini_model:
                logger.error("Cannot switch to Gemini model as it is not available")
                return
            self.current_model = self.gemini_model
        else:
            if not self.openai_model:
                logger.error("Cannot switch to OpenAI model as it is not available")
                return
            self.current_model = self.openai_model
            
        logger.info(f"Switched to {model_name} model")
        # Update model for all agents
        for agent in self.agents:
            agent.llm = self.current_model
    
    def process_message(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        active_agent: Optional[str] = None,
        agent_info: Optional[Dict] = None
    ) -> tuple[str, Optional[str], Optional[Dict]]:
        """
        Process a user message and return response with updated agent state.
        
        Returns:
            Tuple of (response, new_active_agent, new_agent_info)
        """
        try:
            # First try to continue with active agent if any
            if active_agent:
                for agent in self.agents:
                    if agent.__class__.__name__ == active_agent:
                        logger.info(f"Continuing with active agent {agent.__class__.__name__}")
                        
                        # Restore agent state if needed
                        if isinstance(agent, HumanRepAgent) and agent_info:
                            agent.user_info = agent_info
                            agent.collecting_info = True
                            logger.info(f"Restored agent state: {agent.user_info}")
                        
                        # Let agent handle message
                        response = agent.handle(message, chat_history)
                        
                        # Update agent state
                        new_active_agent = None
                        new_agent_info = None
                        
                        if isinstance(agent, HumanRepAgent):
                            new_agent_info = agent.user_info
                            # Only clear active agent if done collecting info AND contact saved
                            if not agent.collecting_info:
                                if self._try_save_contact(agent):
                                    new_active_agent = None
                                else:
                                    new_active_agent = active_agent
                            else:
                                new_active_agent = active_agent
                        
                        return response, new_active_agent, new_agent_info
            
            # Try to find an appropriate agent
            for agent in self.agents:
                if agent.can_handle(message):
                    logger.info(f"Agent {agent.__class__.__name__} is handling the message")
                    
                    response = agent.handle(message, chat_history)
                    
                    # Set agent state
                    new_active_agent = None
                    new_agent_info = None
                    
                    if isinstance(agent, HumanRepAgent):
                        new_agent_info = agent.user_info
                        if agent.collecting_info:
                            new_active_agent = agent.__class__.__name__
                    
                    return response, new_active_agent, new_agent_info
            
            # If no agent could handle it, use default model
            logger.info(f"No specific agent found, using {self.current_model.__class__.__name__}")
            response = self.current_model.generate_response(message, chat_history)
            return response, None, None
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I'm sorry, I'm experiencing technical difficulties. Please try again later.", None, None
    
    def _try_save_contact(self, agent: HumanRepAgent) -> bool:
        """Try to save contact info from agent state."""
        try:
            if hasattr(agent, 'user_info') and 'name' in agent.user_info and 'email' in agent.user_info and 'phone' in agent.user_info:
                contact_info = ContactInfo(
                    full_name=agent.user_info['name'],
                    email=agent.user_info['email'],
                    phone_number=agent.user_info['phone']
                )
                success = agent.customer_service.save_contact_request(contact_info)
                if success:
                    logger.info(f"Successfully saved contact request for {contact_info.full_name}")
                    return True
                else:
                    logger.error(f"Failed to save contact request for {agent.user_info['name']}")
            return False
        except Exception as e:
            logger.error(f"Error saving contact info: {str(e)}")
            return False 