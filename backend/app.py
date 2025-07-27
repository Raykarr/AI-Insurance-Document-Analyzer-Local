import asyncio
import hashlib
import os
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import fitz 
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel
from tiktoken import get_encoding

# LangChain & ChromaDB
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Add Groq import
from groq import Groq

# Add local embeddings
from transformers import AutoModel
import torch

# Configure logger for pretty output
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ .env file loaded successfully")
except Exception as e:
    logger.warning(f"❌ Could not load .env file: {e}")

# Environment / API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Log environment variable status
logger.info(f"🔑 GROQ_API_KEY: {'✅ Set' if GROQ_API_KEY else '❌ Not set'}")

# ---------- Database Schema ----------

def init_database():
    """Initialize database with schema"""
    db = sqlite3.connect('insurance_analysis.db')
    
    # Documents table
    db.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_pages INTEGER,
            analysis_status TEXT DEFAULT 'pending',
            analysis_completed_at TIMESTAMP
        )
    ''')
    
    # Findings table
    db.execute('''
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            page_num INTEGER NOT NULL,
            coordinates TEXT NOT NULL, -- JSON: [x0, y0, x1, y1]
            text_content TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            summary TEXT NOT NULL,
            recommendation TEXT,
            confidence_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Cache table 
    db.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.commit()
    db.close()
    logger.info("✅ Database initialized with enhanced schema")

# Initialize database on startup
init_database()

def get_db():
    """Get SQLite database connection"""
    return sqlite3.connect('insurance_analysis.db')

# ---------- Concern Detection Categories ----------

CONCERN_CATEGORIES = {
    "EXCLUSION": "Services/procedures not covered",
    "LIMITATION": "Coverage caps and restrictions", 
    "WAITING_PERIOD": "Time delays before coverage",
    "DEDUCTIBLE": "Out-of-pocket costs",
    "COPAYMENT": "Fixed payment amounts",
    "COINSURANCE": "Percentage cost sharing",
    "POLICYHOLDER_DUTY": "Required actions by insured",
    "RENEWAL_RESTRICTION": "Policy renewal limitations",
    "CLAIM_PROCESS": "Complex claim requirements",
    "NETWORK_RESTRICTION": "Provider network limitations"
}

# ---------- Enhanced Text Extraction with Coordinates ----------

async def extract_text_with_coordinates(bytes_: bytes) -> List[Dict[str, Any]]:
    """
    Extract text with page numbers and coordinates for highlighting
    """
    logger.info(f"📄 Extracting text with coordinates from {len(bytes_)} bytes...")
    
    loop = asyncio.get_event_loop()
    text_blocks = await loop.run_in_executor(None, _sync_extract_with_coordinates, bytes_)
    
    logger.info(f"📄 Extracted {len(text_blocks)} text blocks with coordinates")
    return text_blocks

def _sync_extract_with_coordinates(bytes_: bytes) -> List[Dict[str, Any]]:
    """Synchronous text extraction with coordinates"""
    doc = fitz.open(stream=bytes_, filetype="pdf")
    text_blocks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text blocks with coordinates
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():  # Non-empty text
                            text_blocks.append({
                                "text": span["text"].strip(),
                                "page_num": page_num + 1,  # 1-indexed
                                "coordinates": [
                                    span["bbox"][0],  # x0
                                    span["bbox"][1],  # y0
                                    span["bbox"][2],  # x1
                                    span["bbox"][3]   # y1
                                ],
                                "font_size": span["size"],
                                "font_name": span["font"],
                                "block_id": f"page_{page_num + 1}_block_{len(text_blocks)}"
                            })
    
    doc.close()
    return text_blocks

# ---------- Enhanced Chunking with Location Awareness ----------

