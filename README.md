# LOCAL Insurance Document Analysis System

A **fully functional, production-ready** AI-powered insurance document analysis system that proactively identifies concerns, exclusions, and important clauses in insurance policies with interactive exploration and contextual chat capabilities.

## **Project Overview**

This system transforms insurance document analysis from a **reactive Q&A experience** into a **proactive, interactive discovery platform** that automatically scans policies, identifies key concerns, and provides real-time processing with contextual chat.

### **Key Features**

- **Proactive Analysis**: AI automatically scans documents for concerns across 10 categories
- **Real-time Processing**: Live progress tracking with detailed step information
- **Location-Aware Processing**: Text extraction with coordinates for precise tracking
- **Structured Findings**: Categorized concerns with severity and confidence scores
- **Interactive Exploration**: Click findings to view details and chat
- **Contextual Chat**: Ask questions about specific findings with preserved history
- **Modern UI**: Beautiful, responsive interface with real-time feedback

## **Project Structure**

```
insurance-document-analyzer/
├── backend/                 
│   ├── app.py              
│   ├── requirements.txt    
│   ├── insurance_analysis.db 
│   ├── chroma_db/         
│   └── uploads/           
├── frontend/               
│   ├── src/
│   │   ├── pages/         
│   │   │   ├── Index.tsx  
│   │   │   └── Analysis.tsx 
│   │   ├── components/    
│   │   │   ├── PDFViewer.tsx 
│   │   │   └── ChatPanel.tsx 
│   │   ├── lib/           
│   │   │   ├── api.ts     
│   │   │   └── state.ts   
│   │   └── components/ui/ 
│   ├── package.json       
│   └── vite.config.ts    
├── ARCHITECTURE.md        
├── PROJECT_SUMMARY.md     
├── implementation_plan.md  
└── README.md
```

## **Technology Stack**

### **Backend**
- **FastAPI**: Modern Python web framework with async support
- **PyMuPDF (fitz)**: PDF text extraction with coordinates
- **Groq API**: Fast LLM inference (llama-3.3-70b-versatile)
- **ChromaDB**: Local vector database for embeddings
- **SQLite**: Enhanced database for findings and metadata
- **Transformers**: Local Jina embeddings for semantic search
- **Loguru**: Enhanced logging with pretty output
- **Pydantic**: Data validation and serialization

### **Frontend**
- **React 18**: Modern React with hooks
- **TypeScript**: Type safety throughout
- **Vite**: Fast development and building
- **React Query**: Server state management
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Beautiful component library
- **Axios**: HTTP client for API calls

## **Quick Start**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- Groq API key

### **1. Clone the Repository**
```bash
git clone https://github.com/Raykarr/AI-Insurance-Document-Analyzer
cd insurance-document-analyzer
```

### **2. Backend Setup**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key_here"

# Run the server
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### **3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### **4. Access the Application**
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## **System Architecture**

### **Complete Architecture Documentation**
- **`DIAGRAMS FOLDER`** - Mermaid diagrams for GitHub/Notion compatibility

### **Data Flow**
1. **Document Upload** → PDF processing with coordinates
2. **Text Extraction** → Location-aware text blocks
3. **Chunking** → Semantic chunks with coordinates
4. **AI Analysis** → Proactive concern detection
5. **Storage** → Structured findings in database
6. **Frontend** → Interactive exploration and chat

### **Key Components**
- **Enhanced Database**: SQLite with findings and cache
- **Analysis Engine**: Groq LLM with specialized prompts
- **Vector Storage**: ChromaDB for semantic search
- **Interactive UI**: React with real-time progress

## **API Endpoints**

### **Core Endpoints**
- `POST /ingest` - Upload and analyze document
- `GET /analysis/{document_id}` - Get analysis status
- `GET /findings/{document_id}` - Get all findings (deduplicated)
- `POST /findings/{finding_id}/chat` - Contextual chat
- `GET /documents/{document_id}/pdf` - Serve PDF file
- `GET /progress/{document_id}` - Real-time progress

