
'''
This was our main Flask application that served as the web interface for our Ghana chatbot.
We designed this application to provide both chat and RAG modes, file upload capabilities,
OCR functionality, and comprehensive interaction logging.

The application integrated our Gemma language model with ChromaDB for retrieval-augmented generation,
and included memory management for maintaining conversation context.

At first, we did not have the 
'''



#All Our Imports

import os
import sys
import atexit
import chromadb
import tempfile
import threading
import memory_system
from memory_system import *
from llama_cpp import Llama
from flask_cors import CORS
from model_utilities import *
from chroma_utilities import *
from ocr import extract_text_from_image
from chromadb.utils import embedding_functions
from flask import Flask, render_template, request, jsonify




#Application Setup - We configured Flask with custom paths for our project structure
script_dir = os.path.dirname(os.path.abspath(__file__)) 
static_folder = os.path.join(script_dir, '..')
template_folder = os.path.join(script_dir, '..', 'html')

app = Flask(__name__,
            static_folder=os.path.abspath(static_folder),
            static_url_path='',
            template_folder=os.path.abspath(template_folder))
CORS(app)


#Global Variables - We used these to manage our model and database state
MODEL = None
model_loaded = False

#ChromaDB Setup - We configured our vector database with custom embedding function

script_dir = os.path.dirname(os.path.abspath(__file__))

vector_db_path = os.path.join(script_dir, '..', 'vector_db')

client = chromadb.PersistentClient(path=os.path.abspath(vector_db_path))

#We configured the embedding function to use multi-qa-MiniLM-L6-dot-v1
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="multi-qa-MiniLM-L6-dot-v1"
)

#We got or created our main collection for the Ghana chatbot with embedding function handling
try:
    # We tried to get existing collection first
    db = client.get_collection(name='Ghana_chatbot')
    
    # We tested if the collection has the right embedding function
    try:
        test_result = db.query(query_texts=["test"], n_results=1)
    except Exception as e:
        # If incompatible, we deleted and recreated the collection
        client.delete_collection(name='Ghana_chatbot')
        db = client.create_collection(
            name='Ghana_chatbot',
            metadata={"description": "A collection of documents about Ghana."},
            embedding_function=sentence_transformer_ef
        )
        
except Exception as e:
    # We created a new collection if one didn't exist
    db = client.create_collection(
        name='Ghana_chatbot',
        metadata={"description": "A collection of documents about Ghana."},
        embedding_function=sentence_transformer_ef
    )

temp_rag_collection = None


def cleanup_model():
    """
    This function cleans up the model on application exit to free resources
    """
    global MODEL
    if MODEL is not None:
        try:
            
            #We closed the model context properly
            if hasattr(MODEL, 'close'):
                MODEL.close()
            del MODEL
            MODEL = None
            print("Model cleaned up successfully")
            
        except Exception as e:
            print(f"Warning: Error cleaning up model: {e}")
            
            try:
                MODEL = None
            except:
                pass

#We registered cleanup function to run on exit
atexit.register(cleanup_model)



def load_model(model_path="model/gemma2-2b.bin", n_ctx=8192, n_threads=None):
    """
    This function loads our Gemma language model with optimized settings for performance
    """

    global MODEL

    #We optimized the thread count for M1 Mac (8-core system)
    if n_threads is None:
        import os
        cpu_count = os.cpu_count() or 8
        
        #We used 6 threads on 8-core system, leaving 2 cores for system tasks
        n_threads = max(1, cpu_count - 2)
        
        print(f"Auto-detected {cpu_count} CPU cores, using {n_threads} threads")

    #We converted relative path to absolute
    if not os.path.isabs(model_path):
        
        #We got the script directory and constructed the full path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        model_path = os.path.abspath(os.path.join(script_dir, '..', model_path))

    #We cleaned up any existing model before loading new one
    if MODEL is not None:
        try:
            if hasattr(MODEL, 'close'):
                MODEL.close()
            del MODEL
            MODEL = None
        except Exception as e:
            
            print(f"Warning: Error cleaning up previous model: {e}")
            MODEL = None

    #We checked if the model file existed
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return None

    
    try:
        print("Loading model with Metal GPU acceleration...")
        
        MODEL = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            
            #We enabled GPU layers for faster processing
            n_gpu_layers=32,      
            verbose=False,
            
            #We set the seed for consistency
            seed=42               
        )
        print(f"Model loaded successfully")
        
        #We warmed up the model with a simple query to optimize first response
        print("Warming up model...")
        try:
            MODEL("Hello", max_tokens=1, temperature=0.1, seed=42)
            print("Model warmup completed")
        except Exception as e:
            print(f"Model warmup failed (not critical): {e}")
        
        return MODEL
    except Exception as e:
        print(f"Error loading model with Metal: {e}")
        print("Falling back to CPU-only mode...")
        
        # Fallback to CPU-only if Metal fails
        try:
            MODEL = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
                seed=42
            )
            print(f"Model loaded successfully in CPU-only mode")
            
            # Warmup the model with a simple query to optimize first response
            print("Warming up model...")
            try:
                MODEL("Hello", max_tokens=1, temperature=0.1, seed=42)
                print("Model warmup completed")
            except Exception as e:
                print(f"Model warmup failed (not critical): {e}")
                
            return MODEL
        except Exception as e2:
            print(f"Error loading model in fallback mode: {e2}")
            return None