async def chunk_text_with_coordinates(text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create semantic chunks while preserving location information
    """
    logger.info(f"✂️ Chunking {len(text_blocks)} text blocks with coordinates...")
    
    # Group blocks by proximity and semantic similarity
    chunks = []
    current_chunk = {
        "text": "",
        "page_num": None,
        "coordinates": [],
        "block_ids": [],
        "token_count": 0
    }
    
    enc = get_encoding("cl100k_base")
    CHUNK_SIZE = 200
    CHUNK_OVERLAP = 100
    
    for block in text_blocks:
        block_tokens = enc.encode(block["text"])
        
        # Check if adding this block would exceed chunk size
        if current_chunk["token_count"] + len(block_tokens) > CHUNK_SIZE and current_chunk["text"]:
            # Save current chunk
            if len(current_chunk["text"].strip()) > 50:
                chunks.append(current_chunk.copy())
            
            # Start new chunk with overlap
            overlap_text = current_chunk["text"][-100:]  # Simple overlap
            current_chunk = {
                "text": overlap_text,
                "page_num": block["page_num"],
                "coordinates": block["coordinates"],
                "block_ids": [block["block_id"]],
                "token_count": len(enc.encode(overlap_text))
            }
        
        # Add block to current chunk
        if current_chunk["text"]:
            current_chunk["text"] += " " + block["text"]
        else:
            current_chunk["text"] = block["text"]
            current_chunk["page_num"] = block["page_num"]
        
        current_chunk["coordinates"].append(block["coordinates"])
        current_chunk["block_ids"].append(block["block_id"])
        current_chunk["token_count"] += len(block_tokens)
    
    # Add final chunk
    if current_chunk["text"] and len(current_chunk["text"].strip()) > 50:
        chunks.append(current_chunk)
    
    # Add unique IDs to chunks for serialization
    for i, chunk in enumerate(chunks):
        chunk["id"] = str(i)
        # Ensure all required fields exist
        chunk.setdefault("text", "")
        chunk.setdefault("page_num", None)
        chunk.setdefault("token_count", 0)
        chunk.setdefault("coordinates", [])
        chunk.setdefault("block_ids", [])
    
    logger.info(f"✅ Created {len(chunks)} location-aware chunks")
    if chunks:
        sample_chunk = chunks[0]
        sample_text = sample_chunk.get('text', '')
        if len(sample_text) > 100:
            sample_text = sample_text[:50] + "..." + sample_text[-50:]
        logger.debug(f"📊 [Chunking] Sample chunk: {sample_text}")
    return chunks

# ---------- Proactive Analysis Engine ----------

ANALYST_PROMPT = """
You are an expert insurance policy analyst with 20+ years of experience.
Analyze the following text for potential policyholder concerns.

FOCUS ON:
- Exclusions (what's NOT covered)
- Limitations (coverage caps/restrictions)
- Waiting periods (time delays)
- High costs (deductibles, copays)
- Policyholder obligations
- Claim process complexity

RESPONSE FORMAT (JSON only, no additional text):
{{
    "is_concern": true/false,
    "category": "EXCLUSION/LIMITATION/WAITING_PERIOD/DEDUCTIBLE/COPAYMENT/COINSURANCE/POLICYHOLDER_DUTY/RENEWAL_RESTRICTION/CLAIM_PROCESS/NETWORK_RESTRICTION",
    "severity": "HIGH/MEDIUM/LOW",
    "summary": "One-sentence summary for layperson",
    "recommendation": "Action item for policyholder"
}}

TEXT TO ANALYZE:
{text_content}

Respond with ONLY valid JSON, no other text.
"""

async def analyze_chunk_for_concerns(llm: Groq, chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze each text chunk for insurance concerns
    """
    if not llm:
        return {"is_concern": False}
    
    cache_key = f"analysis:{hashlib.sha1(chunk['text'].encode()).hexdigest()}"
    
    # Try cache first
    db = get_db()
    cursor = db.execute('SELECT value FROM cache WHERE key = ?', (cache_key,))
    result = cursor.fetchone()
    if result:
        db.close()
        return json.loads(result[0])
    
    logger.info(f"🔍 [Analysis] Analyzing chunk for concerns...")
    
    try:
        prompt = ANALYST_PROMPT.format(text_content=chunk['text'])
        messages = [{"role": "user", "content": prompt}]
        
        response = llm.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up the response text
        result_text = result_text.strip()
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        # Parse JSON response
        try:
            analysis_result = json.loads(result_text)
            
            # Validate required fields
            if not isinstance(analysis_result, dict):
                raise ValueError("Response is not a dictionary")
            
            if 'is_concern' not in analysis_result:
                analysis_result['is_concern'] = False
            
            # Cache the result
            db.execute('INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)', 
                      (cache_key, json.dumps(analysis_result)))
            db.commit()
            db.close()
            
            logger.info(f"✅ [Analysis] Found concern: {analysis_result.get('category', 'None')}")
            return analysis_result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"⚠️ [Analysis] Invalid JSON response: {result_text}")
            logger.warning(f"⚠️ [Analysis] Error: {e}")
            return {"is_concern": False}
            
    except Exception as e:
        logger.error(f"❌ [Analysis] Error: {e}")
        db.close()
        return {"is_concern": False}

# ---------- Enhanced Database Operations ----------

async def save_document_metadata(document_id: str, filename: str, total_pages: int):
    """Save document metadata"""
    db = get_db()
    db.execute('''
        INSERT OR REPLACE INTO documents (id, filename, total_pages, analysis_status)
        VALUES (?, ?, ?, ?)
    ''', (document_id, filename, total_pages, 'pending'))
    db.commit()
    db.close()

async def save_finding(document_id: str, finding: Dict[str, Any], chunk: Dict[str, Any]):
    """Save a finding to the database"""
    db = get_db()
    
    # Calculate confidence score
    confidence = calculate_finding_confidence(finding, chunk)
    
    db.execute('''
        INSERT INTO findings 
        (document_id, page_num, coordinates, text_content, category, severity, summary, recommendation, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        document_id,
        chunk['page_num'],
        json.dumps(chunk['coordinates']),
        chunk['text'],
        finding['category'],
        finding['severity'],
        finding['summary'],
        finding.get('recommendation', ''),
        confidence
    ))
    db.commit()
    db.close()

def calculate_finding_confidence(finding: Dict[str, Any], chunk: Dict[str, Any]) -> float:
    """Calculate confidence score for a finding"""
    confidence = 0.5  # Base confidence
    
    # Text clarity
    if len(chunk['text']) > 100:
        confidence += 0.1
    
    # Legal terms presence
    legal_terms = ['excluded', 'not covered', 'limitation', 'deductible', 'copayment', 'waiting period']
    term_count = sum(1 for term in legal_terms if term.lower() in chunk['text'].lower())
    confidence += min(term_count * 0.1, 0.3)
    
    # Severity boost
    if finding.get('severity') == 'HIGH':
        confidence += 0.1
    
    return min(confidence, 1.0)

async def update_analysis_status(document_id: str, status: str):
    """Update document analysis status"""
    db = get_db()
    if status == 'completed':
        db.execute('''
            UPDATE documents 
            SET analysis_status = ?, analysis_completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, document_id))
    else:
        db.execute('''
            UPDATE documents 
            SET analysis_status = ?
            WHERE id = ?
        ''', (status, document_id))
    db.commit()
    db.close()