### **Utility Endpoints**
- `GET /health` - Health check with system status
- `GET /docs` - Interactive API documentation
- `GET /test/chunking` - Test chunking functionality

## **User Experience**

### **1. Document Upload & Processing**
- Select PDF on home page
- Auto-redirects to analysis page
- Real-time progress tracking with detailed steps:
  - File validation
  - Text extraction with coordinates
  - Embedding generation
  - Vector store setup
  - AI analysis processing
- Background concern detection
- Results display with findings

### **2. Findings Discovery**
- Categorized concern display with deduplication
- Category filters (All, EXCLUSION, LIMITATION, etc.)
- Pagination (10 items per page)
- Severity-based color coding
- Confidence scoring
- Page-specific navigation

### **3. Interactive Exploration**
- Click finding to select and view details
- PDF viewer displays document with native browser rendering
- Contextual chat panel with finding context
- Ask specific questions about the finding
- Get precise, context-aware answers
- Chat history preserved across finding selections

## **Development**

### **Backend Development**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app:app --reload

# Check code quality
flake8 app.py
```

### **Frontend Development**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check
```

## **Testing**

### **Manual Testing**
1. **Upload a PDF**: Test document upload and processing
2. **Check Analysis**: Verify background analysis completion
3. **Browse Findings**: Test filtering and categorization
4. **Interactive Features**: Test finding selection and chat
5. **Contextual Chat**: Test finding-specific questions

### **API Testing**
```bash
# Upload document
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.pdf"

# Check status
curl "http://localhost:8000/analysis/{document_id}"

# Get findings
curl "http://localhost:8000/findings/{document_id}"

# Check progress
curl "http://localhost:8000/progress/{document_id}"
```

## **Troubleshooting**

### **Common Issues**

1. **"GROQ_API_KEY not set"**
   ```bash
   # Check environment variable
   echo $GROQ_API_KEY  # Mac/Linux
   echo %GROQ_API_KEY% # Windows
   ```

2. **Import errors**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   npm install
   ```

3. **Port conflicts**
   ```bash
   # Use different ports
   uvicorn app:app --port 8001  # Backend
   npm run dev -- -p 8081       # Frontend
   ```

4. **Database errors**
   - System auto-creates databases
   - Check file permissions
   - Ensure sufficient disk space

### **Performance Issues**
- Large PDFs may require more RAM
- Consider chunking very large documents
- Monitor ChromaDB performance
- Use SSD storage for better I/O

## **Performance Metrics**

### **Target Performance**
- Document analysis time < 30 seconds
- Finding accuracy > 95%
- API response time < 200ms
- PDF rendering < 2 seconds
- Real-time progress updates every 2 seconds

### **Optimization Features**
- Background processing for analysis
- Database caching for text and chunks
- Deduplication of findings
- Memory-efficient chunking
- 120-second upload timeout

## **Security**

### **Implemented Security Features **
- File validation (PDF type checking)
- Input sanitization
- CORS configuration
- API key management
- Error handling and recovery

### **Production Considerations **
- Use production ASGI server (Gunicorn + Uvicorn)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Set up monitoring and logging
- Database backups

## **Key Features Status**

### ** Fully Implemented & Working **
- **Document Upload**: Drag & drop with auto-upload
- **Text Extraction**: Location-aware with coordinates
- **AI Analysis**: Proactive concern detection
- **Real-time Progress**: Live status updates every 2 seconds
- **Findings Display**: Categorized with filtering and pagination
- **PDF Viewer**: Native browser rendering
- **Contextual Chat**: Finding-specific Q&A with history
- **Error Handling**: Comprehensive error recovery
- **Database**: SQLite with findings and cache
- **Vector Store**: ChromaDB for semantic search
- **API Documentation**: Complete FastAPI docs
- **Architecture Documentation**: PlantUML and Mermaid diagrams

### ** Performance Optimizations **
- **Background Processing**: Async analysis tasks
- **Caching Strategy**: Database caching for text and chunks
- **Deduplication**: Prevents duplicate findings
- **Timeout Handling**: 120-second upload timeout
- **Memory Management**: Efficient chunking and processing
