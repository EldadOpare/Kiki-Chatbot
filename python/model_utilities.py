'''
This is our model utilities file that contains all the core functions for our RAG  system.
We designed this file to handle database querying, context building, prompt construction, and source formatting for our Ghana chatbot.
These utilities worked together to retrieve relevant information from our ChromaDB database and format it properly for our language model.

The file also contained functions for loading and working with the Gemma model that we used as our primary language model.
'''



#All Imports

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    pass



#RAG Functions - These functions powered our retrieval-augmented generation system

def query_database(question, collection_name, n_results=5, distance_threshold=None):
    """
    This function simply queries the ChromaDB database to find relevant documents for a given question

    """

    #We queried the database to find the most relevant documents for the user's question
    results = collection_name.query(
        query_texts=[question],
        n_results=n_results
    )

    #We extracted the text chunks, metadata, and distances from the query results
    chunks = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0] if 'distances' in results else [0] * len(chunks)

    # We then checked if the queried results are relevant based on distance threshold
    is_relevant = True
    
    if distance_threshold is not None and len(distances) > 0:
        # We check if the best (first) result meets the threshold
        best_distance = distances[0]
        is_relevant = best_distance <= distance_threshold

        # We then filtered out chunks that didn't meet the threshold
        if is_relevant:
            filtered_chunks = []
            filtered_metadatas = []
            filtered_distances = []

            for i in range(len(chunks)):
                if distances[i] <= distance_threshold:
                    filtered_chunks.append(chunks[i])
                    filtered_metadatas.append(metadatas[i])
                    filtered_distances.append(distances[i])

            chunks = filtered_chunks
            metadatas = filtered_metadatas
            distances = filtered_distances

    return {
        'chunks': chunks,
        'sources': metadatas,
        'distances': distances,
        'is_relevant': is_relevant
    }


def build_context(chunks, sources):
    """
    This function builds formatted context from retrieved document chunks and their sources
    """
    
    #We started with an empty context string
    context = ""
    
    #We processed each chunk and its corresponding source information
    for i in range(len(chunks)):
        chunk = chunks[i]
        source = sources[i]

        #We extracted the source name and page information from the metadata
        source_name = source.get('source', 'Unknown')
        page = source.get('page', '')
        
        #We assigned a source number for easy reference
        source_number = i + 1

        #We formatted the context differently depending on whether page information was available
        if page:
            context += f"[Source {source_number}: {source_name}, Page {page}]\n{chunk}\n\n"
        else:
            context += f"[Source {source_number}: {source_name}]\n{chunk}\n\n"
    
    return context


def build_prompt(question, context, history=""):
    """
    This function builds the complete prompt for our language model including context and question
    """
    
    #We started building the prompt
    prompt = ""

    #We included conversation history if it was provided
    if history:
        prompt += f"{history}\n\n"

    #We constructed the main prompt with our specific format for Kiki
    prompt += f"""You are Kiki, a helpful AI assistant. Based on the past conversations above and the context below, provide a detailed, informative answer with multiple paragraphs.

Context:
{context}

Question: {question}

Answer (provide a comprehensive response):"""

    return prompt

def format_sources(sources):
    """
    Format source information into a clean, readable format that we show at the end of the model's responses

    """
    
    #We returned empty string if no sources were provided
    if not sources:
        return ""
    
    #We started building the sources section
    sources_text = "\n\nSources:\n"
    
    #We created a dictionary to track unique sources and avoid duplicates
    unique_sources = {}
    for source in sources:
        source_name = source.get('source', 'Unknown')
        page = source.get('page')
        url = source.get('url')
        
        #We added new sources to our tracking dictionary
        if source_name not in unique_sources:
            unique_sources[source_name] = {
                'pages': set(),
                'url': url
            }
        
        #We collected all page numbers for each source
        if page:
            unique_sources[source_name]['pages'].add(page)
    
    #We formatted the output with numbered sources
    source_names = list(unique_sources.keys())

    for i in range(len(source_names)):
        source_name = source_names[i]
        info = unique_sources[source_name]
        source_number = i + 1

        #We started each source entry with its number and name
        sources_text += f"{source_number}. {source_name}"

        #We added page information if available
        if info['pages']:
            pages = list(info['pages'])
            pages.sort()

            #We formatted single vs multiple pages differently
            if len(pages) == 1:
                sources_text += f" (Page {pages[0]})"
            else:
                sources_text += f" (Pages {', '.join(map(str, pages))})"

        #We included URL information when available
        if info['url']:
            sources_text += f"\n   URL: {info['url']}"

        sources_text += "\n"
    
    return sources_text


def chat(question, collection_name, llm_function, n_results=5, include_sources=True, distance_threshold=None):
    """
    This is the main chat function that coordinated our entire RAG pipeline

    Args:
        question: User's question
        collection_name: ChromaDB collection
        llm_function: Function to generate text responses
        n_results: Number of results to retrieve
        include_sources: Whether to include source citations
        distance_threshold: Maximum distance for relevant results (None = no filtering)

    Returns:
        str: Generated answer with optional sources, or message if question is irrelevant
    """

    #We queried the database to find relevant information for the question
    query_results = query_database(question, collection_name, n_results, distance_threshold)
    chunks = query_results['chunks']
    sources = query_results['sources']
    is_relevant = query_results['is_relevant']

    # If the question is not relevant to our database, return a polite message
    if not is_relevant or len(chunks) == 0:
        return "I'm sorry, but I don't have information about that topic in my knowledge base. I'm specifically designed to answer questions about Ghana. Could you please ask me something related to Ghana?"

    #We built the context from retrieved chunks and sources
    context = build_context(chunks, sources)

    #We built the prompt without conversation history for clean RAG responses
    prompt = build_prompt(question, context, history="")

    #We generated the answer using our language model
    answer = llm_function(prompt)

    #We formatted the final response with or without sources based on the parameter
    if answer and include_sources:
        sources_text = format_sources(sources)
        final_response = answer + sources_text
    else:
        final_response = answer

    return final_response



def load_gemma_model(model_name):
    """
    Load the Gemma language model and tokenizer for text generation
    """
    
    print("Loading Gemma model. This may take a few minutes...")
    
    #We loaded the tokenizer for the specified model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
   
    #We loaded the model with optimized settings for performance
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        
        #We used float16 to reduce memory usage
        torch_dtype=torch.float16,  
        
        #We let the system automatically manage the device placement whether to use the CPU or GPU depending on availability
        device_map="auto"          
    )
    
    print("Model loaded successfully.")
    
    return tokenizer, model