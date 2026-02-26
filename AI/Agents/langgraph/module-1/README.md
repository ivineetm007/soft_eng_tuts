# Module 1 — Introduction (Building Your First Agents)

> **Notebooks**: `simple-graph.ipynb` · `chain.ipynb` · `router.ipynb` · `agent.ipynb` · `agent-memory.ipynb` · `deployment.ipynb`

---

## What This Module Covers

This module progressively builds up from a **bare-bones graph** to a **deployed, memory-aware ReAct agent**. Each notebook adds one new concept on top of the previous one, so they should be studied in order.

| # | Notebook | Key Idea |
|---|----------|----------|
| 1 | `simple-graph` | Nodes, edges, conditional edges, graph state |
| 2 | `chain` | Messages as state, chat models, tool calls inside nodes |
| 3 | `router` | LLM decides: call a tool **or** respond directly |
| 4 | `agent` | ReAct loop — tool calls fed back to the model |
| 5 | `agent-memory` | Checkpointer adds multi-turn memory |
| 6 | `deployment` | Local Studio testing & LangSmith cloud deployment |

---

## Core Concepts

### 1. Simple Graph (`simple-graph.ipynb`)

Build, compile, and run a `StateGraph`:

- **State** — a `TypedDict` shared between all nodes (e.g., `graph_state: str`).
- **Nodes** — Python functions that receive the current state and return an update.
- **Edges** — fixed connections between nodes (`add_edge`).
- **Conditional edges** — a function inspects the state and returns the name of the next node (`add_conditional_edges`). Uses `random.choice` in the demo to pick one of two paths.
- **Special nodes** — `START` (entry point) and `END` (terminal node).

```python
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
graph = builder.compile()
graph.invoke({"graph_state": "Hi"})
```

### 2. Chain — Messages & Tools (`chain.ipynb`)

Upgrades the state to a **list of chat messages**:

- **`MessagesState`** — a pre-built state with a `messages` key and the `add_messages` reducer that appends instead of overwriting.
- **Chat model + `bind_tools`** — the LLM is told about available Python functions (e.g., `multiply`, `add`) and can emit `tool_calls` in its response.
- **Tool node** — a second node in the graph that executes the tool call and appends a `ToolMessage` with the result.

> **Why reducers matter:** Without `add_messages`, each node would overwrite the state. The reducer _appends_ new messages, preserving the full conversation history.

Message flow: `HumanMessage → AIMessage (with tool_call) → ToolMessage (result)`

### 3. Router (`router.ipynb`)

The LLM becomes a **decision maker**:

- If the user question requires a tool → route to `ToolNode`.
- If not → route straight to `END` (direct answer).

Key building blocks:

| Component | Purpose |
|-----------|---------|
| `ToolNode([...])` | Pre-built node that executes a list of tools |
| `tools_condition` | Pre-built conditional edge that checks for `tool_calls` in the last `AIMessage` |

```python
builder.add_conditional_edges("tool_calling_llm", tools_condition)
```

### 4. Agent — The ReAct Loop (`agent.ipynb`)

Turns the one-shot router into a **loop**:

- After the `ToolNode` runs, the result feeds **back** to the LLM node.
- The LLM can then reason about the result and either make another tool call or produce a final answer.
- This is the **ReAct** pattern: **Reason → Act → Observe → repeat**.

```
           ┌──────────────┐
   START──▶│ tool_calling  │◀─────────────┐
           │    _llm       │              │
           └──────┬───────┘              │
            has tool_call?               │
           ┌──yes──┴──no──┐              │
           ▼              ▼              │
       ┌───────┐      ┌─────┐           │
       │ tools │──────▶      │           │
       └───────┘      │ END │           │
                      └─────┘           │
```

- **LangSmith tracing** — set `LANGSMITH_TRACING=true` and `LANGSMITH_PROJECT=langchain-academy` to get full execution traces.

### 5. Agent Memory (`agent-memory.ipynb`)

Add **persistence** so the agent remembers previous turns:

- **`MemorySaver`** — an in-memory checkpointer that saves the graph state after every step.
- **`thread_id`** — passed via `config`, groups related messages into a conversation thread.
- Same `thread_id` → conversation continues; new `thread_id` → fresh conversation.

```python
memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

# Invoke with a thread
config = {"configurable": {"thread_id": "1"}}
react_graph_memory.invoke({"messages": [("user", "Hi")]}, config)
```

### 6. Deployment (`deployment.ipynb`)

Take the agent from a notebook to a **running service**:

| Term | What it means |
|------|---------------|
| **LangGraph API** | Bundles your graph into a server with built-in persistence, threads & async task management |
| **LangGraph Cloud** | Hosted deployment inside LangSmith |
| **LangGraph Studio** | Visual IDE for testing & debugging your graph locally |
| **LangGraph SDK** | Python/JS client to interact with your deployed agent |

**Local workflow**:

1. Create a `langgraph.json` config pointing at your graph & dependencies.
2. Run `langgraph dev` to spin up Studio locally.
3. Use the SDK to create threads & stream runs.

**Cloud workflow**:

1. Push code to a GitHub repo.
2. In LangSmith → **Deployments → + New Deployment** → connect the repo.
3. Set `OPENAI_API_KEY` as an environment secret.
4. SDK works the same — just swap the URL to the cloud endpoint.

```python
from langgraph_sdk import get_client
client = get_client(url="http://localhost:56091")  # local
# client = get_client(url=<deployment-url>)        # cloud

thread = await client.threads.create()
async for chunk in client.runs.stream(
    thread["thread_id"], "agent",
    input={"messages": [{"role": "user", "content": "What is 2+2?"}]},
    stream_mode="values",
):
    print(chunk.data)
```

---

## Key Takeaways

1. **LangGraph is incremental** — simple graph → chain → router → agent. Each layer adds one new concept.
2. **`MessagesState` + `add_messages` reducer** is the idiomatic way to track conversations.
3. **`ToolNode` + `tools_condition`** handle tool integration with zero boilerplate.
4. **ReAct agent = router + feedback loop** — route tool results back to the LLM until it's done.
5. **`MemorySaver` + `thread_id`** gives you multi-turn memory with a single line of code.
6. **Deployment** is config-driven — `langgraph.json` covers local & cloud.

---

## Setup Checklist

- [ ] `OPENAI_API_KEY` — required for GPT models
- [ ] `LANGSMITH_API_KEY` — required for tracing & deployments
- [ ] `LANGSMITH_TRACING=true` — enable trace logging
- [ ] `LANGSMITH_PROJECT=langchain-academy` — group traces under one project
