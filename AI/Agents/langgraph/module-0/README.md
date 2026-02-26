# Module 0 — Basics (Setup & Foundations)

> **Notebook**: `basics.ipynb`

---

## What This Module Covers

This is the **getting-started** module. No LangGraph concepts yet — it's purely about setting up the environment and getting familiar with the building blocks you'll use throughout the course.

---

## Core Concepts

### 1. Why LangGraph Exists

- Building LLM agents that **reliably work in production** is hard — you often need more control than a simple chain gives you (e.g., force a tool call first, change prompts based on state).
- **LangGraph** (separate from LangChain) provides that control through **graph-based architectures** for agent and multi-agent workflows.

### 2. Chat Models — The Universal Interface

- LangChain provides a **provider-agnostic interface** for chat models — swap between OpenAI, Gemini, etc. without changing downstream code.
- Two key parameters: **`model`** (which model to use) and **`temperature`** (0 = deterministic, 1 = creative).
- Two main methods: **`invoke`** (full response) and **`stream`** (chunked response).

### 3. Messages

- Chat models work with **messages** — each has a **role** and **content**.
- `HumanMessage` = user input, `AIMessage` = model output.
- You can also pass a plain string — it auto-converts to a `HumanMessage`.

### 4. Search Tools (Tavily)

- [Tavily](https://tavily.com/) is a search engine **optimized for LLMs and RAG**.
- Used later in **Module 4** — this module just sets up the API key.

---

## Key Takeaways

1. **LangGraph ≠ LangChain** — LangGraph is a separate framework focused on precision & control for agent workflows.
2. The **chat model interface is provider-agnostic** — learn it once, use with any provider.
3. **Temperature** is the main knob: low = factual, high = creative.
4. **Messages** (`HumanMessage`, `AIMessage`) are the core I/O format for all chat models.

---

## Setup Checklist

- [ ] `OPENAI_API_KEY` — for GPT models
- [ ] `GEMINI_API_KEY` — for Google Gemini models
- [ ] `TAVILY_API_KEY` — for Tavily search (used in Module 4)
