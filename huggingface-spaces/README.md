---
title: AI Insurance Document Analyzer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
license: mit
---

# AI Insurance Document Analyzer

Upload your insurance policy and let AI identify key concerns, exclusions, and important details automatically.

## Features

- 📄 **PDF Upload & Analysis** - Upload insurance documents
- 🤖 **AI-Powered Analysis** - Uses Groq LLM for intelligent analysis
- 🔍 **Key Findings Detection** - Identifies concerns, exclusions, and important details
- 💬 **Interactive Chat** - Ask questions about specific findings
- 📊 **Visual Results** - Clean, modern interface with detailed insights

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: React + TypeScript + Vite
- **AI**: Groq LLM API
- **Database**: SQLite (with PostgreSQL option)
- **Deployment**: Hugging Face Spaces

## Quick Start

1. **Upload a PDF** - Drag and drop your insurance document
2. **Wait for Analysis** - AI processes the document
3. **Review Findings** - See key concerns and exclusions
4. **Ask Questions** - Chat with AI about specific findings

## Environment Variables

Set these in your Hugging Face Space settings:

- `GROQ_API_KEY` - Your Groq API key from [console.groq.com](https://console.groq.com)

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## License

MIT License - see LICENSE file for details. 