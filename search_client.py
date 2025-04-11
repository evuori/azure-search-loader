import os
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from dotenv import load_dotenv

load_dotenv()

class AzureSearchClient:
    def __init__(self):
        self.service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        
        if not all([self.service_name, self.api_key, self.index_name, self.endpoint]):
            raise ValueError("Missing required Azure Search configuration in environment variables")
        
        self.credential = AzureKeyCredential(self.api_key)
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
    
    def search(
        self,
        search_text: str,
        filter: Optional[str] = None,
        select: Optional[List[str]] = None,
        top: int = 5,
        include_total_count: bool = True,
        query_type: QueryType = QueryType.SIMPLE
    ) -> Dict[str, Any]:
        """
        Perform a search query on the Azure Search index.
        
        Args:
            search_text: The text to search for
            filter: OData filter expression
            select: List of fields to return
            top: Number of results to return
            include_total_count: Whether to include total count of results
            query_type: Type of query to perform (SIMPLE, FULL, SEMANTIC)
            
        Returns:
            Dictionary containing search results and metadata
        """
        results = self.client.search(
            search_text=search_text,
            filter=filter,
            select=select,
            top=top,
            include_total_count=include_total_count,
            query_type=query_type
        )
        
        return {
            "results": list(results),
            "count": results.get_count() if include_total_count else None
        }
    
    def suggest(
        self,
        search_text: str,
        suggester_name: str,
        select: Optional[List[str]] = None,
        top: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get search suggestions from the Azure Search index.
        
        Args:
            search_text: The text to get suggestions for
            suggester_name: Name of the suggester to use
            select: List of fields to return
            top: Number of suggestions to return
            
        Returns:
            List of suggestion results
        """
        results = self.client.suggest(
            search_text=search_text,
            suggester_name=suggester_name,
            select=select,
            top=top
        )
        
        return list(results)
    
    def autocomplete(
        self,
        search_text: str,
        suggester_name: str,
        mode: str = "oneTerm",
        top: int = 5
    ) -> List[str]:
        """
        Get autocomplete suggestions from the Azure Search index.
        
        Args:
            search_text: The text to get autocomplete suggestions for
            suggester_name: Name of the suggester to use
            mode: Autocomplete mode ("oneTerm" or "twoTerms")
            top: Number of suggestions to return
            
        Returns:
            List of autocomplete suggestions
        """
        results = self.client.autocomplete(
            search_text=search_text,
            suggester_name=suggester_name,
            mode=mode,
            top=top
        )
        
        return [result.text for result in results] 