
'''
This was our memory management system for chat and RAG interactions that we designed for our Ghana chatbot.
We built this system to handle conversation history efficiently by automatically summarizing old conversations using either BART or Gemma models.
This allowed our chatbot to maintain context from previous interactions without running into token limits.

The system supported separate memory stores for chat mode and RAG mode, and automatically compressed memory when token thresholds were exceeded.
We implemented chunking strategies to handle long conversations and recursive summarization to keep memory usage optimal.
'''



#All Imports

from transformers import pipeline
from typing import Dict, List, Optional
import tiktoken



#Memory Configuration - These settings controlled how our memory system operated
MEMORY_CONFIG = {
    
    #We provided the option to choose either "bart" or "gemma" as the summarization model
    "summarizer": "bart",
    
    #We set this threshold of tokens that triggered the summarization process to happen
    "token_threshold": 2000,
    
    #We configured the number of most recent conversations to keep in full detail
    "recent_turns_keep": 3,
    "summary_max_tokens": 150,
    "enable_summarization": True,
    
}


#Global Model Variables that we used to store our loaded models
BART_SUMMARIZER = None

GEMMA_MODEL = None

#Memory Structures: We created separate memory stores for different interaction modes
chat_memory = {
    "summary": "",
    "recent_turns": [],
    "total_tokens": 0,
}

rag_memory = {
    "summary": "",
    "recent_turns": [],
    "total_tokens": 0,
}


def count_tokens(text):
    """
    This function counts the number of tokens in a text string using tiktoken encoding
    """
    
    try:
        #We used the cl100k_base encoding which worked well for our purposes
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    
    except Exception as e:
        
        #We implemented this fallback approximation if tiktoken failed, using a rate of 4 characters per token
        print(f"Warning: tiktoken failed, using approximation: {e}")
        return len(text) // 4


def init_bart_summarizer():
    """
    Initializing the BART summarization model that we used as our primary summarizer
    """
    global BART_SUMMARIZER

    #We checked if BART was already initialized to avoid reloading
    if BART_SUMMARIZER is not None:
        return BART_SUMMARIZER

    try:
        #We loaded the BART model with specific configuration for summarization
        BART_SUMMARIZER = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            #We set device to -1 (CPU) by default, but you could change this to 0 if you have a GPU
            device=-1
        )
        
        return BART_SUMMARIZER
    
    except Exception as e:
        print(f"Unfortunately we could not load BART model: {e}")
        print("We are falling back to Gemma summarization")
        
        #We automatically switched to Gemma if BART failed to load
        MEMORY_CONFIG["summarizer"] = "gemma"
        return None


def set_gemma_model(model):
    """
    Set reference to Gemma model for summarization fallback when BART failed
    """
    global GEMMA_MODEL
    GEMMA_MODEL = model


def summarize_with_bart(text):
    """
    Summarize text using the BART model with chunking strategy for long texts
    
    Since BART had a maximum input of approximately 1024 tokens, or 4000-4500 chars, 
    we implemented chunking when text was too long and used recursive summarization.
    
    """
    global BART_SUMMARIZER

    #We initialized BART if it wasn't already loaded
    if BART_SUMMARIZER is None:
        BART_SUMMARIZER = init_bart_summarizer()
        if BART_SUMMARIZER is None:
            return summarize_with_gemma(text)

    try:
        #We set the maximum character limit based on BART's token constraints
        MAX_CHARS = 4000

        if len(text) <= MAX_CHARS:
            #If the text fit within limits, we summarized it directly
            summary = BART_SUMMARIZER(
                text,
                max_length=100,
                min_length=30,
                do_sample=False
            )
            return summary[0]['summary_text']

        else:
            #When the text was too long, we chunked and summarized in pieces
            chunks = []
            
            remaining = text

            while len(remaining) > MAX_CHARS:
                #We took chunks from the end to preserve context flow
                chunk = remaining[-MAX_CHARS:]
                
                chunks.insert(0, chunk) 
                
                remaining = remaining[:-MAX_CHARS]

            if remaining:
                chunks.insert(0, remaining)

            #We summarized each chunk separately
            summaries = []
            for i, chunk in enumerate(chunks):
                
                try:
                    result = BART_SUMMARIZER(
                        chunk,
                        max_length=80,
                        min_length=20,
                        do_sample=False
                    )
                    
                    summaries.append(result[0]['summary_text'])
                    
                except Exception as e:
                    print(f"There was an error while trying to summarize chunk {i+1}: {e}")
                    
                    continue

            if len(summaries) == 0:
                return ""
            
            elif len(summaries) == 1:
                return summaries[0]
            
            else:
                #When we had multiple chunk summaries, we combined and recursively summarized again
                combined = " ".join(summaries)

                return summarize_with_bart(combined)

    except Exception as e:
        
        print(f"The BART summarization failed: {e}")
        return summarize_with_gemma(text)