# ---------- Background Analysis Task ----------

async def analyze_document_background(document_id: str):
    """Background task to analyze document for concerns"""
    logger.info(f"🔄 [Background] Starting analysis for document: {document_id}")
    
    try:
        await update_analysis_status(document_id, 'analyzing')
        
        # Get document text from cache
        db = get_db()
        cursor = db.execute('SELECT value FROM cache WHERE key = ?', (f"text:{document_id}",))
        result = cursor.fetchone()
        db.close()
        
        if not result:
            logger.error(f"❌ [Background] Document text not found: {document_id}")
            await update_analysis_status(document_id, 'failed')
            return
        
        # Get text blocks from cache
        text = result[0]
        
        # Get text blocks from cache
        db = get_db()
        cursor = db.execute('SELECT value FROM cache WHERE key = ?', (f"blocks:{document_id}",))
        blocks_result = cursor.fetchone()
        db.close()
        
        if not blocks_result:
            logger.error(f"❌ [Background] Document blocks not found: {document_id}")
            await update_analysis_status(document_id, 'failed')
            return
        
        text_blocks = json.loads(blocks_result[0])
        chunks = await chunk_text_with_coordinates(text_blocks)
        
        # Get LLM
        llm = get_llm()
        if not llm:
            logger.error(f"❌ [Background] LLM not available")
            await update_analysis_status(document_id, 'failed')
            return
        
        # Analyze each chunk
        findings_count = 0
        for chunk in chunks:
            finding = await analyze_chunk_for_concerns(llm, chunk)
            if finding.get('is_concern', False):
                # Create a mock chunk with page info for now
                mock_chunk = {
                    'text': chunk['text'],
                    'page_num': 1,  # Default page
                    'coordinates': [0, 0, 100, 100]  # Default coordinates
                }
                await save_finding(document_id, finding, mock_chunk)
                findings_count += 1
        
        logger.info(f"✅ [Background] Analysis completed. Found {findings_count} concerns")
        await update_analysis_status(document_id, 'completed')
        
    except Exception as e:
        logger.error(f"❌ [Background] Analysis failed: {e}")
        await update_analysis_status(document_id, 'failed')

