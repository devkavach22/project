<div align="center">
  <h1>🚀 SpaceFix CAF Parser API</h1>
  <p><strong>Intelligent Telecom Customer Acquisition Form (CAF) Data Extraction</strong></p>
</div>

---

## 📖 Overview

SpaceFix CAF Parser is a FastAPI-based backend service designed to intelligently process and extract structured data from Telecom Customer Acquisition Forms (CAF) in PDF format. Built with **Langchain**, **OpenAI**, and **Pydantic**, it automates the tedious process of reading scanned or digital CAFs and converts them into standardized JSON data, complete with extracted images.

## ✨ Features

- **Document Parsing:** Extracts raw text and embedded images from uploaded PDF files using `pypdf`.
- **Intelligent Data Extraction:** Utilizes state-of-the-art LLMs via `Langchain` to parse unstructured text into highly structured and reliable JSON.
- **Strict Validation:** Guarantees data structure and typing using `Pydantic` schemas.
- **RESTful API:** Provides a clean and well-documented `/upload` endpoint for seamless frontend integration.
- **Docker Ready:** Includes a `Dockerfile` and `compose.yaml` for containerized deployment.
- **Cross-Origin Resource Sharing (CORS):** Configured to allow requests from remote frontends (e.g., localhost:3000).

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **LLM Orchestration:** [Langchain](https://python.langchain.com/)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **PDF Processing:** [pypdf](https://pypdf.readthedocs.io/)
- **Environment Management:** `uv` (Fast & modern Python package installer) / `dotenv`

## 🚀 Getting Started

### Prerequisites

- Python >= 3.14
- `uv` (Recommended) or `pip`
- Docker & Docker Compose (optional, for containerized run)
- **OpenAI / OpenRouter API Key** (or Ollama for local models depending on `llm/base.py` configuration)

### 1. Clone the project and install dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd project

# Install dependencies using uv
uv sync
```

### 2. Set up Environment Variables

Create a `.env` file in the root directory and add the necessary environment variables for your LLM provider. Example for OpenRouter:

```ini
OPENAI_API_KEY=your_openai_or_openrouter_api_key
OPENROUTER_MODEL=your_preferred_model # e.g., openai/gpt-4o-mini
OPENAI_API_BASE=https://openrouter.ai/api/v1 # If using OpenRouter
```

### 3. Run the Development Server

Start the FastAPI server locally:

```bash
uv run fastapi dev main.py
```
The API will be available at `http://localhost:8000`. 
Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## 🐳 Docker Setup

To run the application inside a Docker container:

```bash
# Build and run with Docker Compose
docker compose up --build
```

## 📡 API Reference

### Upload a CAF PDF

**Endpoint:** `POST /upload`  
**Content-Type:** `multipart/form-data`

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | `file` | Yes | The PDF file to be parsed |

**Response (Success 200 OK):**
```json
{
  "status": "success",
  "filename": "caf_document.pdf",
  "extracted_text": {
    "status": "",
    "filename": "",
    "caf_no": "12345678",
    "service_type": "Prepaid",
    "customer_name": "Ravina Akashkumar Soni",
    "local_address": {
      "house_no": "Flat 101",
      "street_address": "Shree Apartment, Satellite",
      "city": "Ahmedabad",
      "state": "Gujarat",
      "pincode": "380015",
      ...
    },
    ...
  },
  "images_count": 1,
  "images_preview": ["<base64_encoded_string>"]
}
```

## 📂 Project Structure

```
├── app/                  # Application core modules
├── chain/                # Langchain pipelines (e.g., pdf_parser_chain.py)
├── llm/                  # Base LLM configurations (e.g., base.py)
├── schemas/              # Pydantic schemas (SpaceFix_Schema.py)
├── Dockerfile            # Docker image configuration
├── compose.yaml          # Docker Compose configuration
├── main.py               # FastAPI entry point
├── pyproject.toml        # Project dependencies & metadata
└── README.md             # Project documentation (this file)
```

---
<p align="center">Built with ❤️ for rapid and accurate telecom data processing.</p>