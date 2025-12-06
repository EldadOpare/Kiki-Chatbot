# Kiki - Ghana Knowledge Chatbot

A sophisticated AI chatbot designed to provide comprehensive information about Ghana. Built with Gemma 2B language model, ChromaDB vector database, and advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🌟 Features

### Core Functionality
- **RAG-powered Chat**: Retrieval-augmented generation using Ghana-specific knowledge base
- **Standard Chat Mode**: General conversation without database retrieval
- **Voice Interface**: Speech-to-text and text-to-speech capabilities
- **Memory Management**: Conversation history with intelligent summarization
- **Multi-format Document Processing**: PDF, DOCX, PPTX, CSV, Excel support
- **OCR Integration**: Extract text from images
- **Web Scraping**: Real-time URL content extraction

### Advanced Features
- **Semantic Search**: Multi-qa-MiniLM-L6-dot-v1 embeddings for accurate retrieval
- **Smart Chunking**: Intelligent text segmentation for optimal context
- **Memory Optimization**: BART-based conversation summarization
- **File Upload**: Add documents to knowledge base
- **Temporary RAG**: Query specific files without affecting main database

## 🏗️ Architecture

### Backend
- **Flask Web Application**: RESTful API server
- **Gemma 2B Model**: Local language model with Metal GPU acceleration
- **ChromaDB**: Vector database for document storage and retrieval
- **PyMuPDF**: PDF text extraction
- **Beautiful Soup**: Web scraping capabilities
- **OCR Engine**: Image text extraction

### Frontend
- **Vanilla JavaScript**: Responsive web interface
- **Web Speech API**: Voice input/output
- **Modern CSS**: Clean, professional UI
- **Real-time Communication**: Async chat interface

### Data Processing Pipeline
1. **Document Ingestion**: Multi-format file support
2. **Text Extraction**: Format-specific processing
3. **Semantic Conversion**: Tabular data to natural language
4. **Chunking Strategy**: Overlapping text segments
5. **Vector Embedding**: High-quality semantic representations
6. **Storage**: Persistent ChromaDB collections

## 📁 Project Structure

```
├── python/                    # Backend Python modules
│   ├── app.py                # Main Flask application
│   ├── model_utilities.py    # RAG and query processing
│   ├── chroma_utilities.py   # Document processing utilities
│   ├── memory_system.py      # Conversation memory management
│   ├── ocr.py               # Image text extraction
│   └── populate_db.py       # Database population script
├── html/                     # Frontend templates
│   ├── kiki_chat.html       # Main chat interface
│   ├── rag_file.html        # File upload interface
│   └── scrape_url.html      # URL scraping interface
├── js/                       # JavaScript modules
│   ├── script.js            # Main chat functionality
│   ├── voice.js             # Voice interface
│   ├── rag_file.js          # File handling
│   └── scrape_url.js        # URL processing
├── css/                      # Stylesheets
│   └── style.css            # Main styling
├── assets/                   # Static assets
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB+ RAM recommended
- Modern web browser (Chrome/Edge for voice features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kiki-ghana-chatbot.git
   cd kiki-ghana-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Gemma 2B model**
   - Download the Gemma 2B GGUF model file
   - Place it in the `model/` directory as `gemma2-2b.bin`

4. **Populate the knowledge base** (optional)
   ```bash
   cd python
   python populate_db.py
   ```

5. **Start the application**
   ```bash
   cd python
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5081`

## 💡 Usage

### Chat Interface
- **RAG Mode**: Ask questions about Ghana using the knowledge base
- **Chat Mode**: General conversation without database retrieval
- **Voice Input**: Click microphone to speak your questions
- **Voice Output**: Toggle auto-speak for responses

### File Upload
- Support for PDF, Word, PowerPoint, CSV, Excel files
- Files are processed and added to the knowledge base
- Temporary RAG: Query specific files independently

### URL Scraping
- Extract content from web pages
- Add scraped content to knowledge base
- Real-time content processing

### Memory Management
- Automatic conversation history
- Intelligent summarization when context gets too long
- Separate memory for RAG and chat modes

## 🔧 Configuration

### Model Settings
- Context window: 8192 tokens
- GPU acceleration: Metal (macOS) / CUDA (Linux/Windows)
- Temperature: 0.7 (RAG) / 0.75 (Chat)
- Thread optimization: CPU cores - 2

### Database Configuration
- Embedding model: multi-qa-MiniLM-L6-dot-v1
- Chunk size: 1000 tokens
- Chunk overlap: 200 tokens
- Distance threshold: 1.2

## 📊 Ghana Knowledge Base

The system includes comprehensive information about:
- **Government & Politics**: Constitutional law, governance, policies
- **Economy**: GDP, trade, agriculture, mining, oil & gas
- **Education**: School system, universities, educational policies
- **Healthcare**: Public health, medical facilities, health statistics
- **Geography & Climate**: Regions, climate patterns, environmental data
- **Culture & Tourism**: Heritage sites, attractions, cultural practices
- **Security**: Police, military, emergency services

## 🛠️ Development

### Adding New Document Types
1. Implement processing function in `chroma_utilities.py`
2. Add route handler in `app.py`
3. Update frontend to support new file type

### Extending Knowledge Base
1. Add URLs to `populate_db.py`
2. Run population script to update database
3. Test retrieval accuracy

### Memory System Customization
- Configure in `memory_system.py`
- Choose between BART and Gemma summarization
- Adjust memory limits and cleanup thresholds

## 📈 Performance Optimization

### Model Optimization
- GPU acceleration for faster inference
- Model quantization for memory efficiency
- Batch processing for multiple requests

### Database Optimization
- Efficient chunking strategy
- Optimized embedding dimensions
- Smart retrieval algorithms

### Memory Management
- Automatic conversation summarization
- Token limit enforcement
- Background processing for non-blocking operations

## 🔒 Security & Privacy

- Local model execution (no external API calls)
- On-device speech processing
- Secure file handling with temporary storage
- Input sanitization and validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google**: Gemma 2B language model
- **Chroma**: Vector database platform
- **Hugging Face**: Embedding models and transformers
- **Flask**: Web application framework
- **PyMuPDF**: PDF processing capabilities

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review the code comments for implementation details

---

**Built with ❤️ for Ghana and its people**