# ---------- Core Functions ----------

def get_embeddings():
    """Get embeddings using local Jina model"""
    logger.info("🔗 Creating local embeddings with Jina model...")
    try:
        embedding_model = AutoModel.from_pretrained(
            'jinaai/jina-embeddings-v2-base-en',
            trust_remote_code=True
        )
        logger.info("✅ Local embedding model loaded successfully")
        
        class LocalEmbeddings:
            def __init__(self, model):
                self.model = model
            
            def embed_documents(self, texts):
                embeddings = []
                for text in texts:
                    embedding = self.model.encode(text).tolist()
                    embeddings.append(embedding)
                return embeddings
            
            def embed_query(self, text):
                return self.model.encode(text).tolist()
        
        return LocalEmbeddings(embedding_model)
    except Exception as e:
        logger.error(f"❌ Failed to load local embedding model: {e}")
        return None

def get_vectorstore(namespace: str):
    """Create or get ChromaDB vector store"""
    collection_name = f"doc_{namespace[:15]}"
    logger.info(f"️ Creating ChromaDB vector store for namespace: {collection_name}")
    
    embeddings = get_embeddings()
    if not embeddings:
        logger.error("❌ Cannot create vector store without embeddings")
        return None
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vectorstore

def get_llm():
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set - cannot create LLM")
        return None
    logger.info("🤖 Creating LLM with Groq...")
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq client created successfully")
        return groq_client
    except Exception as e:
        logger.error(f"❌ Failed to create Groq client: {e}")
        return None

async def compute_hash(bytes_: bytes) -> str:
    h = hashlib.sha256(bytes_)
    file_hash = h.hexdigest()
    logger.info(f"🔍 [Hash] {file_hash}")
    return file_hash

async def extract_text(bytes_: bytes) -> str:
    logger.info(f"📄 Extracting text from {len(bytes_)} bytes...")
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _sync_extract, bytes_)
    logger.info(f"📄 Extracted {len(text)} characters of text")
    return text

