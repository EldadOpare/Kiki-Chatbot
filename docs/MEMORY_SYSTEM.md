# Memory Summarization System

## Overview

The new memory system automatically summarizes conversation history when it exceeds a token threshold, allowing for much longer conversations without losing context.

## Features

- ✅ **Automatic summarization** when memory exceeds token threshold
- ✅ **Dual implementation**: BART (fast) and Gemma 2B (fallback)
- ✅ **Token-based tracking** instead of turn count
- ✅ **Sliding window**: Keeps recent turns in full, summarizes older ones
- ✅ **Separate memories**: Independent chat and RAG mode histories
- ✅ **Configurable**: Adjust threshold, summarizer, retention, etc.
- ✅ **REST API**: Control and monitor via HTTP endpoints

## How It Works

```
┌─────────────────────────────────────────────┐
│         Memory Structure                     │
├─────────────────────────────────────────────┤
│  Summary: "Earlier context..."              │ ← Compressed old turns
│                                              │
│  Recent Turns (kept in full):               │
│    - Turn N-2                                │
│    - Turn N-1                                │
│    - Turn N (current)                        │ ← Last 3 turns
│                                              │
│  Total: 1,200 tokens                         │
└─────────────────────────────────────────────┘

When memory > threshold (e.g., 2000 tokens):
1. Take oldest 50% of turns
2. Summarize them with BART or Gemma
3. Append to existing summary
4. Keep recent 3 turns in full
```

## Configuration

### Default Settings

```python
MEMORY_CONFIG = {
    "summarizer": "bart",          # "bart" or "gemma"
    "token_threshold": 2000,       # Trigger at 2000 tokens
    "recent_turns_keep": 3,        # Keep 3 recent turns
    "summary_max_tokens": 150,     # Max tokens for summary
    "enable_summarization": True,  # Master switch
}
```

### Change Settings

**In Python:**
```python
from memory_system import configure_memory

configure_memory(
    summarizer="gemma",        # Switch to Gemma
    token_threshold=3000,      # Raise threshold
    recent_turns_keep=5        # Keep more recent turns
)
```

**Via API:**
```bash
curl -X POST http://localhost:5081/api/memory/configure \
  -H "Content-Type: application/json" \
  -d '{"summarizer": "bart", "token_threshold": 2000}'
```

## Usage

### In Your Code

```python
from memory_system import (
    add_to_memory,
    get_memory_text,
    clear_memory,
    get_memory_stats
)

# Add conversation turn
add_to_memory(
    user_question="What is Ghana?",
    model_answer="Ghana is a country in West Africa...",
    mode="chat"  # or "rag"
)

# Get formatted history for prompts
history = get_memory_text(mode="chat")
prompt = f"{history}\n\nUser: {question}\nKiki:"

# Check memory stats
stats = get_memory_stats(mode="chat")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Has summary: {stats['has_summary']}")

# Clear memory
clear_memory(mode="chat")  # or "rag" or None for both
```

### Via API

**Get Memory Stats:**
```bash
# Get stats for both modes
curl http://localhost:5081/api/memory/stats

# Get stats for specific mode
curl http://localhost:5081/api/memory/stats?mode=chat
```

**Configure Memory:**
```bash
curl -X POST http://localhost:5081/api/memory/configure \
  -H "Content-Type: application/json" \
  -d '{
    "token_threshold": 3000,
    "recent_turns_keep": 5,
    "summarizer": "bart"
  }'
```

## BART vs Gemma Summarization

### BART (Default)
- **Speed**: ⚡ 2-3 seconds per summary
- **Quality**: Excellent, purpose-built
- **RAM**: +1.6GB
- **Best for**: Production, frequent summaries

### Gemma 2B (Fallback)
- **Speed**: 🐌 5-10 seconds per summary
- **Quality**: Good, consistent voice
- **RAM**: No extra (uses main model)
- **Best for**: RAM-constrained systems

## Token Counting

Uses simple approximation: **1 token ≈ 4 characters**

For more accuracy, install `tiktoken`:
```bash
pip install tiktoken
```

Then update [`memory_system.py:40`](../python/memory_system.py#L40):
```python
import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))
```

## Example Output

### Before Summarization (3 turns, 210 tokens)
```
Previous conversation:

Recent messages:
User: What is Ghana's history?
Kiki: Ghana was home to several powerful kingdoms...

User: Tell me about the culture.
Kiki: Ghanaian culture is incredibly diverse...

User: What languages are spoken?
Kiki: English is the official language...
```

### After Summarization (5 turns, 277 tokens)
```
Previous conversation:

Earlier context: Ghana was home to several powerful kingdoms
including the Ghana Empire. It became the first sub-Saharan
African nation to gain independence. Ghanaian culture is diverse
and vibrant. English is the official language, with 80+ indigenous
languages spoken.

Recent messages:
User: What is the geography like?
Kiki: Ghana features diverse geography including rainforests...

User: Tell me about the government.
Kiki: Ghana is a democratic republic with a multi-party system...
```

## Testing

Run the test script:
```bash
cd python
python3 test_memory.py
```

This tests:
1. Basic memory addition
2. Automatic summarization
3. Separate chat/RAG modes
4. Configuration options

## Troubleshooting

### BART not loading
- **Symptom**: Falls back to Gemma
- **Solution**: Ensure transformers installed: `pip install transformers torch`

### Memory not summarizing
- **Check**: `MEMORY_CONFIG['enable_summarization']` is True
- **Check**: Token count exceeds threshold
- **Debug**: Use `get_memory_stats()` to view current tokens

### Summaries too long/short
- **Adjust**: `configure_memory(summary_max_tokens=200)`

### Running out of RAM
- **Switch to Gemma**: `configure_memory(summarizer="gemma")`
- **Raise threshold**: `configure_memory(token_threshold=5000)`

## Performance

| Operation | BART | Gemma |
|-----------|------|-------|
| Summarize 500 tokens | 2-3s | 5-10s |
| RAM overhead | +1.6GB | 0GB |
| Quality | Excellent | Good |
| Blocking | No | Yes* |

*Gemma blocks other requests during summarization

## Migration from Old System

The old system is still supported via compatibility functions:

```python
# Old way (still works)
from model_utilities import add_to_history, get_history_text, clear_history

# New way (recommended)
from memory_system import add_to_memory, get_memory_text, clear_memory
```

Both use the same backend, so they're interchangeable.

## Future Improvements

Potential enhancements:
- [ ] Persistent storage (save to disk)
- [ ] Per-user memory (multi-user support)
- [ ] Semantic compression (keep important turns)
- [ ] Progressive summarization (tier system)
- [ ] Custom summarization prompts

## Credits

Built for Kiki RAG Chatbot using:
- [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) for summarization
- [Gemma 2B](https://ai.google.dev/gemma) as fallback
- ChromaDB for vector storage