def summarize_with_gemma(text):
    """
    Summarize text using Gemma 2B model with chunking design that supported our memory system as a fallback option.
    """

    global GEMMA_MODEL

    #We checked if Gemma model was available
    if GEMMA_MODEL is None:
        print("Warning: Gemma model not set, cannot summarize")
        return ""

    try:
        #We set character limits appropriate for Gemma's context window
        MAX_CHARS = 3000

        if len(text) <= MAX_CHARS:
            
            #We constructed a clear prompt for summarization
            prompt = f"""Summarize this conversation concisely in 2-3 sentences, capturing the key points:

{text}

Summary:"""

            #We generated the summary with controlled parameters
            output = GEMMA_MODEL(
                prompt,
                max_tokens=150,
                temperature=0.3,
                stop=["\n\n", "User:", "Question:"],
                echo=False
            )

            return output['choices'][0]['text'].strip()

        else:
            #When text was too long, we chunked and summarized in pieces
            chunks = []
            remaining = text

            while len(remaining) > MAX_CHARS:
                chunk = remaining[-MAX_CHARS:]
                chunks.insert(0, chunk)
                remaining = remaining[:-MAX_CHARS]

            if remaining:
                chunks.insert(0, remaining)

            #We processed each chunk separately
            summaries = []
            for i, chunk in enumerate(chunks):
                try:
                    prompt = f"""Summarize this conversation concisely in 2-3 sentences, capturing the key points:

{chunk}

Summary:"""

                    output = GEMMA_MODEL(
                        prompt,
                        max_tokens=100,
                        temperature=0.3,
                        stop=["\n\n", "User:", "Question:"],
                        echo=False
                    )

                    summaries.append(output['choices'][0]['text'].strip())

                except Exception as e:
                    print(f"There was an error while trying to summarize chunk {i+1} with Gemma: {e}")
                    continue

            if len(summaries) == 0:
                return ""

            elif len(summaries) == 1:
                return summaries[0]

            else:
                #When we had multiple summaries, we combined and recursively summarized again
                combined = " ".join(summaries)
                return summarize_with_gemma(combined)

    except Exception as e:
        print(f"Gemma summarization failed: {e}")
        return ""


def summarize_text(text):
    """
    General function for summarization that picked the right model based on our configuration
    
    """

    if MEMORY_CONFIG["summarizer"] == "bart":
        return summarize_with_bart(text)
    else:
        return summarize_with_gemma(text)


def format_turns_for_summary(turns):
    """
    This function formats past conversation turns for summarization in a readable format
    """
    text = ""
    
    for turn in turns:
        
        text += f"User: {turn['user']}\n"
        
        text += f"Kiki: {turn['model']}\n\n"
        
    return text.strip()


