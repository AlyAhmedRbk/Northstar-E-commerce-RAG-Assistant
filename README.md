# Northstar — E-commerce RAG Assistant

An AI-powered e-commerce assistant built with **Retrieval-Augmented Generation (RAG)**. Northstar allows customers to ask natural-language questions about products, pricing, availability, warranties, and store policies using information stored in a predefined knowledge base.

The application combines semantic search, vector embeddings, ChromaDB, and a Large Language Model (LLM) to generate relevant, context-aware responses.

## Overview

Northstar is designed to demonstrate how RAG technology can be integrated into a modern e-commerce application.

Instead of relying entirely on an LLM's pretrained knowledge, the chatbot retrieves relevant information from indexed business documents before generating an answer.

The system is designed to:

- Answer questions using indexed product and business documents.
- Retrieve relevant information through semantic similarity search.
- Support multiple document formats.
- Generate natural-language responses using an LLM.
- Avoid inventing information when relevant knowledge is unavailable.
- Provide a modern e-commerce storefront with an integrated AI assistant.
- Support both light and dark themes.

## Features

### AI-Powered Customer Assistant

- Natural-language product questions.
- Product price and availability inquiries.
- Warranty and return-policy questions.
- Context-aware responses using retrieved documents.
- Knowledge-grounded answer generation.
- Responses in simple, customer-friendly language.

### Document Processing

Supported document formats:

- PDF
- DOCX
- TXT
- CSV
- XLSX

The ingestion pipeline extracts document content, cleans the text, identifies document structure, splits content into manageable chunks, and prepares it for vector indexing.

### Retrieval-Augmented Generation

The RAG pipeline consists of:

1. User submits a question.
2. The application validates the question.
3. ChromaDB performs semantic similarity search.
4. Relevant document chunks are retrieved.
5. Retrieval results are checked against a similarity threshold.
6. Retrieved context is passed to the LLM.
7. The LLM generates a response grounded in the supplied context.
8. The chatbot displays the answer.

### Modern E-commerce Interface

- Northstar storefront.
- Product catalogue.
- Product search and category filtering.
- Responsive layout.
- Light and dark mode.
- Floating AI chatbot interface.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| LLM Integration | FastRouter API |
| LLM Client | OpenAI Python SDK |
| Vector Database | ChromaDB |
| Embeddings | ChromaDB default ONNX MiniLM |
| PDF Processing | PyPDF |
| Word Documents | python-docx |
| Excel Processing | openpyxl |
| Text Tokenization | tiktoken |
| Configuration | python-dotenv |
| Testing | pytest |

## Architecture

```text
                  CUSTOMER
                      |
                      v
             NORTHSTAR STOREFRONT
                      |
                      v
                CHAT INTERFACE
                      |
                      v
                FLASK BACKEND
                      |
                      v
                RAG SERVICE
                      |
             +--------+--------+
             |                 |
             v                 v
       QUERY VALIDATION   CHROMADB
                               |
                               v
                      SEMANTIC RETRIEVAL
                               |
                               v
                       RELEVANT CHUNKS
                               |
                               v
                       CONTEXT BUILDER
                               |
                               v
                       FASTROUTER API
                               |
                               v
                       LLM GENERATION
                               |
                               v
                      CUSTOMER RESPONSE
```

### Document Ingestion Architecture

```text
       KNOWLEDGE DOCUMENTS
                |
                v
         DOCUMENT EXTRACTOR
                |
                v
           TEXT CLEANING
                |
                v
        STRUCTURE EXTRACTION
                |
                v
           TEXT CHUNKING
                |
                v
         METADATA GENERATION
                |
                v
          CHUNK VALIDATION
                |
                v
          VECTOR INDEXING
                |
                v
             CHROMADB
```

## Project Structure

```text
ecommerce-rag-assistant/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── ingestion/
│   │   ├── extractors.py
│   │   ├── text_cleaner.py
│   │   ├── structure_parser.py
│   │   ├── chunker.py
│   │   ├── metadata_builder.py
│   │   ├── chunk_validator.py
│   │   └── indexer.py
│   │
│   ├── retrieval/
│   │   ├── vector_store.py
│   │   └── retriever.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   └── rag_service.py
│   │
│   ├── routes/
│   │   ├── health.py
│   │   └── chat.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── chat.js
│
├── data/
│   ├── knowledge/
│   ├── uploads/
│   └── chroma/
│
├── scripts/
│   └── index_knowledge.py
│
├── tests/
│
├── .env
├── .gitignore
├── pyproject.toml
├── run.py
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-rag-assistant.git

cd ecommerce-rag-assistant
```

Replace `YOUR_USERNAME` with your GitHub username and repository details.

### 2. Create a Virtual Environment

Using Python:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 3. Install Dependencies

If using the project's UV configuration:

```bash
pip install uv

uv sync
```

Alternatively, install the project dependencies using the package manager configured in your `pyproject.toml`.

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Configure the FastRouter credentials and application settings using the environment variable names expected by `app/config.py`.

Typical configuration values include:

