# Data Loader for Azure AI Search

This project is a data loader utility designed to process and index documents into Azure AI Search. It uses Azure OpenAI for embeddings (text-embeddings-3-large) and provides functionality to manage and search through indexed documents.

## Features

- Document processing and chunking
- Metadata extraction from documents
- Integration with Azure Cognitive Search
- Azure OpenAI embeddings generation
- Search functionality with semantic capabilities

## Prerequisites

- Python 3.8 or higher
- Azure Cognitive Search service
- Azure OpenAI service

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd data-loader
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env-example` and fill in your Azure credentials:
```bash
cp .env-example .env
```

## Configuration

The following environment variables need to be set in your `.env` file:

- `AZURE_SEARCH_SERVICE_NAME`: Your Azure Cognitive Search service name
- `AZURE_SEARCH_INDEX_NAME`: The name of your search index
- `AZURE_SEARCH_API_KEY`: Your Azure Cognitive Search API key
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your Azure OpenAI deployment name

## Usage

### Create Index (brd_index)

To create or delete index , use the index_manager script:

```bash
python index_manager.py --action create (delete)
```

### Indexing Documents

To index documents, use the main script:

```bash
python main.py
```

### Searching Documents

To search through indexed documents, use the search example:

```bash
python search_example.py
```

## Project Structure

- `main.py`: Main script for document processing and indexing
- `index_manager.py`: Manages Azure Cognitive Search index operations
- `search_client.py`: Client for interacting with Azure Cognitive Search
- `search_example.py`: Example script demonstrating search functionality
- `data/`: Directory for storing documents to be processed

## Dependencies

The project uses several key Python packages:
- Azure Search Documents SDK
- Azure OpenAI
- LangChain
- Python-dotenv

See `requirements.txt` for the complete list of dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 