# Insurance Document Analysis System - Mermaid Architecture Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        A[Index Page]
        B[Analysis Page]
        C[PDF Viewer]
        D[Chat Panel]
        E[UI Components]
    end
    
    subgraph "Backend (FastAPI + Python)"
        F[Ingest Endpoint]
        G[Analysis Engine]
        H[LLM Integration]
        I[Vector Store]
        J[Background Tasks]
    end
    
    subgraph "Data Layer"
        K[SQLite Database]
        L[ChromaDB]
        M[File Storage]
    end
    
    subgraph "External Services"
        N[Groq API]
        O[Jina Embeddings]
    end
    
    subgraph "Document Processing"
        P[PyMuPDF]
        Q[Text Extraction]
        R[Chunking]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    
    F --> G
    G --> H
    G --> I
    G --> J
    
    F --> K
    F --> M
    G --> K
    I --> L
    
    H --> N
    I --> O
    
    F --> P
    P --> Q
    Q --> R
    R --> G
    
    B --> F
    D --> H
    C --> M
```

## 2. Data Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant P as Processor
    participant AI as AI Engine
    participant DB as Database
    participant VS as Vector Store
    participant S as Storage
    
    Note over U,S: Document Upload & Processing
    U->>F: Upload PDF
    F->>B: POST /ingest
    activate B
    B->>S: Save PDF file
    B->>P: Extract text with coordinates
    P->>DB: Cache text blocks
    B->>P: Create semantic chunks
    P->>VS: Store embeddings
    B->>AI: Start background analysis
    deactivate B
    B->>F: Return document ID
    F->>U: Show processing status
    
    Note over U,S: Background Analysis
    AI->>DB: Get cached text blocks
    AI->>AI: Analyze chunks for concerns
    AI->>DB: Save findings
    AI->>DB: Update analysis status
    
    Note over U,S: Real-time Progress
    loop Every 2 seconds
        F->>B: GET /progress/{id}
        B->>DB: Get analysis status
        B->>F: Return progress
    end
    
    Note over U,S: Results Display
    F->>B: GET /findings/{id}
    B->>DB: Query findings
    B->>F: Return findings list
    F->>U: Display findings
    
    Note over U,S: PDF Viewing
    U->>F: Select finding
    F->>B: GET /documents/{id}/pdf
    B->>S: Retrieve PDF
    B->>F: Return PDF
    F->>U: Display PDF
    
    Note over U,S: Chat Interaction
    U->>F: Ask question
    F->>B: POST /findings/{id}/chat
    B->>DB: Get finding context
    B->>AI: Generate response
    AI->>B: Return answer
    B->>F: Return chat response
    F->>U: Display answer
```

## 3. Processing Pipeline Flowchart

```mermaid
flowchart TD
    A[User uploads PDF] --> B[Frontend sends to /ingest]
    B --> C[Backend receives file]
    C --> D[Generate document hash]
    D --> E[Save PDF to file system]
    E --> F[Extract text with coordinates]
    F --> G[Cache text blocks in database]
    G --> H[Create semantic chunks]
    H --> I[Setup vector store]
    I --> J[Store document embeddings]
    J --> K[Start background analysis task]
    K --> L[Update status to 'analyzing']
    
    L --> M{Process chunks}
    M --> N[Send to Groq LLM]
    N --> O[Analyze for concerns]
    O --> P[Save findings to database]
    P --> Q{More chunks?}
    Q -->|Yes| M
    Q -->|No| R[Analysis complete]
    
    L --> S[Frontend polls progress]
    S --> T[Update UI with status]
    T --> S
    
    R --> U[Update status to 'completed']
    U --> V[Frontend fetches findings]
    V --> W[Display results to user]
    W --> X[User can view PDF]
    X --> Y[User can chat about findings]
```

## 4. Database Schema

