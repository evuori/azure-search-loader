from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    ComplexField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_search_index_client():
    """Create and return a SearchIndexClient."""
    return SearchIndexClient(
        endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    )

def create_index():
    """Create a new search index with the required schema."""
    index_client = get_search_index_client()
    
    # Define the fields for the index
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, 
                       searchable=True, retrievable=True),
        SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                   searchable=True, vector_search_dimensions=3072,  # OpenAI embeddings dimension
                   vector_search_profile_name="my-vector-profile"),
        ComplexField(name="metadata", fields=[
            SimpleField(name="section_number", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="section_title", type=SearchFieldDataType.String, filterable=True, searchable=True),
            SimpleField(name="requirement_ids", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
            SimpleField(name="document_part", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="chunk_id", type=SearchFieldDataType.Int32, filterable=True),
            SimpleField(name="total_chunks", type=SearchFieldDataType.Int32, filterable=True),
            SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="project_name", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="feature_name", type=SearchFieldDataType.String, filterable=True)
        ])
    ]
    
    # Define vector search configuration
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-algorithm-config"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="my-algorithm-config"
            )
        ]
    )
    
    # Define semantic search configuration with more detailed settings
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="metadata/section_title"),
            content_fields=[SemanticField(field_name="content")],
            keywords_fields=[SemanticField(field_name="metadata/requirement_ids")]
        )
    )
    
    # Create the index with semantic search enabled
    index = SearchIndex(
        name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        fields=fields,
        vector_search=vector_search,
        semantic_search=SemanticSearch(
            configurations=[semantic_config],
            default_configuration_name="my-semantic-config"
        )
    )
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"Index '{result.name}' created/updated successfully")
        return result
    except Exception as e:
        print(f"Error creating/updating index: {str(e)}")
        raise

def delete_index():
    """Delete the search index."""
    index_client = get_search_index_client()
    try:
        index_client.delete_index(os.getenv("AZURE_SEARCH_INDEX_NAME"))
        print(f"Index '{os.getenv('AZURE_SEARCH_INDEX_NAME')}' deleted successfully")
    except Exception as e:
        print(f"Error deleting index: {str(e)}")
        raise

def get_index():
    """Get the current index definition."""
    index_client = get_search_index_client()
    try:
        index = index_client.get_index(os.getenv("AZURE_SEARCH_INDEX_NAME"))
        print(f"Index '{index.name}' retrieved successfully")
        return index
    except Exception as e:
        print(f"Error getting index: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Azure AI Search index")
    parser.add_argument("--action", choices=["create", "delete", "get"], required=True,
                       help="Action to perform on the index")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_index()
    elif args.action == "delete":
        delete_index()
    elif args.action == "get":
        get_index() 