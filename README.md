# TaxGPT

An AI-powered tax assistant built on a microservices Hybrid GraphRAG architecture. TaxGPT ingests tax documents such as PDFs, spreadsheets, and slides, then uses a combination of vector and graph-based retrieval to deliver accurate, context-aware answers to tax-related questions.

## Architecture Overview

TaxGPT is composed of four containerized services that communicate over an internal Docker network.

**API Gateway** - A FastAPI service that acts as the entry point for all client requests. It forwards queries to the orchestrator and returns responses to the user.

**Orchestration Service** - The core intelligence layer powered by LangGraph. It performs stateful routing to decide whether a query needs vector retrieval, graph retrieval, or both, and then synthesizes a final answer using Claude Opus 4.

**Worker Service (Ingestion)** - A background worker that processes raw tax documents including IRS Form 1040 PDFs, IRC publications, PowerPoint slides, and CSV data. It chunks, embeds, and stores the processed data into the vector and graph databases.

**Databases** - ChromaDB serves as the vector database for semantic similarity search. Neo4j Aura serves as the graph database for structured relationship queries across tax entities. Together they enable the Hybrid GraphRAG retrieval strategy.

## Tech Stack

- Python and FastAPI for the API gateway
- LangGraph for orchestration and stateful agent routing
- Claude Opus 4 as the primary language model
- ChromaDB for vector storage and retrieval
- Neo4j Aura for graph storage and relationship queries
- Docker and Docker Compose for containerization

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine
- An Anthropic API key for Claude
- An OpenAI API key for embeddings
- A Neo4j Aura instance with connection credentials

### Environment Setup

Create a `.env` file in the project root with the following variables

```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
NEO4J_URI=neo4j+s://your_aura_instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### Running the Application

Step 1 - Start the core services (API Gateway, Orchestrator, and ChromaDB)

```bash
docker compose up -d --build
```

Step 2 - Run the ingestion worker to process and load documents into the databases. This is a one-time job that extracts data from the source files, embeds text into ChromaDB, and inserts structured records into Neo4j.

```bash
docker compose --profile worker up ingestion
```

Step 3 - Send a query to the API

```bash
curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d "{\"query\": \"What is the standard deduction for 2024?\"}"
```

### Service Ports

| Service       | Port |
|---------------|------|
| API Gateway   | 8000 |
| ChromaDB      | 8001 |
| Orchestrator  | 8002 |

## Project Structure

```
TaxGPT
  api               API Gateway service (FastAPI)
  orchestrator       Orchestration service (LangGraph)
  ingestion          Document ingestion worker
  docker-compose.yml Multi-container configuration
  .env               Environment variables (not committed)
```

## License

This project is proprietary. All rights reserved.
