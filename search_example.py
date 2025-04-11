from search_client import AzureSearchClient
import json

def print_results(results, title):
    print(f"\n=== {title} ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    # Initialize the search client
    client = AzureSearchClient()
    
    # Example 1: Simple semantic search
    print("\n1. Simple Semantic Search")
    semantic_results = client.search(
        search_text="What are the main business requirements for the project?",
        query_type="semantic",
        select=["content", "metadata/section_title", "metadata/document_type"],
        top=3
    )
    print_results(semantic_results, "Semantic Search Results")
    
    # Example 2: Semantic search with filter
    print("\n2. Semantic Search with Filter")
    filtered_semantic = client.search(
        search_text="Explain the technical requirements for the system",
        query_type="semantic",
        filter="metadata/document_type eq 'BRD'",
        select=["content", "metadata/section_title", "metadata/document_type"],
        top=3
    )
    print_results(filtered_semantic, "Filtered Semantic Search Results")
    
    # Example 3: Regular search with semantic ranking
    print("\n3. Regular Search with Semantic Ranking")
    ranked_results = client.search(
        search_text="system requirements",
        query_type="semantic",
        select=["content", "metadata/section_title", "metadata/document_type"],
        top=3
    )
    print_results(ranked_results, "Semantically Ranked Results")

if __name__ == "__main__":
    main() 