# LOCAL Insurance Document Analysis System
A **fully functional, production-ready** AI-powered insurance document analysis system that proactively identifies concerns, exclusions, and important clauses in insurance policies with interactive exploration and contextual chat capabilities.

Basically - Insurance documents can be overwhelming and confusing, this AI makes it super easy to understand what you're signing up for

![confused-about-insurance](https://github.com/user-attachments/assets/3efea597-196c-4bc0-be6d-593fb6cf2670)

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

![automation-win](https://github.com/user-attachments/assets/6108e08a-6cf3-4bee-9788-b8f068e591b0)

---

## **Project Structure**

No more messy document folders - everything is organized and analyzed automatically!

![organized-files](https://github.com/user-attachments/assets/a3198d78-7712-4bb0-981b-4d84beb228ad)

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

---

## **Technology Stack**

### **Backend**

- **FastAPI**: Modern Python web framework with async support
- **PyMuPDF (fitz)**: PDF text extraction with coordinates
- **Groq API**: Fast LLM inference (llama-3.3-70b-versatile)
- **ChromaDB**: Local vector database for embeddings
- **SQLite**: Enhanced database for findings and metadata
- **Transformers**: Local Jina embeddings for semantic search
- **Loguru**: Enhanced logging with pretty output

![galaxy-brain-ai](https://github.com/user-attachments/assets/77d75e93-fca5-42d6-b571-c057ba799572)

### **Frontend**

- **React**: Modern UI library with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first styling
- **Shadcn/ui**: High-quality component library
- **Zustand**: Lightweight state management
- **React Router**: Client-side routing
- **React PDF**: Native PDF rendering

---

## **Getting Started**

### **Prerequisites**

- Python 3.8+
- Node.js 18+
- Groq API key (get from [groq.com](https://groq.com))

### **Installation**

#### **Backend Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Raykarr/AI-Insurance-Document-Analyzer-Local
   cd AI-Insurance-Document-Analyzer-Local
   ```

2. **Set up Python environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

#### **Frontend Setup**

1. **Navigate to frontend:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

### **Running the Application**

1. **Start the backend server:**
   ```bash
   cd backend
   python app.py
   ```
   Backend will run on `http://localhost:8000`

![its-working](https://github.com/user-attachments/assets/df50e66f-abb6-48cb-a193-48a010afd8e3)

2. **Start the frontend development server:**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Access the application:**
   Open your browser and navigate to `http://localhost:5173`

---

## **How It Works**

### **Analysis Pipeline**

1. **Document Upload**
   - User uploads insurance policy PDF
   - System validates and stores document
   - Generates unique document ID

2. **Text Extraction**
   - PyMuPDF extracts text with page and coordinate information
   - Text is stored in SQLite database
   - Location data preserved for precise tracking

3. **Chunking**
   - Document split into semantic chunks
   - Chunks stored in ChromaDB with embeddings
   - Local Jina embeddings used (no external API)

4. **AI Analysis**
   - Groq API analyzes chunks for concerns
   - 10 categories of analysis:
     * Coverage Limitations
     * Exclusions
     * Claim Requirements
     * Premium & Payment Terms
     * Cancellation Terms
     * Coverage Periods
     * Beneficiary Rules
     * Liability Limits
     * Deductibles
     * Special Conditions
   - Severity and confidence scores assigned

5. **Findings Storage**
   - Findings deduplicated and stored
   - Categories, severity, and metadata preserved
   - Real-time progress updates sent to frontend

6. **Interactive Exploration**
   - Users can filter findings by category
   - Click findings to view details
   - Ask questions about specific findings
   - Chat history preserved per finding

---

## **API Documentation**

FastAPI provides automatic interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### **Key Endpoints**

- `POST /upload`: Upload insurance document
- `GET /document/{doc_id}/status`: Get analysis status
- `GET /document/{doc_id}/findings`: Get all findings
- `POST /chat`: Chat about specific finding

---

## **Architecture**

Detailed architecture documentation available in:
- [ARCHITECTURE.md](ARCHITECTURE.md): System architecture and design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md): Project summary and features
- [implementation_plan.md](implementation_plan.md): Implementation details

---

## **Troubleshooting**

### **Common Issues**

#### **Backend Won't Start**
   - Check Python version (3.8+ required)
   - Verify all dependencies installed
   - Ensure GROQ_API_KEY is set
   - Check port 8000 is available

#### **Frontend Won't Start**
   - Check Node.js version (18+ required)
   - Run `npm install` again
   - Clear `node_modules` and reinstall
   - Check port 5173 is available

#### **Analysis Fails**
   - Verify GROQ_API_KEY is valid
   - Check PDF is not corrupted
   - Ensure sufficient disk space
   - Check backend logs for errors

#### **Database Issues**
   - System auto-creates databases
   - Check file permissions
   - Ensure sufficient disk space

### **Performance Issues**

- Large PDFs may require more RAM
- Consider chunking very large documents
- Monitor ChromaDB performance
- Use SSD storage for better I/O

---

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

---

## **Security**

### Implemented Security Features 

- File validation (PDF type checking)
- Input sanitization
- CORS configuration
- API key management
- Error handling and recovery
- 
### Production Considerations 

- Use production ASGI server (Gunicorn + Uvicorn)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Set up monitoring and logging
- Database backups

---

## **Key Features Status**

### **Fully Implemented & Working**

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

### **Performance Optimizations**

- **Background Processing**: Async analysis tasks
- **Caching Strategy**: Database caching for text and chunks
- **Deduplication**: Prevents duplicate findings
- **Timeout Handling**: 120-second upload timeout
- **Memory Management**: Efficient chunking and processing