```env
APP_ENV=development
DEBUG=True

SECRET_KEY=replace-with-a-secure-secret

FASTROUTER_API_KEY=your_api_key
FASTROUTER_BASE_URL=https://api.fastrouter.ai/api/v1
FASTROUTER_MODEL=openai/gpt-oss-20b:free
```

**Important:** Never commit your `.env` file or expose API keys in public repositories.

The variable names above should match your application's actual configuration.

## Knowledge Base Setup

Northstar uses predefined documents stored in:

```text
data/knowledge/
```

Place your business documents inside this directory.

Example:

```text
data/knowledge/
│
├── products/
│   ├── laptops.pdf
│   ├── accessories.pdf
│   └── smartphones.pdf
│
├── policies/
│   ├── return_policy.pdf
│   └── shipping_policy.pdf
│
└── faq/
    └── customer_faq.docx
```

The example structure is illustrative. Add documents containing accurate business information before indexing.

## Indexing Documents

Northstar includes an internal indexing script.

Run:

```bash
python scripts/index_knowledge.py
```

The indexing process:

1. Scans the knowledge directory.
2. Identifies supported document formats.
3. Extracts document content.
4. Cleans and structures extracted text.
5. Splits content into chunks.
6. Generates document metadata and hashes.
7. Adds indexed chunks to ChromaDB.

Existing indexed data is persisted in:

```text
data/chroma/
```

The application checks document hashes to avoid unnecessarily indexing duplicate documents.

Re-run the indexing script whenever you add or update knowledge documents.

## Running the Application

Start the Flask development server:

```bash
python run.py
```

Open the application:

**http://127.0.0.1:5000**

The application runs locally on port `5000`.

## API Endpoints

### Health Check

```http
GET /api/health
```

Checks whether the application is running.

### Readiness Check

```http
GET /api/ready
```

Checks application readiness.

### Chat Endpoint

```http
POST /api/chat/
```

Example request:

```json
{
  "question": "What is the price of the HP EliteBook Laptop?"
}
```

The endpoint processes the question through the RAG pipeline and returns a response.

Example response shape:

```json
{
  "status": "success",
  "answer": "The HP EliteBook Laptop is priced at $850 USD."
}
```

The exact response fields depend on the current backend implementation.

## Configuration

Some important application settings are managed through `app/config.py`.

| Setting | Description |
|---|---|
| `CHUNK_SIZE` | Maximum target chunk size |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks |
| `TOP_K` | Number of retrieval results |
| `SIMILARITY_THRESHOLD` | Minimum similarity required |
| `LLM_TIMEOUT` | LLM request timeout |
| `LLM_MAX_RETRIES` | Maximum retry attempts |
| `MAX_QUESTION_LENGTH` | Maximum customer question length |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name |

Current ingestion configuration:

- Chunk size: 450 tokens
- Chunk overlap: 75 tokens
- Retrieval top-k: 5
- Similarity threshold: 0.30 (provisional; requires evaluation against real queries)

## Testing

Run the test suite:

```bash
pytest -v
```

For coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Tests cover application functionality, document processing, ingestion, retrieval, and chatbot behavior.

## Important Design Decisions

### Why RAG?

A conventional LLM chatbot can generate answers using information that is unrelated to a company's actual products or policies.

RAG addresses this by retrieving relevant business information before answer generation.

### Why ChromaDB?

ChromaDB provides persistent local vector storage and semantic similarity search, making it suitable for this development project.

### Why Document Chunking?

Large documents are divided into smaller sections so that retrieval can identify relevant information without passing entire documents to the LLM.

### Why Similarity Thresholding?

Not every retrieved result is relevant. A similarity threshold helps filter weak matches and reduces the risk of generating unsupported answers.

The threshold must be evaluated using representative questions and retrieval results before production use.

## Security and Limitations

- Customer-facing users do not receive document upload or indexing permissions.
- Knowledge documents are managed internally.
- API credentials must remain in environment variables.
- The LLM must not be treated as a source of verified business facts.
- Responses depend on the quality and completeness of indexed documents.
- Free-tier LLM providers may enforce request and daily usage limits.
- The current Flask development server is intended for local development, not production deployment.
- Production deployment requires a production WSGI server, HTTPS, rate limiting, request-size controls, monitoring, and appropriate vector database infrastructure.

## Future Improvements

Potential development areas include:

- Expanded product and business knowledge bases.
- Better retrieval evaluation and similarity calibration.
- Hybrid search combining keyword and semantic retrieval.
- Reranking retrieved document chunks.
- Conversation memory and context management.
- Automated document update and re-indexing workflows.
- Authentication and administrative knowledge management.
- Production deployment with monitoring and observability.
- Evaluation of hallucination resistance and prompt-injection handling.

## Learning Outcomes

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation.
- Document extraction and preprocessing.
- Token-based text chunking.
- Vector embeddings.
- Persistent vector databases.
- Semantic similarity search.
- LLM API integration.
- Context construction and grounded generation.
- Flask backend development.
- AI-powered frontend integration.

## License

Choose and add an appropriate open-source license before distributing this project.

---

**Northstar — Making product knowledge accessible through AI.**