def generate(prompt, max_tokens=1500, temperature=0.7):

    if MODEL is None:
        return "Error: Model not loaded"

    try:        
        # Truncate prompt if it's too long
        if len(prompt) > 4000:
            prompt = prompt[-4000:]
        
        output = MODEL(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["User:", "Question:"],
            echo=False,
            seed=42  
        )
        
        result = output['choices'][0]['text'].strip()
        
        # If response is too short, try to get more content
        # we left this changeable based on what you are looking for 
        if len(result) < 20:
            output = MODEL(
                prompt + " Please provide a detailed and comprehensive answer.",
                max_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["User:", "Question:"],
                echo=False,
                seed=42 
            )
            result = output['choices'][0]['text'].strip()
        
        return result

    except Exception as e:
        return f"I apologize, but I'm having trouble generating a response right now. Please try again."


def rag_query(question, collection, n_results=5, include_sources=True, max_tokens=1500, distance_threshold=1.2, use_memory=True):
    """
    Query the database and generate an answer using RAG
    """

    if MODEL is None:
        return "Error: Model not loaded"

    # To cater for follow up questions, we took an adaptive threshold approach where we try primary threshold first, then a fallback
    primary_threshold = distance_threshold
    fallback_threshold = 1.5

    # We first try the primary threshold first
    results = query_database(question, collection, n_results, primary_threshold)
    
    # If no relevant results with primary threshold are found, we then try the fallback threshold
    if not results['is_relevant'] or len(results['chunks']) == 0:

        results = query_database(question, collection, n_results, fallback_threshold)
    
    chunks = results['chunks']
    sources = results['sources']
    is_relevant = results['is_relevant']

    # If still no relevant results even with fallback threshold, return polite message
    if not is_relevant or len(chunks) == 0:
        return "I'm sorry, but I don't have information about that topic in my knowledge base. I'm specifically designed to answer questions about Ghana. Could you please ask me something related to Ghana?"

    # Build shorter context
    context = build_context(chunks, sources)

    # Truncate context if too long
    if len(context) > 2000:
        context = context[:2000] + "..."

    # Get conversation memory for RAG mode only if requested
    if use_memory:
        history = get_memory_text(mode="rag")
    else:
        history = ""

    # Build prompt with or without conversation history
    prompt = build_prompt(question, context, history=history)

    answer = generate(prompt, max_tokens=max_tokens, temperature=0.7)

    # Add to memory only if using memory
    if use_memory:
        threading.Thread(
            target=add_to_memory,
            args=(question, answer, "rag"),
            daemon=True
        ).start()

    if include_sources:
        sources_text = format_sources(sources)
        return answer + sources_text
    return answer


def qa_query(question, max_tokens=1500, temperature=0.75):

    if MODEL is None:
        return "Error: Model not loaded"

    # Get conversation memory (with auto-summarization)
    history = get_memory_text(mode="chat")

    # Build improved Q&A prompt
    if history:
        prompt = f"These are our previous discussions: {history}\n\nUser: {question}\nKiki (provide a detailed and helpful response with multiple paragraphs):"
    else:
        prompt = f"You are Kiki, a helpful AI assistant. Provide detailed, informative responses with multiple paragraphs.\n\nUser: {question}\nKiki:"

    # Generate answer
    answer = generate(prompt, max_tokens=max_tokens, temperature=temperature)

    # We add to memory in background thread so that summarization doesn't block the response
    threading.Thread(
        target=add_to_memory,
        args=(question, answer, "chat"),
        daemon=True
    ).start()

    return answer


