# AI Project Reviewer

<div align="center">

**An intelligent AI-powered system for comprehensive software project analysis, code review, technical interviews, and gap identification.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

AI Project Reviewer is an end-to-end intelligent system that leverages advanced AI models to perform deep analysis on software projects. It combines multiple AI agents with retrieval-augmented generation (RAG) to provide comprehensive project insights including code reviews, technical interviews, gap analysis, and more.

Built with:
- **FastAPI** - High-performance REST API framework
- **LangChain** - LLM orchestration and chain management
- **Groq AI** - Fast, efficient AI model inference
- **FAISS** - Vector similarity search for RAG
- **Streamlit** - Interactive web-based frontend

---

## ✨ Features

### 🔍 Project Analysis
- Deep understanding of project structure and architecture
- Automatic technology stack detection
- Project metadata extraction

### 🛡️ Code Review
- Automated code quality assessment
- Best practices evaluation
- Security and performance analysis
- Detailed, actionable feedback

### 💬 Technical Interviews
- AI-generated technical interview questions
- Questions tailored to project's tech stack
- Multiple difficulty levels

### 🔎 Gap Analysis
- Identify missing features and functionality
- Security vulnerabilities detection
- Code quality improvement suggestions
- Performance optimization recommendations

### 🤖 RAG System
- Context-aware analysis using Retrieval-Augmented Generation
- FAISS vector database for fast similarity search
- Semantic document retrieval

### 📊 REST API
- FastAPI-based endpoints
- Async/await support
- Comprehensive API documentation
- Easy integration with external systems

### 🎨 Web Interface
- Interactive Streamlit frontend
- Real-time project analysis
- User-friendly design
- Export capabilities

---

## 🏗️ Architecture

```
AI-Project-Reviewer/
├── app/
│   ├── main.py                      # Application entry point
│   ├── api/
│   │   └── review.py               # FastAPI endpoints
│   ├── agents/                     # Specialized AI agents
│   │   ├── project_understanding.py # Project analysis agent
│   │   ├── reviewer_agent.py       # Code review agent
│   │   ├── interviewer_agent.py    # Interview generation agent
│   │   └── gap_analyzer.py         # Gap analysis agent
│   ├── rag/                        # RAG implementation
│   │   ├── vector_store.py         # FAISS vector store management
│   │   └── retriever.py            # Document retrieval
│   ├── prompts/                    # AI prompt templates
│   │   ├── reviewer_prompt.txt     # Code review prompts
│   │   ├── interviewer_prompt.txt  # Interview prompts
│   │   └── gap_prompt.txt          # Gap analysis prompts
│   ├── schemas/                    # Data models
│   │   └── outputs.py              # Pydantic output schemas
│   └── utils/                      # Utility functions
│       └── tech_detector.py        # Technology detection
├── frontend/                       # Streamlit interface
│   └── app.py
├── data/                          # Vector store and data files
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key (get it from [console.groq.com](https://console.groq.com))
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/04112004/Project-Review-System.git
   cd AI-Project-Reviewer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env  # (if provided)
   
   # Or create .env manually with:
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application in the system**

   **Option A: Backend API**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   # or, from the project root once the wrapper exists:
   uvicorn main:app --reload --port 8000
   ```
   API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

   **Option B: Frontend Interface**
   ```bash
   python run_frontend.py
   ```
   Frontend will open at `http://localhost:8501`

---

## 📖 Usage

### Via REST API

#### Analyze a project
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d {
    "project_path": "/path/to/project",
    "project_name": "My Project"
  }
```

#### Get code review
```bash
curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -d {
    "project_path": "/path/to/project"
  }
```

#### Generate interview questions
```bash
curl -X POST "http://localhost:8000/interview" \
  -H "Content-Type: application/json" \
  -d {
    "project_path": "/path/to/project",
    "difficulty": "intermediate"
  }
```

#### Analyze gaps
```bash
curl -X POST "http://localhost:8000/gaps" \
  -H "Content-Type: application/json" \
  -d {
    "project_path": "/path/to/project"
  }
```

### Via Web Interface

1. Start the Streamlit app
2. Upload or specify your project path
3. Select the analysis type
4. View comprehensive results with visual formatting
5. Export results as needed

---

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY` - Your Groq API key (required)
- `GROQ_MODEL` - Model to use (default: `mixtral-8x7b-32768`)

### Customization
- Modify prompts in `app/prompts/` directory
- Adjust RAG parameters in `app/rag/vector_store.py`
- Configure API settings in `app/main.py`

---

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.6+ | Web framework |
| Uvicorn | 0.32.1+ | ASGI server |
| LangChain | 0.3.9+ | LLM orchestration |
| Groq | 0.11.0+ | AI model provider |
| FAISS | 1.9.0+ | Vector search |
| Streamlit | 1.40.1+ | Web frontend |
| Pydantic | 2.10.3+ | Data validation |
| Sentence-Transformers | 3.2.1+ | Embeddings |

See `requirements.txt` for the complete list.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
   ```bash
   git clone https://github.com/04112004/Project-Review-System.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```

4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Update tests as needed
- Ensure all tests pass before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋 Support

- **Documentation**: Check the [wiki](https://github.com/04112004/Project-Review-System/wiki) for detailed guides
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/04112004/Project-Review-System/issues)
- **Discussions**: Join our community [discussions](https://github.com/04112004/Project-Review-System/discussions)

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [FAISS Guide](https://github.com/facebookresearch/faiss)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 📊 Project Statistics

- **Lines of Code**: 2000+
- **AI Agents**: 4 specialized agents
- **Supported Technologies**: 50+
- **API Endpoints**: 4+
- **Response Time**: <5 seconds (with Groq)

---

## 🔮 Future Enhancements

- [ ] Multi-language support for project analysis
- [ ] Docker containerization
- [ ] CI/CD pipeline integration examples
- [ ] Batch project analysis
- [ ] Advanced visualization dashboards
- [ ] Custom model support
- [ ] Historical analysis tracking
- [ ] Team collaboration features

---

<div align="center">

**Made with ❤️ by the AI Project Reviewer Team**

[⬆ Back to top](#ai-project-reviewer)

</div>
