from typing import List, Dict, Any
from langchain_core.documents import Document
from .vector_store import VectorStore


class Retriever:
    """Handles retrieval of relevant project information using RAG."""

    def __init__(self, vector_store: VectorStore):
        """Initialize the retriever.

        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store

    def retrieve_relevant_info(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant information for a query.

        Args:
            query: Search query
            k: Number of documents to retrieve

        Returns:
            List of relevant documents
        """
        return self.vector_store.similarity_search(query, k=k)

    def get_project_context(self, project_path: str) -> str:
        """Get contextual information about the project.

        Args:
            project_path: Path to the project

        Returns:
            Contextual string about the project
        """
        docs = self.vector_store.similarity_search(project_path, k=3)

        if not docs:
            return ""

        return " ".join(
            doc.page_content[:500] for doc in docs[:3]
        )

    def get_code_examples(self, technology: str) -> List[str]:
        """Get code examples for a specific technology.

        Args:
            technology: Technology name

        Returns:
            List of code examples
        """
        docs = self.retrieve_relevant_info(f"code examples for {technology}", k=3)
        return [doc.page_content for doc in docs]

    def get_best_practices(self, category: str) -> List[str]:
        """Get best practices for a category.

        Args:
            category: Category like "security", "performance", etc.

        Returns:
            List of best practices
        """
        docs = self.retrieve_relevant_info(f"best practices for {category}", k=3)
        return [doc.page_content for doc in docs]
