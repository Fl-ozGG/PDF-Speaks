# 🚀 TurboLauncher: RAG Document Intelligence

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-000000?style=for-the-badge&logo=pinecone)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

**TurboLauncher** is an intelligent search and question-answering engine built on **RAG (Retrieval-Augmented Generation)**. It allows users to upload PDF files, process them to extract knowledge, and query them in natural language, returning precise, contextually relevant answers strictly based on their personal documents.

## 📖 API Documentation

You can explore and test the API endpoints using our official Postman documentation:

[![Postman Documentation](https://img.shields.io/badge/Postman-Documentation-FF6C37?style=for-the-badge&logo=postman&logoColor=white)](https://documenter.getpostman.com/view/40133516/2sBXVfiArJ)

Alternatively, click the link below:
[View Postman Documentation](https://documenter.getpostman.com/view/40133516/2sBXVfiArJ)

---

## 🐳 Deployment with Docker Compose (Recommended)

The fastest and most robust way to run the project is using **Docker**. This ensures all dependencies (Python, PDF libraries, security components) are automatically configured in an isolated environment.

### 1. Requirements
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* A `.env` file at the project root containing your credentials.

## ⚠️ Important Note for Windows Users (Database Setup)

When running this project on Windows via Docker Desktop, Docker might mistakenly create a **directory** instead of a **file** when mapping volumes that don't exist yet. This will cause the application to crash with an `OperationalError`.

**Please follow these steps before running Docker for the first time:**

1.  Navigate to the project's root directory.
2.  **Manually create an empty file** named `iachatbot.db`. (You can do this by creating a new text file and renaming it, making sure it has no `.txt` extension).
3.  Ensure there is no folder with that same name.
4.  The application will automatically initialize the database schema inside this file once it starts.

### 3. Startup Commands
From a terminal in the project directory:

```bash
docker compose up -d --build

docker ps

docker logs -f turbolauncher-app
```

--

## ✨ Key Features

- 🔐 **Advanced Security**: OAuth2 authentication with JWT tokens and password hashing via Bcrypt.
- 📄 **PDF Processing**: Automated text extraction and cleanup of special characters.
- 🧠 **Next-Generation Embeddings**: Uses OpenAI’s `text-embedding-3-small` model with 1024 dimensions for strong semantic representation.
- ⚡ **Vector Search**: Storage and indexing in Pinecone for millisecond-level retrieval.
- 🤖 **GPT-4o Integration**: Answer generation using OpenAI’s latest model, strictly constrained to the provided context.
- 👤 **Multi-user Privacy**: Metadata-based filters ensure users can only access their own documents.

---

## 🛠️ Tech Stack

| Tool | Purpose |
| :--- | :--- |
| **FastAPI** | Core framework for building the REST API. |
| **OpenAI API** | Embedding generation and GPT-4o responses. |
| **Pinecone** | Vector database for chunk storage and retrieval. |
| **SQLite** | Persistent storage for user accounts and credentials. |
| **LangChain** | Intelligent text splitting (RecursiveCharacterTextSplitter). |
| **Jose/JWT** | Secure token signing and validation. |

---

## 🏗️ Workflow (Architecture)

1. **Register/Login**: The user authenticates to obtain an access token.
2. **PDF Upload**: A file is uploaded and split into overlapping chunks to preserve context.
3. **Vectorization**: Each chunk is converted into a numerical vector using the OpenAI API.
4. **Indexing**: Vectors are stored in Pinecone along with metadata (user ID, page, filename).
5. **RAG Query**: On a query, the system retrieves the 5 most similar chunks from Pinecone and sends them to GPT-4o as context to generate the answer.

---

## 📂 Code Structure

- `main.py`: Application orchestrator and route (endpoint) definitions.
- `auth.py`: Security logic, token creation, and validation.
- `pdf_processing.py`: Document extraction, cleanup, and chunking utilities.
- `db_pinecone.py`: Connector and client for the vector database.
- `database.py`: Local SQLite database management.
- `openai_utils.py`: Helper functions for interacting with OpenAI models.

---

## 🚀 Initial Setup

### Environment Variables

Create a `.env` file at the project root with the following keys:

```env
OPENAI_API_KEY="sk-..."
PINECONE_API_KEY="your_pinecone_api_key"
