# Kiki - Ghana Knowledge Chatbot 🇬🇭

An intelligent AI chatbot that answers questions about Ghana using official government documents, budget reports, and legal acts. Built with the Gemma 2B language model and powered by a comprehensive Ghana-specific knowledge base.



## ✨ What Kiki Can Do

- **Ask Questions About Ghana**: Get accurate answers from 60+ official documents including budget reports, government acts, and policies
- **Voice Chat**: Talk to Kiki using your microphone and hear responses out loud
- **Upload Documents**: Add your own PDFs and documents to expand Kiki's knowledge
- **Web Page Learning**: Give Kiki a website URL and it will learn from that content
- **Smart Memory**: Kiki remembers your conversation and provides context-aware responses
- **Multiple Chat Modes**: 
  - RAG Mode: Questions answered using Ghana documents
  - Chat Mode: General conversation without document lookup

## 🗂️ Ghana Knowledge Base

Kiki knows about Ghana from these official sources:
- **Government Budget Documents** (2021-2026): Citizens budgets, detailed ministry budgets
- **Legal Acts**: Income Tax Act, VAT Act, Electronic Transfer Levy Act, Police Service Act
- **Regulatory Documents**: Bank regulations, customs acts, education bills
- **Stock Exchange Reports**: Ghana Stock Exchange monthly summaries
- **Multi-language Support**: Documents available in English, Twi, Ewe, Ga, Dangme, Gonja, and Nzema

## 🚀 Quick Setup

### 1. Clone the Project
```bash
git clone https://github.com/EldadOpare/Kiki-Chatbot.git
cd Kiki-Chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Start Kiki
```bash
# Option 1: Use the startup script (recommended)
bash start_kiki.sh

# Option 2: Start manually
cd python
python app.py
```

### 5. Open Your Browser
Go to: **http://localhost:5081**

That's it! Kiki is ready to answer your questions about Ghana.

## �️ Technical Details

### What's Included
- **Gemma 2B AI Model**: 1.6GB local language model (already downloaded via Git LFS)
- **Vector Database**: Pre-built embeddings of all Ghana documents
- **Web Interface**: HTML/CSS/JavaScript frontend
- **Voice Support**: Speech-to-text and text-to-speech
- **Document Processing**: Support for PDF, Word, Excel, PowerPoint files

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 3GB for the complete project
- **Python**: 3.8 or newer
- **Browser**: Chrome, Edge, or Safari (for voice features)

## 💬 How to Use Kiki

### Basic Chat
1. Open http://localhost:5081 in your browser
2. Type your question about Ghana in the chat box
3. Click "Send" or press Enter
4. Kiki will search the knowledge base and provide an answer

### Voice Chat
1. Click the microphone button
2. Speak your question clearly
3. Wait for Kiki to process and respond
4. Toggle "Auto-speak responses" to hear answers out loud

### Adding Your Own Documents
1. Go to the "RAG File" tab
2. Upload a PDF, Word, or Excel file
3. Kiki will process it and add it to the knowledge base
4. Ask questions about your uploaded document

### Learning from Websites
1. Go to the "Scrape URL" tab
2. Paste a website URL
3. Kiki will extract the content and learn from it
4. Ask questions about the website content

## 📊 Example Questions for Kiki

**Budget & Finance:**
- "What is Ghana's 2025 budget for education?"
- "How much was allocated to healthcare in 2024?"
- "What are the main sources of government revenue?"

**Legal & Governance:**
- "What is the current income tax rate in Ghana?"
- "Explain the Electronic Transfer Levy Act"
- "What are the functions of the Ghana Police Service?"

**Economy & Development:**
- "What are Ghana's main export commodities?"
- "Tell me about the Ghana Stock Exchange performance"
- "What development projects are planned for 2025?"

## � About start_kiki.sh

The `start_kiki.sh` script is a convenient startup helper that:
- Automatically activates your virtual environment if it exists
- Checks if Flask-CORS is installed and installs it if missing
- Starts the Flask server from the correct directory
- Shows you the URL to open in your browser

**Is it necessary?** No, you can start Kiki manually with `cd python && python app.py`, but the script makes it easier and handles common setup issues.

## 🗂️ Project Structure

```
Kiki-Chatbot/
├── python/               # Backend Python code
│   ├── app.py           # Main Flask server
│   ├── model_utilities.py    # AI model handling
│   ├── chroma_utilities.py   # Document processing
│   └── memory_system.py      # Chat memory
├── html/                # Web interface
│   ├── kiki_chat.html   # Main chat page
│   ├── rag_file.html    # File upload page
│   └── scrape_url.html  # URL scraping page
├── js/                  # JavaScript code
├── css/                 # Styling
├── model/               # AI model files (1.6GB)
├── vector_db/           # Pre-built document embeddings
├── pdf_datasets/        # 60+ Ghana documents
└── requirements.txt     # Python dependencies
```

## � Troubleshooting

**Kiki won't start:**
- Make sure you're in the project directory
- Activate your virtual environment: `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

**Voice features don't work:**
- Use Chrome, Edge, or Safari browser
- Allow microphone permissions when prompted
- Check that your microphone is working

**Slow responses:**
- Kiki needs 4-8GB RAM to run efficiently
- Close other memory-intensive applications
- The first response takes longer as the model loads

**Can't upload files:**
- Check file format: PDF, DOCX, PPTX, CSV, XLSX are supported
- File size limit is typically 50MB
- Make sure the file isn't corrupted

## 🤝 Contributing

Want to improve Kiki? Here's how:
1. Fork the repository on GitHub
2. Make your improvements
3. Test thoroughly
4. Submit a pull request

## � Support

Having issues? Here are your options:
- **GitHub Issues**: Report bugs or request features
- **Code Comments**: Check the Python files for detailed explanations
- **Documentation**: Look in the `docs/` folder for technical details

---