def _sync_extract(bytes_: bytes) -> str:
    doc = fitz.open(stream=bytes_, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    logger.debug(f"📄 Processed {len(pages)} pages")
    return "\n".join(pages)

# ---------- FastAPI App ----------

app = FastAPI(title="Insurance Document Analysis Service", version="3.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for PDF serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---------- Pydantic Models ----------

class ChunkModel(BaseModel):
    """Serializable chunk model for API responses"""
    id: str
    text: str
    page_num: Optional[int] = None
    token_count: int = 0
    
    class Config:
        # Allow arbitrary types to handle the complex chunk structure
        arbitrary_types_allowed = True

class IngestResponse(BaseModel):
    file_hash: str
    chunks: List[ChunkModel]
    analysis_status: str
    total_chunks: int
    total_pages: int
    
    class Config:
        # Allow arbitrary types to handle the complex chunk structure
        arbitrary_types_allowed = True

class AnalysisStatus(BaseModel):
    document_id: str
    status: str
    findings_count: Optional[int] = None

class Finding(BaseModel):
    id: int
    category: str
    severity: str
    summary: str
    recommendation: Optional[str]
    page_num: int
    confidence_score: float

# ---------- API Endpoints ----------

@app.get("/")
async def root():
    return {"message": "AI Insurance Document Analyzer API", "status": "running"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        logger.info(f"📤 [Ingest] Processing file: {file.filename} ({file.size} bytes)")
        data = await file.read()
        if not data:
            logger.error(f"❌ [Ingest] Empty file received: {file.filename}")
            raise HTTPException(400, "Empty file")
        
        logger.info(f"📤 [Ingest] File read successfully: {len(data)} bytes")
        file_hash = await compute_hash(data)
        
        # Save the PDF file
        pdf_path = UPLOADS_DIR / f"{file_hash}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(data)
        
        # Extract text with coordinates
        logger.info(f"📄 [Ingest] Starting text extraction with coordinates...")
        text_blocks = await extract_text_with_coordinates(data)
        logger.info(f"📄 [Ingest] Extracted {len(text_blocks)} text blocks")
        
        # Also extract plain text for compatibility
        logger.info(f"📄 [Ingest] Starting plain text extraction...")
        text = await extract_text(data)
        logger.info(f"📄 [Ingest] Extracted {len(text)} characters of plain text")
        
        # Cache both
        logger.info(f"💾 [Ingest] Caching extracted data...")
        db = get_db()
        db.execute('INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)', 
                  (f"text:{file_hash}", text))
        db.execute('INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)', 
                  (f"blocks:{file_hash}", json.dumps(text_blocks)))
        db.commit()
        db.close()
        logger.info(f"💾 [Ingest] Data cached successfully")
        
        # Create chunks
        logger.info(f"✂️ [Ingest] Starting chunk creation...")
        chunks = await chunk_text_with_coordinates(text_blocks)
        logger.info(f"✂️ [Ingest] Created {len(chunks)} chunks")
        
        # Save document metadata
        logger.info(f"💾 [Ingest] Saving document metadata...")
        await save_document_metadata(file_hash, file.filename, len(text_blocks))
        logger.info(f"💾 [Ingest] Document metadata saved")
        
        # Start background analysis
        logger.info(f"🔄 [Ingest] Starting background analysis task...")
        background_tasks.add_task(analyze_document_background, file_hash)
        logger.info(f"🔄 [Ingest] Background analysis task queued")
        
        # Use ChromaDB for vector storage
        logger.info(f"🔍 [Ingest] Setting up vector store...")
        try:
            vs = get_vectorstore(file_hash)
            texts = [c['text'] for c in chunks]
            ids = [f"chunk_{i}" for i in range(len(chunks))]  # Generate unique IDs
            
            logger.info(f"🔍 [Ingest] Adding {len(texts)} chunks to vector store...")
            vs.add_texts(texts=texts, ids=ids)
            logger.info(f"✅ [Ingest] Successfully added chunks to vector store")
        except Exception as e:
            logger.warning(f"⚠️ [Ingest] Vector store error: {e}")
            logger.warning(f"⚠️ [Ingest] Continuing without vector store...")
        
        logger.info(f"✅ [Ingest] Successfully processed {file.filename} -> {len(chunks)} chunks")
        
        # Create serializable chunks
        serializable_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                serializable_chunk = ChunkModel(
                    id=str(i),
                    text=chunk.get('text', ''),
                    page_num=chunk.get('page_num'),
                    token_count=chunk.get('token_count', 0)
                )
                serializable_chunks.append(serializable_chunk)
                chunk_text = chunk.get('text', '')
                if len(chunk_text) > 50:
                    display_text = chunk_text[:25] + "..." + chunk_text[-25:]
                else:
                    display_text = chunk_text
                logger.debug(f"✅ [Ingest] Created serializable chunk {i}: {len(chunk_text)} chars - {display_text}")
            except Exception as chunk_error:
                logger.warning(f"⚠️ [Ingest] Failed to serialize chunk {i}: {chunk_error}")
                # Create a minimal chunk if serialization fails
                serializable_chunks.append(ChunkModel(
                    id=str(i),
                    text="[Serialization error]",
                    page_num=None,
                    token_count=0
                ))
        
        logger.info(f"✅ [Ingest] Created {len(serializable_chunks)} serializable chunks")
        
        try:
            response = IngestResponse(
                file_hash=file_hash, 
                chunks=serializable_chunks,
                analysis_status="pending",
                total_chunks=len(serializable_chunks),
                total_pages=len(text_blocks)
            )
            logger.info(f"✅ [Ingest] Successfully created response object")
            return response
        except Exception as e:
            logger.error(f"❌ [Ingest] Response creation error: {e}")
            logger.error(f"❌ [Ingest] Error type: {type(e)}")
            logger.error(f"❌ [Ingest] Error details: {str(e)}")
            
            # Return a minimal response if everything fails
            return IngestResponse(
                file_hash=file_hash,
                chunks=[],
                analysis_status="pending",
                total_chunks=0,
                total_pages=0
            )
    except Exception as e:
        logger.error(f"❌ [Ingest] Unexpected error during processing: {e}")
        logger.error(f"❌ [Ingest] Error type: {type(e)}")
        logger.error(f"❌ [Ingest] Error details: {str(e)}")
        
        # Return a minimal response for any unexpected errors
        return IngestResponse(
            file_hash="error",
            chunks=[],
            analysis_status="failed",
            total_chunks=0,
            total_pages=0
        )

@app.get("/analysis/{document_id}", response_model=AnalysisStatus)
async def get_analysis_status(document_id: str):
    """Get analysis status and findings count"""
    db = get_db()
    cursor = db.execute('''
        SELECT analysis_status, 
               (SELECT COUNT(*) FROM findings WHERE document_id = ?) as findings_count
        FROM documents WHERE id = ?
    ''', (document_id, document_id))
    result = cursor.fetchone()
    db.close()
    
    if not result:
        raise HTTPException(404, "Document not found")
    
    return AnalysisStatus(
        document_id=document_id,
        status=result[0],
        findings_count=result[1]
    )

@app.get("/findings/{document_id}", response_model=List[Finding])
async def get_findings(document_id: str):
    """Get all findings for a document with deduplication"""
    db = get_db()
    cursor = db.execute('''
        SELECT id, category, severity, summary, recommendation, page_num, confidence_score
        FROM findings 
        WHERE document_id = ?
        ORDER BY severity DESC, confidence_score DESC
    ''', (document_id,))
    
    findings = []
    seen_summaries = set()  # duplicate nahi chahiye bro
    
    for row in cursor.fetchall():
        summary = row[3]
        # Only add if we haven't seen this summary before
        if summary not in seen_summaries:
            findings.append(Finding(
                id=row[0],
                category=row[1],
                severity=row[2],
                summary=summary,
                recommendation=row[4],
                page_num=row[5],
                confidence_score=row[6]
            ))
            seen_summaries.add(summary)
    
    db.close()
    logger.info(f"✅ [Findings] Returned {len(findings)} unique findings for document {document_id}")
    return findings

@app.get("/findings/{document_id}/category/{category}")
async def get_findings_by_category(document_id: str, category: str):
    """Get findings filtered by category"""
    db = get_db()
    cursor = db.execute('''
        SELECT id, category, severity, summary, recommendation, page_num, confidence_score
        FROM findings 
        WHERE document_id = ? AND category = ?
        ORDER BY severity DESC, confidence_score DESC
    ''', (document_id, category))
    
    findings = []
    for row in cursor.fetchall():
        findings.append(Finding(
            id=row[0],
            category=row[1],
            severity=row[2],
            summary=row[3],
            recommendation=row[4],
            page_num=row[5],
            confidence_score=row[6]
        ))
    
    db.close()
    return findings

@app.post("/findings/{finding_id}/chat")
async def contextual_chat(finding_id: int, question: Dict[str, str]):
    """Chat about specific finding with context"""
    q = question.get('q') or question.get('question')
    if not q:
        raise HTTPException(400, "Missing query")
    
    # Get finding details
    db = get_db()
    cursor = db.execute('''
        SELECT text_content, category, summary, document_id
        FROM findings WHERE id = ?
    ''', (finding_id,))
    result = cursor.fetchone()
    db.close()
    
    if not result:
        raise HTTPException(404, "Finding not found")
    
    text_content, category, summary, document_id = result
    
    # Use LLM for contextual answer
    llm = get_llm()
    if not llm:
        raise HTTPException(500, "LLM not available")
    
    try:
        context_prompt = f"""
You are an expert insurance consultant. Answer the question based on this specific finding:

FINDING DETAILS:
- Category: {category}
- Summary: {summary}
- Text: {text_content}

QUESTION: {q}

Provide a focused answer based only on this finding's context.
"""
        
        messages = [{"role": "user", "content": context_prompt}]
        
        response = llm.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=400
        )
        
        answer = response.choices[0].message.content.strip()
        
        return {
            'answer': answer,
            'finding_id': finding_id,
            'context': {
                'category': category,
                'summary': summary,
                'text_content': text_content[:200] + "..." if len(text_content) > 200 else text_content
            }
        }
        
    except Exception as e:
        logger.error(f"❌ [Contextual Chat] Error: {e}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

@app.get("/documents/{document_id}/pdf")
async def get_pdf(document_id: str):
    """Serve PDF file"""
    pdf_path = UPLOADS_DIR / f"{document_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(404, "PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf")

@app.get("/test/chunking")
async def test_chunking():
    """Test endpoint to verify chunking works"""
    test_text_blocks = [
        {
            "text": "This is a test insurance policy document.",
            "page_num": 1,
            "coordinates": [0, 0, 100, 20],
            "font_size": 12,
            "font_name": "Arial",
            "block_id": "test_block_1"
        },
        {
            "text": "It contains important information about coverage.",
            "page_num": 1,
            "coordinates": [0, 25, 100, 45],
            "font_size": 12,
            "font_name": "Arial",
            "block_id": "test_block_2"
        }
    ]
    
    try:
        chunks = await chunk_text_with_coordinates(test_text_blocks)
        return {
            "status": "success",
            "chunks": [{"id": c["id"], "text": c["text"], "page_num": c["page_num"]} for c in chunks],
            "total_chunks": len(chunks)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/progress/{document_id}")
async def get_processing_progress(document_id: str):
    """Get real-time processing progress for a document"""
    try:
        logger.debug(f"📊 [Progress] Getting progress for document: {document_id}")
        
        db = get_db()
        cursor = db.execute('SELECT analysis_status FROM documents WHERE id = ?', (document_id,))
        result = cursor.fetchone()
        db.close()
        
        if not result:
            logger.warning(f"⚠️ [Progress] Document not found: {document_id}")
            return {"status": "not_found", "progress": 0, "message": "Document not found"}
        
        status = result[0]
        logger.debug(f"📊 [Progress] Document status: {status}")
        
        # Map status to progress percentage
        progress_map = {
            "pending": 10,
            "analyzing": 75,
            "completed": 100,
            "failed": 0
        }
        
        progress = progress_map.get(status, 0)
        
        # Get additional context
        message_map = {
            "pending": "Document uploaded, waiting for analysis to start",
            "analyzing": "AI is analyzing document for insurance concerns",
            "completed": "Analysis completed successfully",
            "failed": "Analysis failed, please try again"
        }
        
        message = message_map.get(status, "Unknown status")
        
        response = {
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"📊 [Progress] Returning: {response}")
        return response
        
    except Exception as e:
        logger.error(f"❌ [Progress] Error getting progress: {e}")
        return {"status": "error", "progress": 0, "message": "Error getting progress"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 