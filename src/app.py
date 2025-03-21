"""
Main application for the e-commerce customer support chatbot.
"""
import logging
import streamlit as st

from src.core.app_factory import AppFactory
from src.core.conversation_manager import ConversationManager
from src.core.input_handler import InputHandler
from src.utils.error_handler import ErrorHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEBUG_SESSION = False

class ChatbotApp:
    """Main chatbot application."""
    
    def __init__(self):
        """Initialize the chatbot application."""
        # Create app components
        try:
            self.components = AppFactory.create_app_components()
            
            # Create helper objects
            self.conversation_manager = ConversationManager(
                self.components['session_manager'],
                self.components['conversation_service']
            )
            
            self.input_handler = InputHandler(
                self.components['session_manager'],
                self.components['message_processor']
            )
            
            # Load conversation history
            self.conversation_manager.load_conversation()
            
            # Log debug info if enabled
            if DEBUG_SESSION:
                logger.info(
                    f"Session state initialized with user_id: {self.components['session_manager'].user_id}"
                )
        except Exception as e:
            ErrorHandler.handle_error(e, "Failed to initialize the application")
    
    def _handle_model_change(self, new_model: str) -> None:
        """Handle model change from UI."""
        session_manager = self.components['session_manager']
        message_processor = self.components['message_processor']
        
        if new_model != session_manager.model:
            session_manager.model = new_model
            message_processor.switch_model(new_model)
            logger.info(f"Switched to {new_model} model")
    
    def run(self) -> None:
        """Run the Streamlit application."""
        # Get components
        ui = self.components['ui']
        session_manager = self.components['session_manager']
        openai_model = self.components['openai_model']
        gemini_model = self.components['gemini_model']
        
        # Determine available models
        available_models = AppFactory.get_available_models(openai_model, gemini_model)
        
        # Render header
        ui.render_header()
        
        # Render existing messages
        ui.render_messages(session_manager.messages)
        
        # Handle user input
        if prompt := ui.render_chat_input():
            # Process the input
            response = self.input_handler.handle_user_input(prompt, ui)
            
            # Save conversation if response was generated
            if response:
                self.conversation_manager.save_conversation()
        
        # Render sidebar with settings
        ui.render_sidebar(
            session_manager.model,
            self._handle_model_change,
            self.conversation_manager.clear_conversation,
            available_models
        )

def main():
    """Main entry point for the application."""
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        ErrorHandler.handle_error(e)

if __name__ == "__main__":
    main() 