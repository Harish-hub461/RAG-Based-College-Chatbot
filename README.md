# RAG-Based College Information Assistant

An intelligent, full-stack college information web application powered by **Retrieval-Augmented Generation (RAG)**. 

Unlike traditional chatbots that may generate unsupported answers, this assistant searches official college documents (PDF, DOCX, TXT), retrieves relevant chunks using dense vector embeddings, and synthesizes accurate answers strictly grounded in retrieved context with **verifiable source citations**.

---

## 1. Project Overview

Students often face difficulties locating scattered information regarding admissions, course fee structures, hostel curfews, exam rules, library hours, scholarships, and campus placements across fragmented notices and PDFs.

This application provides a **centralized AI assistant** that:
- Allows administrators to upload and manage official college policy documents.
- Extracts, cleans, and chunks document text into semantic vector embeddings.
- Stores embeddings in a persistent Vector Database (ChromaDB).
- Answers student questions using semantic vector similarity search.
- Displays verified source citations (Document Name, Category, Page Number, and Confidence Match %).
- Safely handles unknown questions by refusing to invent or hallucinate answers when information is not present in official documents.

---

## 2. Features

### Student Features
- **Student Authentication**: Register, log in, and secure session management via JWT.
- **RAG Chat Workspace**: Modern interactive chat interface with suggested query pills.
- **Source Citation Cards**: Clickable reference cards displaying Document Name, Category, Page #, Confidence Score, and retrieved text snippets.
- **Category Filtering**: Filter questions by department/topic (Admissions, Hostel, Fees, Exams, Scholarships, Placements).
- **Conversation History**: Save, list, resume, and delete past chat sessions.
- **Answer Feedback System**: Thumbs up / thumbs down feedback modal with optional comment logging.
- **User Profile**: View account status, role authorization, and join date.

### Administrator Features
- **Admin Dashboard**: Real-time KPI metrics (Total Documents, Vector Chunks, Active Conversations, Total Questions, Unanswered Query Count).
- **Document Management**: Upload PDF, DOCX, or TXT documents with Title, Category, and Version controls.
- **Document Processing Pipeline**: Real-time status tracking (`pending`, `processing`, `completed`, `error`).
- **Reprocessing & Deletion**: Trigger document re-indexing or delete documents along with relational chunks and vector embeddings.
- **Analytics & User Overview**: View frequently asked student questions and registered user accounts.

### RAG Pipeline Features
- **Text Extraction**: Automatic extraction from PDF (`pypdf`), DOCX (`python-docx`), and TXT files.
- **Semantic Overlapping Chunking**: Smart paragraph & sentence chunking preserving page numbers and section metadata.
- **Dense Embedding Generation**: High-performance 384-dimensional vector embeddings (`sentence-transformers` / feature-hashing vectorizer).
- **Vector Database**: Cosine similarity retrieval with metadata filtering (ChromaDB / Persistent Vector Engine).
- **Grounded Response Generation**: LLM synthesis (Google Gemini API / OpenAI API / Grounded Local Synthesizer) with non-hallucination unknown query reporting.

---

## 3. Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Modern, fast RESTful API web framework.
- **SQLAlchemy & SQLite**: Relational database engine and models.
- **PyJWT & Passlib**: Secure JWT token authentication and bcrypt password hashing.
- **PyPDF & python-docx**: Document text extraction.
- **ChromaDB / NumPy**: Vector database indexing and similarity search.
- **Sentence-Transformers / Scikit-Learn**: Vector embeddings.

### Frontend
- **React 18 & Vite**: Ultra-fast single-page web application.
- **Tailwind CSS**: Modern glassmorphic aesthetic design system with dark ambient mode.
- **Lucide React**: Iconography.
- **React Router DOM v6**: Protected client-side routing.
- **Axios**: HTTP API client with JWT interceptors.

---

## 4. Architecture & RAG Pipeline

