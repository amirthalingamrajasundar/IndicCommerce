import os
from google.cloud import firestore
import logging

DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("SCHEMA_NAME")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirestoreClient:
    def __init__(self):
        """
        Initialize FirestoreClient.
        """
        if not DB_NAME or not COLLECTION_NAME:
            raise ValueError("DB_NAME and COLLECTION_NAME environment variables must be set.")
        self.client = firestore.Client(
            project=os.environ.get("GCP_PROJECT_ID"),
            database=DB_NAME
        )
        self.collection = self.client.collection(COLLECTION_NAME)

    def save_conversation(self, user_id: str, exchange: list[dict]) -> None:
        """
        Save conversation data to Firestore.

        Args:
            user_id (str): Unique identifier for the user.
            exchange (list[dict]): List of dictionaries containing conversation data.
        """
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()

        if doc.exists:
            history = doc.to_dict().get("history", [])
        else:
            history = []

        history.extend(exchange)
        doc_ref.set({"history": history})

    def save_user_data(self, user_id: str, key: str, input_data: any) -> None:
        """
        Save user data to Firestore.

        Args:
            key (str): The key under which to store the user data.
            input_data (any): Input data from the user.
        """
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()

        if doc.exists:
            user_data = doc.to_dict()
        else:
            user_data = {}

        user_data[key] = input_data
        doc_ref.set(user_data)

    def get_full_user_data(self, user_id: str) -> dict:
        """
        Load user data from Firestore.

        Returns:
            dict: user data
        """
        logger.info(f"Fetching user data for user_id: {user_id}")
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()

        logger.debug(f"Document exists: {doc.exists}, Data: {doc.to_dict() if doc.exists else 'None'}")

        if doc.exists:
            return doc.to_dict()
        return {}

    def delete_user(self, user_id: str) -> None:
        """
        Delete user data from Firestore.
        """
        doc_ref = self.collection.document(user_id)
        doc_ref.delete()
