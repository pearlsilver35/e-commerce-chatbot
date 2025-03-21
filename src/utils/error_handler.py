import logging
import traceback
import streamlit as st
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application."""
    
    @staticmethod
    def handle_error(e: Exception, user_message: str = "An error occurred. Please try again later.") -> None:
        """
        Handle exceptions by logging and displaying an error to the user.
        
        Args:
            e: The exception that occurred
            user_message: Message to display to the user
        """
        logger.error(f"Application error: {str(e)}")
        logger.debug(traceback.format_exc())
        st.error(user_message)
    
    @staticmethod
    def safe_execute(func: Callable, *args, default_return: Any = None, 
                      error_message: str = "An error occurred. Please try again later.", 
                      **kwargs) -> Any:
        """
        Execute a function safely, handling any exceptions.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            default_return: Value to return if function raises an exception
            error_message: Message to display to the user on error
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Either the function result or default_return if an exception occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, error_message)
            return default_return 