def compress_memory(memory):
    """
    This function was called when memory exceeded the token threshold.
    We designed it to keep the most recent conversations in full detail and summarize older ones.
    """

    #We first checked if summarization was enabled in the configuration
    if not MEMORY_CONFIG["enable_summarization"]:
        
        keep = MEMORY_CONFIG["recent_turns_keep"]
        memory["recent_turns"] = memory["recent_turns"][-keep:]

        #We recalculated the total token count for the remaining turns
        memory["total_tokens"] = sum(
            count_tokens(t['user'] + t['model'])
            for t in memory["recent_turns"]
        )

        #If there was an existing summary, we added its tokens to the total
        if memory["summary"]:
            memory["total_tokens"] += count_tokens(memory["summary"])
        return


    #When summarization was enabled, we summarized old turns instead of dropping them
    #We determined how many recent turns to keep in full detail
    keep = MEMORY_CONFIG["recent_turns_keep"]

    #We split the turns: old turns were summarized, recent turns kept as-is
    turns_to_summarize = memory["recent_turns"][:-keep]  
    
    memory["recent_turns"] = memory["recent_turns"][-keep:]  

    #If there were no old turns to summarize, we were done
    if not turns_to_summarize:
        return

    #We formatted the old turns into readable text format and generated a summary
    text_to_summarize = format_turns_for_summary(turns_to_summarize)
    new_summary = summarize_text(text_to_summarize)

    #We handled the case where we already had a summary from previous compressions
    if memory["summary"]:
        #We combined the old summary with the new summary
        combined = f"{memory['summary']} {new_summary}"

        #If the combined summary was getting too long (>300 tokens), we summarized it again
        #This prevented the summary itself from growing indefinitely
        if count_tokens(combined) > 300:
            memory["summary"] = summarize_text(combined)
        else:
            memory["summary"] = combined
            
    else:
        #When there was no existing summary, we just used the new one
        memory["summary"] = new_summary

    #We recalculated the total token count after compression
    #We started with the summary tokens
    memory["total_tokens"] = count_tokens(memory["summary"])

    #We added the tokens from all remaining recent turns
    for turn in memory["recent_turns"]:
        memory["total_tokens"] += count_tokens(turn['user'] + turn['model'])


def add_to_memory(user_question, model_answer, mode="chat"):
    """
    This was the main function for adding interactions to our memory system.
    We designed it to automatically trigger compression when memory exceeded the token threshold.
    
    """

    #We selected the appropriate memory storage based on mode because we had separate stores for RAG and chat
    memory = rag_memory if mode == "rag" else chat_memory

    #We created a turn object containing both the user's question and model's answer
    turn = {
        "user": user_question,
        "model": model_answer
    }

    #We added this turn to the list of recent turns in memory
    memory["recent_turns"].append(turn)

    #We calculated how many tokens this new turn contained
    turn_tokens = count_tokens(user_question + model_answer)

    #We updated the total token count in memory
    memory["total_tokens"] += turn_tokens

    #We checked if the total tokens exceeded the configured threshold
    threshold = MEMORY_CONFIG["token_threshold"]
    
    if memory["total_tokens"] > threshold:
        
        #When memory got too large, we triggered compression
        compress_memory(memory)


def get_memory_text(mode: str = "chat") -> str:
    """
    This function formatted memory into a readable string that provided context
    from previous conversations. We designed it to include both the summary of old conversations
    and the full text of recent conversations.
    """
    #We selected the appropriate memory storage based on mode
    memory = rag_memory if mode == "rag" else chat_memory

    
    if not memory["recent_turns"] and not memory["summary"]:
        return ""

    #We started building the memory text with a clear header
    text = "Previous conversation:\n\n"

    #We included the summary of older conversations if it existed
    if memory["summary"]:
        text += f"Earlier context: {memory['summary']}\n\n"

    #We included the full text of recent conversations
    if memory["recent_turns"]:
        text += "Recent messages:\n"
        for turn in memory["recent_turns"]:
            
            #We formatted each turn as a User/Kiki exchange
            text += f"User: {turn['user']}\n"
            text += f"Kiki: {turn['model']}\n\n"

    return text


def clear_memory(mode: Optional[str] = None):
    """
    This function reset the memory by removing all stored conversations,
    summaries, and resetting token counts. We made it useful for starting new topics
    or when you wanted to remove all conversation history.

    """
    if mode == "chat":
        #We cleared only the chat memory
        chat_memory["summary"] = ""
        chat_memory["recent_turns"] = []
        chat_memory["total_tokens"] = 0
    elif mode == "rag":
        #We cleared only the RAG memory
        rag_memory["summary"] = ""
        rag_memory["recent_turns"] = []
        rag_memory["total_tokens"] = 0
    else:
        #When no specific mode was provided, we cleared both chat and RAG memory
        chat_memory["summary"] = ""
        chat_memory["recent_turns"] = []
        chat_memory["total_tokens"] = 0
        rag_memory["summary"] = ""
        rag_memory["recent_turns"] = []
        rag_memory["total_tokens"] = 0



