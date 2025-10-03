# LOCAL Insurance Document Analysis System

<div align="center">

![Insurance Policy Confusion](https://i.imgflip.com/1qfxa4.jpg)

*"Me trying to understand my insurance policy... Send help!" 🤯*

</div>

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

<div align="center">

![No More Manual Work](https://i.redd.it/ah-yes-the-programmer-move-v0-8sgu3ay49va61.jpg?width=640)

*"When AI finally handles all your boring insurance paperwork" 🎉*

</div>

## **Project Structure**

<div align="center">

![Organized vs Messy](https://i.redd.it/organized-version-of-messy-v0-pefxhvvqxdq01.jpg?width=500)

*"Before AI: Messy docs everywhere. After AI: Perfectly organized insights!" 📁✨*

</div>

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

<div align="center">

![Galaxy Brain AI](https://imgflip.com/s/meme/Expanding-Brain.jpg)

*"Using advanced AI to analyze insurance documents = GALAXY BRAIN" 🧠✨*

</div>

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
- **TailwindCSS**: Utility-first styling
- **shadcn/ui**: Beautiful component library

## **Getting Started**

### **Prerequisites**

- Python 3.10+
- Node.js 18+
- Groq API key ([Get one here](https://console.groq.com))

### **Installation**

#### **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### **Frontend Setup**

```bash
cd frontend
npm install
```

### **Configuration**

Create a `.env` file in the backend directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### **Running the Application**

#### **Start Backend**

```bash
cd backend
uvicorn app:app --reload
```

Backend will run on `http://localhost:8000`

#### **Start Frontend**

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

## **Usage**

<div align="center">

![I Finally Understand](https://i.redd.it/insurance-101-v0-0g1kqr2gvcge1.png?width=500)

*"When you finally understand your coverage thanks to AI analysis!" 💡🎯*

</div>

1. **Upload Document**: Navigate to the home page and upload your insurance policy PDF
2. **Wait for Analysis**: The system will:
   - Extract text from your PDF
   - Create semantic embeddings
   - Analyze for concerns across 10 categories
   - Store findings in the database
3. **Explore Findings**: View categorized concerns with:
   - Severity indicators (Critical, High, Medium, Low)
   - Confidence scores
   - Relevant document excerpts
4. **Interactive Chat**: Click on any finding to:
   - Get detailed explanations
   - Ask follow-up questions
   - Explore related clauses

## **Key Features Explained**

### **Proactive Analysis Categories**

The system automatically scans for:

1. **Exclusions**: What's NOT covered
2. **Coverage Limitations**: Caps, limits, and restrictions
3. **Pre-existing Conditions**: Health-related limitations
4. **Deductibles & Co-payments**: Out-of-pocket costs
5. **Waiting Periods**: Time before coverage begins
6. **Policy Cancellation**: Termination clauses
7. **Claim Procedures**: How to file claims
8. **Premium Changes**: Rate adjustment terms
9. **Grace Periods**: Payment flexibility
10. **Renewal Terms**: Policy continuation conditions

### **Real-time Processing**

Watch the magic happen:
- Progress indicators for each step
- Live status updates
- Estimated completion time
- Detailed step information

### **Contextual Chat**

Powered by Groq's lightning-fast LLM:
- Semantic search through your document
- RAG (Retrieval Augmented Generation)
- Chat history preserved per finding
- Context-aware responses

## **Architecture Highlights**

### **Database Schema**

- **Documents Table**: Stores PDF metadata and processing status
- **Findings Table**: Structured concern data with categories
- **Chat History**: Preserves conversations per finding

### **Vector Store**

- ChromaDB for semantic search
- Jina embeddings (local model)
- Efficient document chunking

### **API Design**

- RESTful endpoints
- WebSocket support (planned)
- Comprehensive error handling
- Request validation with Pydantic

## **Development**

### **Project Philosophy**

- **Local-first**: Runs entirely on your machine
- **Privacy-focused**: Your documents never leave your system
- **Production-ready**: Robust error handling and logging
- **Modern stack**: Latest best practices

### **Code Quality**

- Type hints throughout Python code
- TypeScript for frontend safety
- Comprehensive logging
- Clear separation of concerns

## **Roadmap**

- [ ] Multi-document comparison
- [ ] Export findings to PDF/Excel
- [ ] Policy recommendation engine
- [ ] Mobile-responsive UI improvements
- [ ] WebSocket for real-time updates
- [ ] Document versioning
- [ ] Advanced search filters

## **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## **Acknowledgments**

- Groq for lightning-fast LLM inference
- ChromaDB for elegant vector storage
- The amazing open-source community

---

<div align="center">

**Built with ❤️ for making insurance documents actually readable**

*Because nobody should need a law degree to understand their coverage* 📄✨

</div>