```mermaid
erDiagram
    documents {
        TEXT id PK
        TEXT filename
        TIMESTAMP upload_date
        INTEGER total_pages
        TEXT analysis_status
        TIMESTAMP analysis_completed_at
    }
    
    findings {
        INTEGER id PK
        TEXT document_id FK
        INTEGER page_num
        TEXT coordinates
        TEXT text_content
        TEXT category
        TEXT severity
        TEXT summary
        TEXT recommendation
        REAL confidence_score
        TIMESTAMP created_at
    }
    
    cache {
        TEXT key PK
        TEXT value
        TIMESTAMP created_at
    }
    
    documents ||--o{ findings : "has"
    documents ||--o{ cache : "caches"
```

## 5. AI Analysis Flow

```mermaid
flowchart TD
    A[Get cached text blocks] --> B[Create semantic chunks]
    B --> C[For each chunk]
    C --> D[Prepare analysis prompt]
    D --> E[Send to Groq LLM]
    E --> F[Parse JSON response]
    F --> G[Validate concern fields]
    G --> H{is_concern?}
    H -->|Yes| I[Calculate confidence score]
    I --> J[Save finding to database]
    H -->|No| K[Skip chunk]
    J --> L[Next chunk]
    K --> L
    L --> M{More chunks?}
    M -->|Yes| C
    M -->|No| N[Analysis complete]
```

## 6. Frontend State Management

```mermaid
graph LR
    subgraph "File State"
        A[File Selection]
        B[Upload Progress]
        C[Auto Upload]
    end
    
    subgraph "Analysis State"
        D[Document ID]
        E[Analysis Status]
        F[Findings List]
        G[Selected Finding]
    end
    
    subgraph "UI State"
        H[Current Page]
        I[Category Filter]
        J[Pagination]
        K[Loading States]
    end
    
    subgraph "Chat State"
        L[Chat History]
        M[Current Context]
        N[Input State]
    end
    
    A --> B
    B --> D
    D --> E
    E --> F
    F --> G
    
    G --> M
    M --> L
    L --> N
    
    H --> I
    I --> J
    J --> K
```

## 7. Error Handling Flow

```mermaid
flowchart TD
    A[User uploads document] --> B{File validation?}
    B -->|Failed| C[Show error message]
    C --> D[Allow retry]
    D --> E[Stop]
    
    B -->|Passed| F[Send to backend]
    F --> G{Backend connection?}
    G -->|Failed| H[Show connection error]
    H --> I[Retry mechanism]
    I --> E
    
    G -->|Success| J{File processing?}
    J -->|Failed| K[Show processing error]
    K --> L[Log error details]
    L --> M[Allow new upload]
    M --> E
    
    J -->|Success| N{AI analysis?}
    N -->|Failed| O[Mark as failed]
    O --> P[Show failure message]
    P --> Q[Allow retry]
    Q --> E
    
    N -->|Success| R[Success]
    R --> S[Display results]
    S --> T{PDF loading?}
    T -->|Failed| U[Show fallback options]
    U --> V[Download link]
    V --> W[View in new tab]
    T -->|Success| X[Complete]
```