```text
                     ┌──────────────────┐
                     │     Student      │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  React Frontend  │
                     └────────┬─────────┘
                              │ REST API (JWT)
                              ▼
                     ┌──────────────────┐
                     │  FastAPI Server  │
                     │  Auth + Chat API │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   RAG Pipeline   │
                     └────────┬─────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
      ┌─────────────────┐           ┌─────────────────┐
      │ Vector Database │           │ Relational DB   │
      │ (ChromaDB)      │           │ (SQLite)        │
      │ Embeddings      │           │ Users, Chats,   │
      │ Document Chunks │           │ Documents       │
      └─────────────────┘           └─────────────────┘
               │
               ▼
      ┌─────────────────┐
      │ College Context │
      │ Retrieved Chunks│
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │       LLM       │
      │ (Gemini/OpenAI) │
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │ Answer + Sources│
      └─────────────────┘
```

### Complete RAG Workflow:
1. **Document Upload**: Admin uploads document (`.pdf`, `.docx`, `.txt`).
2. **Text Extraction & Cleaning**: Extracted page by page, removing null bytes and normalizing whitespace.
3. **Chunking**: Text divided into ~500-character chunks with 100-character overlaps and page metadata.
4. **Vector Embedding**: Converted into 384-dimensional dense vectors.
5. **Vector DB Storage**: Indexed in ChromaDB with metadata (document_id, title, category, page_number).
6. **Query Embedding**: Student question converted to dense query vector.
7. **Similarity Search**: Cosine similarity top-K search filters chunks passing similarity threshold (`0.30`).
8. **Context Injection**: Top chunks formatted into grounded prompt.
9. **LLM Synthesis**: Generates accurate answer based *only* on context.
10. **Source Attribution**: Returns response + clickable source cards. If score < threshold, returns standard unknown notice.

---

## 5. Prerequisites

Before installing, ensure you have the following installed on your machine:

- **Node.js**: `v18.0.0` or higher (Tested on `v22.13.1`)
- **npm**: `v9.0.0` or higher
- **Python**: `3.8` or higher
- **Git**

---

## 6. Environment Setup

### Root Directory Setup
Create `.env` in project root:
```bash
cp .env.example .env
```

### Backend `.env` (`backend/.env`)
```ini
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=dev-secret-key-rag-college-chatbot-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_EMAIL=admin@college.edu
ADMIN_PASSWORD=AdminPassword123!
ADMIN_NAME=System Administrator

# Optional: Add your Google Gemini API key or OpenAI API key
GEMINI_API_KEY=
OPENAI_API_KEY=
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash

SIMILARITY_THRESHOLD=0.30
TOP_K_CHUNKS=4
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

### Frontend `.env` (`frontend/.env`)
```ini
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 7. Database Setup

The backend automatically creates and initializes SQLite relational tables (`users`, `documents`, `document_chunks`, `conversations`, `messages`, `feedback`) and seeds the default administrator account upon first launch.

Default Seeded Admin Credentials:
- **Email**: `admin@college.edu`
- **Password**: `AdminPassword123!`

---

## 8. Backend Setup

1. Open terminal and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run automated RAG pipeline verification test:
```bash
python test_rag.py
```

5. Start backend Uvicorn server:
```bash
uvicorn app.main:app --reload --port 8000
```
Backend API server will run at `http://localhost:8000`. API Swagger documentation available at `http://localhost:8000/docs`.

---

## 9. Frontend Setup

1. Open a new terminal tab and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start Vite development server:
```bash
npm run dev -- --port 3000
```
Frontend Web App will run at `http://localhost:3000`.

---

## 10. Run the Complete Application

Start servers in the following order:

1. **Backend**: `uvicorn app.main:app --reload --port 8000` (runs on `http://localhost:8000`)
2. **Frontend**: `npm run dev -- --port 3000` (runs on `http://localhost:3000`)

Access `http://localhost:3000` in your web browser.

---

## 11. Test the RAG Pipeline (Step-by-Step)

Follow these steps to test the complete application end-to-end:

