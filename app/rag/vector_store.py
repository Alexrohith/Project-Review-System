import os
import pickle
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


class VectorStore:
    """Handles vector storage and retrieval using FAISS."""

    def __init__(self, index_path: str = "data/vector_index"):
        """Initialize the vector store.

        Args:
            index_path: Path to store/load the FAISS index
        """
        self.index_path = index_path
        # Use local sentence-transformers embeddings instead of OpenAI
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore: Optional[FAISS] = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.index_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_path, self.embeddings, allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self.vectorstore = None
        else:
            self.vectorstore = None

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of Document objects to add
        """
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)
        self._save_index()

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)

    def _save_index(self) -> None:
        """Save the index to disk."""
        if self.vectorstore is not None:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            self.vectorstore.save_local(self.index_path)

    def clear_index(self) -> None:
        """Clear the vector store."""
        self.vectorstore = None
        if os.path.exists(self.index_path):
            import shutil
            shutil.rmtree(self.index_path)
