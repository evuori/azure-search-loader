from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
import re
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration is now loaded from environment variables
os.environ["OPENAI_API_VERSION"] = "2023-07-01-preview"  # This is still hardcoded as it's a constant

def extract_metadata(text_chunk):
    """Extract metadata from a chunk of text from the BRD document."""
    metadata = {}
    
    # Extract Project Name and Feature Name with improved patterns
    project_match = re.search(r'\*\*Project Name:\*\*\s*(.+?)(?:\n|$)', text_chunk)
    if project_match:
        metadata['project_name'] = project_match.group(1).strip()
    
    feature_match = re.search(r'\*\*Feature Name:\*\*\s*(.+?)(?:\n|$)', text_chunk)
    if feature_match:
        metadata['feature_name'] = feature_match.group(1).strip()
    
    # Extract section number and title with improved pattern
    section_match = re.search(r'^#{1,3}\s*(?:(\d+(?:\.\d+)*)\s+)?(.+)$', text_chunk, re.MULTILINE)
    if section_match:
        if section_match.group(1):  # If there's a section number
            metadata['section_number'] = section_match.group(1)
        metadata['section_title'] = section_match.group(2).strip()
    
    # Extract requirement IDs with improved pattern
    req_ids = re.findall(r'\|?\s*((?:BR|FR|NFR)-[A-Z]+-\d+)\s*\|?', text_chunk)
    if req_ids:
        metadata['requirement_ids'] = list(set(req_ids))  # Remove duplicates
    
    # Determine document part with improved logic
    if re.search(r'Executive\s+Summary', text_chunk, re.IGNORECASE):
        metadata['document_part'] = 'executive_summary'
    elif re.search(r'Business\s+Requirements', text_chunk, re.IGNORECASE) or re.search(r'BR-[A-Z]+-\d+', text_chunk):
        metadata['document_part'] = 'business_requirements'
    elif re.search(r'Functional\s+Requirements', text_chunk, re.IGNORECASE) or re.search(r'FR-[A-Z]+-\d+', text_chunk):
        metadata['document_part'] = 'functional_requirements'
    elif re.search(r'Non-Functional\s+Requirements', text_chunk, re.IGNORECASE) or re.search(r'NFR-[A-Z]+-\d+', text_chunk):
        metadata['document_part'] = 'non_functional_requirements'
    elif re.search(r'Technical\s+Constraints', text_chunk, re.IGNORECASE):
        metadata['document_part'] = 'technical_constraints'
    elif re.search(r'Stakeholders', text_chunk, re.IGNORECASE):
        metadata['document_part'] = 'stakeholders'
    elif re.search(r'Project\s+Overview', text_chunk, re.IGNORECASE):
        metadata['document_part'] = 'project_overview'
    
    # Add document type
    metadata['document_type'] = 'Business Requirements Document'
    
    return metadata

def clean_markdown(text):
    """Remove Markdown formatting from text while preserving the content."""
    # Remove headers but preserve their text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold and italic markers but keep the text
    text = re.sub(r'\*\*|\*|__|_', '', text)
    
    # Remove links but keep the link text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove images but keep the alt text
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    
    # Remove inline code markers but keep the code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove blockquotes but keep the content
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Preserve table content but remove formatting
    text = re.sub(r'\|', ' ', text)  # Replace pipe with space
    text = re.sub(r'\|-+\|', '', text)  # Remove table header separators
    
    # Remove list markers but preserve the content
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace but preserve paragraph breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

# Load the BRD document
with open('data/brd-example-001.md', 'r') as file:
    brd_text = file.read()

# Configure the text splitter - optimized for markdown structure
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,            # Increased chunk size to preserve more context
    chunk_overlap=400,          # Increased overlap to maintain better context between chunks
    length_function=len,        # Function that measures chunk size
    separators=[                # Separators in order of priority
        "\n## ",               # Split first on H2 headers
        "\n### ",              # Then on H3 headers
        "\n#### ",             # Then on H4 headers
        "\n\n",                # Then on paragraphs
        ". ",                  # Then on sentences
        "\n",                  # Then on line breaks
        ", ",                  # Then on clauses
        " ",                   # Then on words
        ""                     # Finally on characters
    ],
    keep_separator=True        # Keep the separators to maintain document structure
)

# Split the text and add metadata
chunks = text_splitter.create_documents([brd_text])

# Enhance chunks with metadata
project_name = None
feature_name = None

# First pass to find project and feature names
for chunk in chunks:
    chunk_metadata = extract_metadata(chunk.page_content)
    if 'project_name' in chunk_metadata:
        project_name = chunk_metadata['project_name']
    if 'feature_name' in chunk_metadata:
        feature_name = chunk_metadata['feature_name']
    if project_name and feature_name:
        break

# Second pass to add all metadata
for i, chunk in enumerate(chunks):
    # Extract metadata from the chunk text
    chunk_metadata = extract_metadata(chunk.page_content)
    
    # Add positional metadata
    chunk_metadata['chunk_id'] = i
    chunk_metadata['total_chunks'] = len(chunks)
    
    # Add document-level metadata
    chunk_metadata['document_type'] = 'Business Requirements Document'
    
    # Add project and feature names if found
    if project_name and 'project_name' not in chunk_metadata:
        chunk_metadata['project_name'] = project_name
    if feature_name and 'feature_name' not in chunk_metadata:
        chunk_metadata['feature_name'] = feature_name
    
    # Update the chunk's metadata
    chunk.metadata.update(chunk_metadata)

# Initialize Azure OpenAI embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    openai_api_version="2023-07-01-preview",
    chunk_size=16
)

# Create Azure AI Search client
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

# Convert chunks to Azure AI Search documents
search_documents = []
for i, chunk in enumerate(chunks):
    # Clean the content of Markdown formatting
    clean_content = clean_markdown(chunk.page_content)
    
    # Get the embedding for the chunk
    embedding = embeddings.embed_query(clean_content)
    
    # Create the search document
    search_doc = {
        "id": str(i),
        "content": clean_content,
        "embedding": embedding,
        "metadata": chunk.metadata
    }
    search_documents.append(search_doc)

# Upload documents to Azure AI Search
search_client.upload_documents(search_documents)

print(f"Successfully uploaded {len(search_documents)} documents to Azure AI Search")