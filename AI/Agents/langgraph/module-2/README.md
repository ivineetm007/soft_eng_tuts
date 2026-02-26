# Module 2 — State & Memory

This module dives deep into **state management** in LangGraph: how to define state schemas, control updates with reducers, work with multiple schemas, manage long conversations through trimming/filtering/summarization, and persist memory with external databases.

---

## Table of Contents

1. [State Schema](#1-state-schema)
2. [State Reducers](#2-state-reducers)
3. [Multiple Schemas](#3-multiple-schemas)
4. [Trim & Filter Messages](#4-trim--filter-messages)
5. [Chatbot with Summarization](#5-chatbot-with-summarization)
6. [Chatbot with External Memory](#6-chatbot-with-external-memory)
7. [Key Takeaways](#7-key-takeaways)
8. [Setup Checklist](#8-setup-checklist)

---

## 1. State Schema

> **Notebook:** `state-schema.ipynb`

LangGraph state can be defined using three approaches, each with different trade-offs:

### TypedDict (default)

The simplest option — a Python `TypedDict` serves as a lightweight schema with no runtime validation.

```python
from typing_extensions import TypedDict

class TypedDictState(TypedDict):
    name: str
    mood: str
```

### Dataclass

Standard Python `dataclass` — provides a structured schema with attribute access but still **no runtime validation**.

```python
from dataclasses import dataclass

@dataclass
class DataclassState:
    name: str
    mood: str
```

### Pydantic BaseModel ⭐

The most robust option — adds **runtime type validation**, meaning invalid data will raise a `ValidationError` immediately.

```python
from pydantic import BaseModel, field_validator

class PydanticState(BaseModel):
    name: str
    mood: str

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, value):
        if value not in ["happy", "sad"]:
            raise ValueError("Each mood must be either 'happy' or 'sad'")
        return value
```

> **Tip:** Use `TypedDict` for quick prototyping, `Pydantic` when you need guaranteed data integrity at runtime.

---

## 2. State Reducers

> **Notebook:** `state-reducers.ipynb`

### The Problem: Default Overwrite Behavior

By default, each node's return value **overwrites** the corresponding state key. This breaks when parallel (branching) nodes try to update the same key — only the last write wins.

### Solution: Reducers via `Annotated`

A **reducer** is a function that defines *how* to combine old and new values for a state key.

```python
from typing import Annotated
from operator import add

class State(TypedDict):
    foo: Annotated[list, add]  # Lists are concatenated, not overwritten
```

With `operator.add`, lists from parallel branches are **concatenated** instead of one overwriting the other.

### Custom Reducers

For more complex logic, write your own reducer function:

```python
def reduce_list(left: list | None, right: list | None) -> list:
    if not left:
        left = []
    if not right:
        right = []
    return left + right

class DefaultState(TypedDict):
    foo: Annotated[list, reduce_list]
```

This handles `None` defaults gracefully — important because state keys start as `None` before their first write.

### The `add_messages` Reducer

The built-in `add_messages` reducer intelligently handles message lists:

- **Appends** new messages to the existing list
- **Overwrites** an existing message if the new message has the **same `id`** (useful for editing)
- **Removes** messages when passed `RemoveMessage` objects targeting specific IDs

```python
from langchain_core.messages import RemoveMessage

# Remove specific messages by ID
delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
add_messages(messages, delete_messages)
```

---

## 3. Multiple Schemas

> **Notebook:** `multiple-schemas.ipynb`

### Private State Between Nodes

Nodes can pass **private data** to each other without exposing it in the graph's overall state. Define a key that's only written and read by specific nodes:

```python
class OverallState(TypedDict):
    foo: int

class PrivateState(TypedDict):
    baz: int  # Only exists between node_2 and node_3
```

Wire private state by specifying node types and inter-node edges carefully.

### Input & Output Schema Filtering

You can define **separate schemas** for the graph's input, internal state, and output. This controls what data users can send in and what they receive back:

```python
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(TypedDict):
    question: str
    answer: str
    notes: str  # Internal only — not exposed to input or output

graph = StateGraph(OverallState, input=InputState, output=OutputState)
```

- **InputState** restricts what the graph accepts
- **OutputState** filters what the graph returns
- The full **OverallState** is used internally

---

## 4. Trim & Filter Messages

> **Notebook:** `trim-filter-messages.ipynb`

Long conversations grow the message list, increasing token usage and latency. Three strategies to manage this:

### Strategy 1: Remove with `RemoveMessage` (Modifies State)

Add a dedicated **filter node** to the graph that removes old messages from state:

```python
def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}
```

The graph runs `filter → chat_model`, so the model always sees a pruned history. The state is **permanently modified**.

### Strategy 2: Filter In-Place (State Unchanged)

Pass a **subset** of messages to the model without changing state:

```python
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}
```

The full history stays in state, but the model only sees the last message. Useful when you want the full record but don't want to pay for it at inference time.

### Strategy 3: `trim_messages` (Token-Based)

Use LangChain's `trim_messages` utility to cap messages by **token count**:

```python
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    state["messages"],
    max_tokens=100,
    strategy="last",
    token_counter=ChatOpenAI(model="gpt-4o"),
    allow_partial=False,
)
```

| Parameter | Purpose |
|---|---|
| `max_tokens` | Maximum number of tokens to keep |
| `strategy` | `"last"` keeps the most recent messages |
| `token_counter` | Model instance used to count tokens |
| `allow_partial` | If `False`, drops entire messages rather than truncating |

---

## 5. Chatbot with Summarization

> **Notebook:** `chatbot-summarization.ipynb`

### Architecture

Rather than blindly trimming messages, use the LLM to produce a **running summary** of the conversation. This retains a compressed representation of the full history.

```
START → conversation → [should_continue] → END
                              ↓
                   summarize_conversation → END
```

### Extended State

Add a `summary` key to `MessagesState`:

```python
class State(MessagesState):
    summary: str
```

### Key Nodes

**`call_model`** — Injects any existing summary as a `SystemMessage` before invoking the LLM:

```python
def call_model(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": response}
```

**`summarize_conversation`** — Generates a new/extended summary and removes old messages:

```python
def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Keep only the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}
```

### Conditional Routing

Summarization triggers when the conversation exceeds a threshold (e.g., 6 messages):

```python
def should_continue(state: State) -> Literal["summarize_conversation", END]:
    if len(state["messages"]) > 6:
        return "summarize_conversation"
    return END
```

### Adding Memory

Compile with `MemorySaver` to persist across turns within the same thread:

```python
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Use thread-based config for multi-turn conversations
config = {"configurable": {"thread_id": "1"}}
```

---

## 6. Chatbot with External Memory

> **Notebook:** `chatbot-external-memory.ipynb`

### Why External Memory?

`MemorySaver` stores state in-memory — it's lost when the process restarts. For **persistent** memory across sessions, use a database-backed checkpointer.

### SQLite Checkpointer

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# In-memory SQLite (still non-persistent, but faster)
conn = sqlite3.connect(":memory:", check_same_thread=False)

# File-based SQLite (persistent across restarts)
conn = sqlite3.connect("state_db/example.db", check_same_thread=False)

memory = SqliteSaver(conn)
graph = workflow.compile(checkpointer=memory)
```

The SQLite database creates two tables:
- **`checkpoints`** — stores serialized graph state at each step (`thread_id`, `checkpoint_id`, `checkpoint` blob, `metadata`)
- **`writes`** — stores individual channel writes (`thread_id`, `checkpoint_id`, `task_id`, `channel`, `value`)

### Other Checkpointers

LangGraph also supports **Postgres** and other databases for production-grade persistence.

### LangGraph Studio Integration

Run the chatbot locally with LangGraph's development server:

```bash
langgraph dev
```

This provides:
- **API** at `http://127.0.0.1:2024`
- **Studio UI** at `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`
- **API Docs** at `http://127.0.0.1:2024/docs`

---

## 7. Key Takeaways

| Concept | Key Insight |
|---|---|
| **State schema** | `TypedDict` for speed, `Pydantic` for safety — choose based on your validation needs |
| **Reducers** | Essential for parallel branches; `operator.add` for lists, `add_messages` for message handling |
| **`add_messages`** | Supports append, overwrite-by-ID, and delete via `RemoveMessage` |
| **Multiple schemas** | Use `input`/`output` schemas on `StateGraph` to control what enters and leaves the graph |
| **Message management** | Three strategies — remove from state, filter at inference, or token-based trimming |
| **Summarization** | Compress conversation history into a running summary to maintain context without growing token costs |
| **External memory** | `SqliteSaver` for persistent state; swappable with Postgres for production |

---

## 8. Setup Checklist

```bash
# Required environment variables
export OPENAI_API_KEY="your-openai-key"
export LANGSMITH_API_KEY="your-langsmith-key"

# LangSmith tracing config
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=langchain-academy
```

**Packages:**
```bash
pip install langchain_core langgraph langchain_openai langgraph-checkpoint-sqlite
```