### Step 1: Admin Login & Document Upload
1. Go to `http://localhost:3000/login`.
2. Click **"Fill Admin Credentials"** (`admin@college.edu` / `AdminPassword123!`) and click **Sign In**.
3. You will be redirected to the **Admin Control Center**.
4. Navigate to **Documents** in the top navigation.
5. In the **Upload & Index New Document** form:
   - **Title**: `CSE Admissions Bulletin 2026`
   - **Category**: `Admissions`
   - **File**: Choose sample document `sample_docs/CSE_Admissions_and_Fees_2026.txt` (or `sample_docs/Hostel_and_Campus_Rules_2026.txt`).
6. Click **Upload Document**.
7. Observe status change to `completed` and chunk counts generated in the table.

### Step 2: Student Registration & Question Answering
1. Log out of Admin account.
2. Click **Get Started** or navigate to `http://localhost:3000/register`.
3. Create a student account (e.g. `alex@college.edu`).
4. Navigate to **Chatbot**.
5. Ask a supported question:
   > *"What is the tuition fee for CSE?"*
6. **Verify Output**:
   - The AI responds with exact fee amounts ($2,500 per semester).
   - Clickable **Source Citation Cards** appear displaying `CSE Admissions Bulletin 2026`, Category `Admissions`, Page `1`, Match % Confidence score, and text snippet.

### Step 3: Test Non-Hallucination Safe Fallback
1. Ask an unsupported question:
   > *"What is the secret recipe for chocolate cake?"*
2. **Verify Output**:
   - The AI responds: *"I couldn't find reliable information about this in the available college documents. Please contact the relevant department or try asking in a different way."*
   - Zero hallucinated information.

---

## 12. API Documentation

### Authentication Endpoints

#### 1. User Registration
- **Method**: `POST`
- **URL**: `/api/auth/register`
- **Request Body**:
```json
{
  "name": "Alex Morgan",
  "email": "alex@college.edu",
  "password": "Password123!",
  "role": "student"
}
```
- **Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "Alex Morgan",
    "email": "alex@college.edu",
    "role": "student",
    "created_at": "2026-08-23T12:00:00"
  }
}
```

#### 2. User Login
- **Method**: `POST`
- **URL**: `/api/auth/login`
- **Request Body**:
```json
{
  "email": "admin@college.edu",
  "password": "AdminPassword123!"
}
```

### Chat & RAG Endpoints

#### 3. Ask RAG Question
- **Method**: `POST`
- **URL**: `/api/chat/ask`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "conversation_id": null,
  "question": "What are the hostel fees?",
  "category_filter": "Hostel"
}
```
- **Response** (`200 OK`):
```json
{
  "id": 14,
  "conversation_id": 3,
  "sender": "ai",
  "message_text": "Based on the official college documents, hostel fees are...",
  "sources": [
    {
      "document_id": 2,
      "document_title": "Hostel Residence Policies 2026",
      "file_name": "Hostel_and_Campus_Rules_2026.txt",
      "category": "Hostel",
      "page_number": 1,
      "similarity_score": 0.842,
      "snippet": "Single Occupancy (A/C Room): $1,200 USD per semester..."
    }
  ],
  "is_unanswered": false,
  "created_at": "2026-08-23T12:05:00"
}
```

#### 4. Chat History
- **Method**: `GET`
- **URL**: `/api/chat/history`
- **Headers**: `Authorization: Bearer <token>`

### Document Management Endpoints

#### 5. Upload Document
- **Method**: `POST`
- **URL**: `/api/documents/upload`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Form Data**: `title`, `category`, `version`, `file`

---

## 13. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`ModuleNotFoundError` on backend startup** | Virtual environment not activated or packages missing | Run `source venv/bin/activate` (or `.\venv\Scripts\activate`) and `pip install -r requirements.txt`. |
| **`MISSING_EXPORT` or Vite Build Error** | Node module version mismatch | Run `npm install` inside `frontend/` directory. |
| **CORS Error in browser console** | Backend port mismatch | Ensure FastAPI has CORS enabled and frontend `.env` points to `http://localhost:8000/api`. |
| **Document upload returns 403 Forbidden** | Upload attempted with student account | Log in with Admin credentials (`admin@college.edu`). |
| **Query returns "I couldn't find reliable information..."** | Document not uploaded or similarity threshold too strict | Upload sample documents in Admin panel or adjust `SIMILARITY_THRESHOLD` in `backend/.env`. |

