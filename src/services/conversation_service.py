"""
Conversation history service using ChromaDB for persistent storage.
"""
import os
import logging
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.core.config import Config

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation history with persistent storage."""
    
    def __init__(self, config: Config):
        """
        Initialize conversation service with ChromaDB.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize ChromaDB and create collection if it doesn't exist."""
        try:
            # Setup ChromaDB client with persistent storage
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            # Add authentication if enabled
            if self.config.CHROMA_USE_AUTH:
                logger.info("Initializing ChromaDB with authentication")
                self.client = chromadb.PersistentClient(
                    path=self.config.CHROMA_DB_PATH,
                    settings=settings,
                    chroma_server_auth_credentials=(
                        self.config.CHROMA_USERNAME,
                        self.config.CHROMA_PASSWORD
                    )
                )
            else:
                logger.info("Initializing ChromaDB without authentication")
                self.client = chromadb.PersistentClient(
                    path=self.config.CHROMA_DB_PATH,
                    settings=settings
                )
            
            # Always use default embedding function to avoid OpenAI API calls
            # This ensures we don't hit API limits or require OpenAI keys
            # Initialize embedding function before creating/getting collection to ensure
            # it's downloaded and cached before first use
            logger.info("Loading default embedding function for ChromaDB...")
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            logger.info("Default embedding function loaded successfully")
            
            # Get or create collection for storing conversations
            try:
                self.collection = self.client.get_collection(
                    name=self.config.CHROMA_COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Successfully connected to existing ChromaDB collection: {self.config.CHROMA_COLLECTION_NAME}")
            except ValueError:
                self.collection = self.client.create_collection(
                    name=self.config.CHROMA_COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Created new ChromaDB collection: {self.config.CHROMA_COLLECTION_NAME}")
                
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def _serialize_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Serialize messages to JSON string.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            str: JSON string of messages
        """
        return json.dumps(messages)
    
    def _deserialize_messages(self, json_str: str) -> List[Dict[str, str]]:
        """
        Deserialize JSON string to messages.
        
        Args:
            json_str: JSON string of messages
            
        Returns:
            List[Dict[str, str]]: List of message dictionaries
        """
        return json.loads(json_str)
    
    def save_conversation(self, user_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Save or update a conversation for a user.
        
        Args:
            user_id: Unique identifier for the user
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not messages:
            return True  # Nothing to save
            
        try:
            # Create document ID
            doc_id = f"conversation_{user_id}"
            
            # Check if conversation exists
            results = self.collection.get(ids=[doc_id], include=[])
            
            # Get the most recent user message for metadata
            recent_user_messages = [m for m in messages if m["role"] == "user"]
            latest_query = recent_user_messages[-1]["content"] if recent_user_messages else ""
            
            # Prepare metadata
            metadata = {
                "user_id": user_id,
                "last_updated": datetime.now().isoformat(),
                "message_count": len(messages),
                "latest_query": latest_query[:100]  # Truncate for metadata
            }
            
            # Serialize messages
            serialized_messages = self._serialize_messages(messages)
            
            # Upsert to collection
            if results and results["ids"]:
                # Update existing conversation
                self.collection.update(
                    ids=[doc_id],
                    documents=[serialized_messages],
                    metadatas=[metadata]
                )
            else:
                # Add new conversation
                self.collection.add(
                    ids=[doc_id],
                    documents=[serialized_messages],
                    metadatas=[metadata]
                )
                
            logger.info(f"Saved conversation for user {user_id} with {len(messages)} messages")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False
    
    def load_conversation(self, user_id: str) -> List[Dict[str, str]]:
        """
        Load a conversation for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List[Dict[str, str]]: List of message dictionaries with 'role' and 'content'
        """
        try:
            # Create document ID
            doc_id = f"conversation_{user_id}"
            
            # Attempt to retrieve the conversation
            results = self.collection.get(ids=[doc_id])
            
            # Check if any results were found
            if results and results["documents"] and results["documents"][0]:
                serialized_messages = results["documents"][0]
                messages = self._deserialize_messages(serialized_messages)
                logger.info(f"Loaded conversation for user {user_id} with {len(messages)} messages")
                return messages
            else:
                logger.info(f"No existing conversation found for user {user_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            return []
    
    def delete_conversation(self, user_id: str) -> bool:
        """
        Delete a conversation for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create document ID
            doc_id = f"conversation_{user_id}"
            
            # Delete the conversation
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted conversation for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False
    
    def query_similar_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Find conversations similar to the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict]: List of similar conversations with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            if results and results["documents"] and results["documents"][0]:
                conversations = []
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if i < len(results["metadatas"][0]) else {}
                    messages = self._deserialize_messages(doc)
                    conversations.append({
                        "metadata": metadata,
                        "messages": messages
                    })
                return conversations
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error querying similar conversations: {str(e)}")
            return [] 