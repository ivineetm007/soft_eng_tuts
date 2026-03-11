# Module 3 — Human-in-the-Loop

This module introduces **human-in-the-loop** patterns in LangGraph: streaming graph output in real time, pausing execution with breakpoints (static and dynamic), editing graph state with human feedback, and navigating execution history via time travel (replay & fork).

---

## Table of Contents

1. [Streaming](#1-streaming)
2. [Breakpoints](#2-breakpoints)
3. [Dynamic Breakpoints](#3-dynamic-breakpoints)
4. [Editing State & Human Feedback](#4-editing-state--human-feedback)
5. [Time Travel](#5-time-travel)
6. [Key Takeaways](#6-key-takeaways)
7. [Setup Checklist](#7-setup-checklist)

---

## 1. Streaming

> **Notebook:** `streaming-interruption.ipynb`

LangGraph has **first-class streaming support**, providing multiple ways to observe graph output as it's produced.

### Stream Modes for Graph State

Use `.stream` (sync) or `.astream` (async) to stream graph execution. Two primary modes:

| Mode | What it emits | Use case |
|---|---|---|
| `stream_mode="values"` | **Full state** after each node runs (first chunk = initial input) | When you need the complete state snapshot at each step |
| `stream_mode="updates"` | **Only the updates** (delta) from each node | When you only care about what changed |

#### Updates Mode

Each chunk is a `dict` with the **node name** as the key and the state update as the value:

```python
config = {"configurable": {"thread_id": "1"}}

for chunk in graph.stream(
    {"messages": [HumanMessage(content="hi! I'm Lance")]},
    config,
    stream_mode="updates",
):
    chunk['conversation']["messages"].pretty_print()
```

#### Values Mode

Emits the **full state** after each node — note that the **first chunk is the initial input**, before any node has run:

```python
for event in graph.stream(
    {"messages": [input_message]},
    config,
    stream_mode="values",
):
    for m in event['messages']:
        m.pretty_print()
```

### Streaming Tokens (LLM-level)

Beyond graph-level streaming, you can stream **individual tokens** as the LLM generates them using `.astream_events`:

```python
async for event in graph.astream_events(
    {"messages": [input_message]}, config, version="v2"
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="", flush=True)
```

Each event is a dict with key fields:

| Field | Description |
|---|---|
| `event` | Type of event (e.g., `on_chat_model_stream`) |
| `name` | Name of the component (e.g., `ChatOpenAI`) |
| `data` | Event payload — for token streaming, contains `AIMessageChunk` |
| `metadata` | Includes `langgraph_node` — the node that emitted the event |

Use `event['metadata']['langgraph_node']` to filter tokens from a specific node.

> **Note:** Streaming works by default with `ChatOpenAI` and most LangChain chat models. Only if you explicitly set `streaming=False` will tokens not stream.

---

## 2. Breakpoints

> **Notebook:** `breakpoints.ipynb`

Breakpoints **pause graph execution** at specified nodes, enabling human approval, inspection, and intervention.

### Why Human-in-the-Loop?

Three core motivations:
1. **Approval** — Interrupt the agent, surface state, and let the user accept or reject an action
2. **Debugging** — Rewind the graph to reproduce or avoid issues
3. **Editing** — Modify the graph state directly

### Setting Breakpoints

Breakpoints are set at **compile time** using `interrupt_before` or `interrupt_after`:

```python
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],   # Pause BEFORE the tools node runs
)
```

> **Important:** A checkpointer is **required** for breakpoints — it saves the state so execution can resume later.

### Execution Flow with a Breakpoint

```python
# Step 1: Run until breakpoint
initial_input = {"messages": "Multiply 2 and 3"}
thread = {"configurable": {"thread_id": "2"}}

for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Step 2: Inspect the paused state
state = graph.get_state(thread)
print(state.next)    # → ('tools',) — the next node that would run
```

### Resuming After a Breakpoint

Pass `None` as input to continue from the saved state:

```python
for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()
```

The graph picks up exactly where it left off, executing the pending node.

### Using Breakpoints with LangGraph API / Studio

Breakpoints also work via the LangGraph SDK, useful when running agents as deployed services:

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2024")
thread = await client.threads.create()

# Stream with remote breakpoint
async for chunk in client.runs.stream(
    thread["thread_id"],
    assistant_id="agent",
    input={"messages": [{"role": "user", "content": "Multiply 2 and 3"}]},
    stream_mode="values",
    interrupt_before=["tools"],
):
    # ...process chunks...
```

---

## 3. Dynamic Breakpoints

> **Notebook:** `dynamic-breakpoints.ipynb`

While static breakpoints are set at compile time, **dynamic breakpoints** let a node decide at runtime whether to interrupt — based on conditions evaluated during execution.

### `NodeInterrupt`

Use `NodeInterrupt` to conditionally halt execution from *inside* a node:

```python
from langgraph.errors import NodeInterrupt

def my_node(state: State):
    if len(state['input']) > 5:
        raise NodeInterrupt(
            f"Received input that is longer than 5 characters: {state['input']}"
        )
    return state
```

### Key Difference from Static Breakpoints

| Feature | Static Breakpoint | Dynamic Breakpoint (`NodeInterrupt`) |
|---|---|---|
| When defined | Compile time (`interrupt_before`/`interrupt_after`) | Runtime (inside a node function) |
| Conditional | No — always fires | Yes — based on any logic |
| Where it stops | Before/after a specific node | At the exact point the exception is raised |
| Resuming behavior | Resumes from saved state | Re-executes the node; if the same condition is met → interrupts again |

### Inspecting Interrupts

When a `NodeInterrupt` fires, the interrupt details are available in the state:

```python
state = graph.get_state(thread_config)
print(state.next)          # → ('my_node',)
print(state.tasks)         # Contains interrupt information
print(state.tasks[0].interrupts)  # The NodeInterrupt details
```

### Resuming with Updated State

If you resume without fixing the condition, the node will **re-interrupt**:

```python
# This will hit the same interrupt again!
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)
```

To proceed, **update the state** so the condition passes:

```python
graph.update_state(thread_config, {"input": "hi"})  # Now ≤ 5 chars

# Resume — node runs successfully this time
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)
```

---

## 4. Editing State & Human Feedback

> **Notebook:** `edit-state-human-feedback.ipynb`

### Editing Agent State at a Breakpoint

Breakpoints combined with `update_state` allow you to **modify the agent's state** before resuming. This is powerful for correcting, redirecting, or enriching the agent's behavior mid-execution.

#### Example: Changing a Tool Call

After pausing before the `tools` node, inspect and modify the last AI message:

```python
# Pause and inspect
state = graph.get_state(thread)
last_message = state.values["messages"][-1]

# The AI wanted to multiply 2 and 3 — change it to 3 and 3
last_message.tool_calls[0]["args"] = {"a": 3, "b": 3}

# Apply the edit
graph.update_state(thread, {"messages": last_message})

# Resume — now it multiplies 3 × 3 instead
for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()
```

> **Key insight:** The `add_messages` reducer uses message **ID** matching — updating a message with the same ID **overwrites** it rather than appending.

### Human Feedback Node Pattern

For structured human-in-the-loop, add a dedicated **feedback node** that serves as a placeholder for human input:

```python
# No-op node that we'll interrupt on
def human_feedback(state: MessagesState):
    pass

# Build graph with human feedback loop
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_feedback", human_feedback)

builder.add_edge(START, "human_feedback")
builder.add_edge("human_feedback", "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "human_feedback")

# Interrupt before the human feedback node
graph = builder.compile(
    interrupt_before=["human_feedback"],
    checkpointer=MemorySaver(),
)
```

### Graph Topology

```
START → human_feedback → assistant → [tools_condition] → END
              ↑                              ↓
              └──────── tools ←──────────────┘
```

The agent pauses before every `human_feedback` node, allowing the user to inject input.

### Injecting Human Feedback

Use `update_state` with `as_node` to update the state **as if** the `human_feedback` node produced the update:

```python
# Run until interrupt
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Get user input
user_input = input("Tell me how you want to update the state: ")

# Apply as the human_feedback node
graph.update_state(
    thread,
    {"messages": user_input},
    as_node="human_feedback",
)

# Resume execution
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
```

> The `as_node="human_feedback"` parameter tells LangGraph to treat this state update as if the `human_feedback` node produced it, preserving correct graph routing.

---

## 5. Time Travel

> **Notebook:** `time-travel.ipynb`

Time travel lets you **browse, replay, and fork** from any point in the graph's execution history. This is built on LangGraph's checkpoint system.

### Browsing History

Every step of execution is saved as a checkpoint. Use `get_state_history` to retrieve all past states:

```python
all_states = [s for s in graph.get_state_history(thread)]
len(all_states)  # e.g., 5 states for a 3-step execution + initial + empty
```

Each `StateSnapshot` includes:
- `values` — the state data at that checkpoint
- `next` — which node(s) would run next
- `config` — contains `thread_id` and `checkpoint_id`
- `metadata` — includes `source` and `step` number
- `tasks` — pending tasks at that checkpoint

### Replaying

To **replay** from a past state, pass its `config` back to `graph.stream`:

```python
to_replay = all_states[-2]  # Step 0: just the human input

# The graph re-plays from this checkpoint
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event['messages'][-1].pretty_print()
```

> **Replay = re-execute.** The graph recognizes the checkpoint exists and re-runs from that point. This means the LLM is called again, and results may differ (non-deterministic).

### Forking

**Forking** creates a new execution branch from a past state with **modified input**:

```python
to_fork = all_states[-2]  # The state with just the human message

# Overwrite the original message using its ID
fork_config = graph.update_state(
    to_fork.config,
    {"messages": [HumanMessage(
        content="Multiply 5 and 3",
        id=to_fork.values["messages"][0].id,  # Same ID = overwrite
    )]},
)

# Run the forked branch — this is a NEW execution
for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()
```

Key mechanics:
- `update_state` with a past `config` creates a **new checkpoint** (new `checkpoint_id`)
- The `next` metadata is preserved — the graph knows which node to run
- Passing the **same message ID** overwrites the message (via the `add_messages` reducer)
- The result is a **new branch** in the execution history, not a modification of the original

### Visual Summary

```
Original:    Input → Assistant → Tools → Assistant → END
                 ↑
Fork point ──────┘
                 ↓
Forked:      Modified Input → Assistant → Tools → Assistant → END
```

---

## 6. Key Takeaways

| Concept | Key Insight |
|---|---|
| **Streaming (values)** | Emits full state after each node; first chunk is the initial input |
| **Streaming (updates)** | Emits only deltas; each chunk keyed by node name |
| **Token streaming** | Use `astream_events` with `on_chat_model_stream` to get individual tokens |
| **Static breakpoints** | Set at compile time with `interrupt_before`/`interrupt_after`; requires a checkpointer |
| **Dynamic breakpoints** | `NodeInterrupt` inside a node for conditional pausing; re-interrupts if condition still holds |
| **State editing** | `update_state` modifies state at a breakpoint; uses `add_messages` ID matching for message overwrites |
| **Human feedback node** | No-op node + `interrupt_before` + `update_state(as_node=...)` for structured human input |
| **Replay** | Pass a past checkpoint's `config` to `stream(None, config)` to re-execute from that point |
| **Fork** | `update_state` on a past checkpoint with modified data creates a new branch with a new `checkpoint_id` |

---

## 7. Setup Checklist

```bash
# Required environment variables
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export LANGSMITH_API_KEY="your-langsmith-key"

# LangSmith tracing config
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=langchain-academy
```

**Packages:**
```bash
pip install langchain_core langgraph langchain_openai langchain_google_genai langgraph_sdk langgraph-prebuilt
```