---

## 14. Project Structure

```text
Rag project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin.py          # Admin analytics & user management APIs
│   │   │   ├── auth.py           # Registration, login, profile APIs
│   │   │   ├── chat.py           # Ask question, history, conversation APIs
│   │   │   └── documents.py      # Admin document upload & status APIs
│   │   ├── core/
│   │   │   ├── config.py         # Application settings & environment loader
│   │   │   ├── database.py       # SQLAlchemy engine & session manager
│   │   │   └── security.py       # JWT token generation & password hashing
│   │   ├── db/
│   │   │   └── models.py         # Relational database ORM schemas
│   │   ├── rag/
│   │   │   ├── chunker.py        # Text cleaning & semantic overlap chunker
│   │   │   ├── embedder.py       # Dense vector embedding generator
│   │   │   ├── extractor.py      # PDF, DOCX, TXT text extraction
│   │   │   ├── pipeline.py       # Complete RAG query & grounding orchestrator
│   │   │   └── vector_db.py      # ChromaDB & vector index manager
│   │   ├── schemas/
│   │   │   └── schemas.py        # Pydantic request/response validation
│   │   └── main.py               # FastAPI application entrypoint
│   ├── uploads/                  # Uploaded policy documents directory
│   ├── chroma_db/                # Persistent vector database directory
│   ├── test_rag.py               # Automated end-to-end RAG verification test
│   ├── requirements.txt          # Python dependencies manifest
│   ├── .env                      # Backend environment configuration
│   └── .env.example              # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FeedbackModal.jsx # User feedback popup
│   │   │   ├── Navbar.jsx        # Navigation header & role indicator
│   │   │   ├── Sidebar.jsx       # Chat history sidebar navigation
│   │   │   └── SourceCard.jsx    # Verified source reference card
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # Client authentication state manager
│   │   ├── pages/
│   │   │   ├── AdminDashboard.jsx# Metrics KPIs, recent uploads, top queries
│   │   │   ├── AdminDocuments.jsx# Document upload & status tracking page
│   │   │   ├── AdminUsers.jsx    # Registered user management
│   │   │   ├── ChatPage.jsx      # Interactive RAG Chat workspace
│   │   │   ├── HistoryPage.jsx   # Conversation history list
│   │   │   ├── LandingPage.jsx   # Hero marketing & pipeline visual
│   │   │   ├── LoginPage.jsx     # Login with demo shortcuts
│   │   │   ├── ProfilePage.jsx   # User profile details
│   │   │   └── RegisterPage.jsx  # Student & admin registration
│   │   ├── services/
│   │   │   └── api.js            # Axios client with JWT interceptor
│   │   ├── App.jsx               # Router & Protected route configuration
│   │   ├── index.css             # Glassmorphism theme & design system
│   │   └── main.jsx              # React entry point
│   ├── package.json              # Frontend package manifest
│   ├── vite.config.js            # Vite configuration
│   ├── .env                      # Frontend environment configuration
│   └── .env.example              # Frontend environment template
├── sample_docs/                  # Sample PDFs & TXTs for Admissions, Hostel, Fees, Scholarships
├── .env.example                  # Root environment template
└── README.md                     # Complete project documentation
```

---

## 15. Security Notes

- **Never Commit Secrets**: Never commit actual `.env` files or private API keys to version control. Use `.env.example` templates for public repositories.
- **Change Default Admin Password**: Change default admin credentials (`AdminPassword123!`) before deploying to production.
- **JWT Secret**: Update `SECRET_KEY` in production with a strong 256-bit random key (`openssl rand -hex 32`).
- **Input Validation & Sanitization**: File uploads are validated against allowed extension formats (`pdf`, `docx`, `txt`).

---

## License

Distributed under the MIT License. See `LICENSE` for details.