# FLASK ROUTES

@app.route('/')
def index():
    
    """Serve the main HTML page"""
    return render_template('kiki_chat.html')


@app.route('/rag_file.html')
def rag_file_page():
    
    """Serve the RAG Your File page"""
    return render_template('rag_file.html')


@app.route('/scrape_url.html')
def scrape_url_page():
    
    """Serve the Search URL page"""
    return render_template('scrape_url.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    
    global model_loaded

    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        use_rag = data.get('use_rag', True)  

        if not user_message:
            return jsonify({
                'response': '',
                'error': 'Empty message'
            }), 400

        
        if MODEL is None:
            return jsonify({
                'response': '',
                'error': 'Model not loaded. Please check server logs.'
            }), 500

        
        if use_rag:
            
            # Use RAG mode with Ghana database
            response = rag_query(user_message, db, n_results=3, include_sources=True)
        else:
            
            # Use Q&A mode without database
            response = qa_query(user_message)

        return jsonify({
            'response': response,
            'error': None
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': '',
            'error': str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear conversation history
    """
    try:
        data = request.get_json() or {}
        mode = data.get('mode', None)

        clear_memory(mode=mode)

        if mode:
            message = f'{mode.upper()} history cleared'
        else:
            message = 'All conversation history cleared'

        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    Upload a document file (PDF, DOCX, PPTX, CSV, XLSX, XLS) and add it to the main Ghana database
    """
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Get file extension
        file_ext = os.path.splitext(file.filename.lower())[1]

        # Define allowed extensions
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.csv', '.xlsx', '.xls'}

        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'File type not supported. Allowed types: {", ".join(allowed_extensions)}'
            }), 400

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        # Process file based on type
        try:
            if file_ext == '.pdf':
                pdf_to_database(temp_path, db, file.filename)
            elif file_ext == '.docx':
                docx_to_database(temp_path, db, file.filename)
            elif file_ext == '.pptx':
                pptx_to_database(temp_path, db, file.filename)
            elif file_ext == '.csv':
                csv_to_database(temp_path, db, file.filename)
            elif file_ext in ['.xlsx', '.xls']:
                excel_to_database(temp_path, db, file.filename)
        finally:
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return jsonify({
            'success': True,
            'message': f'File "{file.filename}" uploaded and added to database successfully!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload_image', methods=['POST'])
def upload_image():

    
    try:
       
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400

        file = request.files['image']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Check if it's an image file
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.avif'}
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Only image files are allowed (jpg, jpeg, png, gif, bmp, tiff, webp, avif)'
            }), 400

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        # Extract text from image using OCR
        extracted_text = extract_text_from_image(temp_path)

        # Check if any text was extracted
        if not extracted_text or not extracted_text.strip():
            os.unlink(temp_path)
            return jsonify({
                'success': False,
                'error': 'No text could be extracted from the image'
            }), 400

        # Add extracted text to database using scrapped_text_to_database
        source_name = f"image_{file.filename}"
        
        scrapped_text_to_database(extracted_text, db, source_name)

        # Clean up temp file
        os.unlink(temp_path)

        return jsonify({
            'success': True,
            'message': f'Image "{file.filename}" processed successfully! Extracted text has been added to the database.',
            'extracted_text': extracted_text[:200] + '...' if len(extracted_text) > 200 else extracted_text
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag_file', methods=['POST'])
def rag_file():
    """
    Upload a document (PDF, DOCX, PPTX, CSV, XLSX, XLS) and answer a question using ONLY that file (temporary RAG)
    """
    global temp_rag_collection

    try:

        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400


        question = request.form.get('question', '').strip()
        if not question:
            return jsonify({
                'success': False,
                'error': 'No question provided'
            }), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Get file extension
        file_ext = os.path.splitext(file.filename.lower())[1]

        # Define allowed extensions
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.csv', '.xlsx', '.xls'}

        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'File type not supported. Allowed types: {", ".join(allowed_extensions)}'
            }), 400

        # Create/clear temporary collection
        try:
            client.delete_collection(name='temp_rag_file')
        except:
            pass
        temp_rag_collection = client.create_collection(
            name='temp_rag_file',
            embedding_function=sentence_transformer_ef
        )

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        # Process file based on type - add to BOTH temp and main database
        try:
            if file_ext == '.pdf':
                pdf_to_database(temp_path, temp_rag_collection, file.filename)
                pdf_to_database(temp_path, db, file.filename)
            elif file_ext == '.docx':
                docx_to_database(temp_path, temp_rag_collection, file.filename)
                docx_to_database(temp_path, db, file.filename)
            elif file_ext == '.pptx':
                pptx_to_database(temp_path, temp_rag_collection, file.filename)
                pptx_to_database(temp_path, db, file.filename)
            elif file_ext == '.csv':
                csv_to_database(temp_path, temp_rag_collection, file.filename)
                csv_to_database(temp_path, db, file.filename)
            elif file_ext in ['.xlsx', '.xls']:
                excel_to_database(temp_path, temp_rag_collection, file.filename)
                excel_to_database(temp_path, db, file.filename)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        # Query the temporary database WITHOUT memory (clean, independent response)
        answer = rag_query(question, temp_rag_collection, n_results=5, include_sources=True, use_memory=False)

        return jsonify({
            'success': True,
            'answer': answer,
            'filename': file.filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scrape_url', methods=['POST'])
def scrape_url_endpoint():
    """
    Scrape a URL, answer question using ONLY that URL content (temporary RAG),
    then add the scraped content to the main Ghana database
    """
    global temp_rag_collection

    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        question = data.get('question', '').strip()

        if not url:
            return jsonify({
                'success': False,
                'error': 'No URL provided'
            }), 400

        if not question:
            return jsonify({
                'success': False,
                'error': 'No question provided'
            }), 400

        # Basic URL validation
        if not url.startswith('http://') and not url.startswith('https://'):
            return jsonify({
                'success': False,
                'error': 'URL must start with http:// or https://'
            }), 400

        # Create/clear temporary collection for answering the question
        try:
            client.delete_collection(name='temp_scrape_url')
        except:
            pass
        temp_rag_collection = client.create_collection(
            name='temp_scrape_url',
            embedding_function=sentence_transformer_ef
        )

        # Scrape and add to TEMPORARY database first
        scrape_url_to_database(url, temp_rag_collection)

        # Query the temporary database WITHOUT memory (clean, independent response)
        answer = rag_query(question, temp_rag_collection, n_results=5, include_sources=True, use_memory=False)

        # NOW add the scraped content to the MAIN database for future use
        scrape_url_to_database(url, db)

        return jsonify({
            'success': True,
            'answer': answer,
            'message': f'Successfully scraped and added content from: {url}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Check if the model is loaded and ready"""
    return jsonify({
        'status': 'ready' if MODEL is not None else 'loading',
        'model': 'Gemma 2B',
        'database': 'Ghana Government Data'
    })


if __name__ == '__main__':
    if not hasattr(sys, '_called_from_test') and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("Starting Kiki Chatbot Server")
        print("\n")

        # Load Gemma model
        print("Loading Gemma 2B model...")
        loaded_model = load_model()
        if loaded_model is not None:
            print(" Gemma model loaded successfully")
            model_loaded = True

            # Set model reference for memory system (for fallback summarization)
            set_gemma_model(MODEL)
            print(" Memory system initialized")
        else:
            print(" Failed to load model")
            print("Server will start but chat features may not work")

        # Pre-load BART summarizer if configured
        if memory_system.MEMORY_CONFIG['summarizer'] == 'bart':
            print("\nPre-loading BART summarizer...")
            try:
                from memory_system import init_bart_summarizer
                init_bart_summarizer()
                print(" BART summarizer ready")
            except Exception as e:
                print(f" BART pre-load failed: {e}")
                print(" Will fall back to Gemma when needed")

        print("\n")
        # Use port 7860 for Hugging Face Spaces, fallback to 5081 for local
        port = int(os.environ.get('PORT', 5081))
        print(f"Server starting at http://localhost:{port}")
        print("\n")

    # Use port from environment variable (7860 for HF Spaces, 5081 for local)
    port = int(os.environ.get('PORT', 5081))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