## 8. Component Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        subgraph "Pages"
            A1[Index.tsx]
            A2[Analysis.tsx]
            A3[NotFound.tsx]
        end
        
        subgraph "Components"
            B1[PDFViewer.tsx]
            B2[ChatPanel.tsx]
            B3[UI Components]
        end
        
        subgraph "State Management"
            C1[React Query]
            C2[useState/useEffect]
            C3[File State]
        end
        
        subgraph "API Layer"
            D1[api.ts]
            D2[Axios]
        end
    end
    
    subgraph "Backend Layer"
        subgraph "API Endpoints"
            E1[POST /ingest]
            E2[GET /analysis/{id}]
            E3[GET /findings/{id}]
            E4[POST /findings/{id}/chat]
            E5[GET /progress/{id}]
            E6[GET /documents/{id}/pdf]
            E7[GET /health]
        end
        
        subgraph "Core Services"
            F1[Document Processing]
            F2[Text Extraction]
            F3[Chunking Engine]
            F4[Analysis Engine]
            F5[Vector Store]
        end
        
        subgraph "AI Services"
            G1[Groq LLM]
            G2[Jina Embeddings]
            G3[Concern Detection]
        end
        
        subgraph "Background Tasks"
            H1[Analysis Task]
            H2[Progress Tracking]
        end
    end
    
    subgraph "Data Layer"
        subgraph "Databases"
            I1[SQLite]
            I2[ChromaDB]
        end
        
        subgraph "Storage"
            J1[File System]
            J2[Cache]
        end
    end
    
    subgraph "External Services"
        K1[Groq API]
        K2[Jina AI]
    end
    
    A1 --> A2
    A2 --> B1
    A2 --> B2
    A2 --> B3
    A2 --> C1
    C1 --> D1
    D1 --> D2
    
    E1 --> F1
    F1 --> F2
    F2 --> F3
    F3 --> F4
    F4 --> G3
    F4 --> F5
    
    G3 --> G1
    F5 --> G2
    G1 --> K1
    G2 --> K2
    
    H1 --> F4
    H2 --> H1
    
    E1 --> I1
    E1 --> J1
    F4 --> I1
    F5 --> I2
    F1 --> J2
    
    D2 --> E1
    D2 --> E2
    D2 --> E3
    D2 --> E4
    D2 --> E5
    D2 --> E6
```

## 9. Security & Performance

```mermaid
graph LR
    subgraph "Security"
        A1[CORS Configuration]
        A2[File Validation]
        A3[Input Sanitization]
        A4[API Key Management]
    end
    
    subgraph "Performance"
        B1[Background Processing]
        B2[Caching Strategy]
        B3[Database Optimization]
        B4[Vector Store Indexing]
    end
    
    subgraph "Scalability"
        C1[Async Processing]
        C2[Database Connections]
        C3[File Storage]
        C4[Memory Management]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> A4
    
    B1 --> B2
    B2 --> B3
    B3 --> B4
    
    C1 --> C2
    C2 --> C3
    C3 --> C4
```

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Client Browser"
        A[React App]
    end
    
    subgraph "Frontend Hosting"
        B[Vite Dev Server]
        C[Static Files]
    end
    
    subgraph "Backend Server"
        D[FastAPI App]
        E[Uvicorn Server]
    end
    
    subgraph "Data Storage"
        F[SQLite Database]
        G[ChromaDB]
        H[File System]
    end
    
    subgraph "External APIs"
        I[Groq API]
        J[Jina AI]
    end
    
    A --> B
    B --> C
    A --> D
    D --> E
    E --> F
    E --> G
    E --> H
    D --> I
    D --> J
```

## Key Technical Features Summary

### Frontend Stack
- **React 18** with TypeScript
- **Vite** for development
- **React Query** for state management
- **Tailwind CSS** for styling
- **Shadcn/ui** components
- **React Router** for navigation

### Backend Stack
- **FastAPI** for API
- **PyMuPDF** for PDF processing
- **Groq API** for LLM (llama-3.3-70b-versatile)
- **Jina Embeddings** for semantic search
- **ChromaDB** for vector storage
- **SQLite** for metadata
- **Background tasks** for async processing

### AI/ML Features
- **Semantic chunking** with location preservation
- **Concern detection** across 10 categories
- **Confidence scoring** for findings
- **Contextual chat** about specific findings
- **Deduplication** of similar findings

### Data Flow
1. **Upload** → PDF saved, text extracted with coordinates
2. **Processing** → Chunks created, embeddings generated
3. **Analysis** → AI analyzes each chunk for concerns
4. **Storage** → Findings saved with metadata
5. **Display** → Results shown with interactive features
6. **Chat** → Contextual Q&A about findings 