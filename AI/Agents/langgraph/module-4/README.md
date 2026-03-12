# Module 4 — Multi-Agent Communication & Research Assistant

This module covers advanced **LangGraph controllability** patterns — parallelization, sub-graphs, and map-reduce — and culminates in a full **multi-agent research assistant** that ties them all together.

---

## 📂 Notebooks

| #   | Notebook                   | Topic                         | Key Concepts                                                 |
| --- | -------------------------- | ----------------------------- | ------------------------------------------------------------ |
| 1   | `parallelization.ipynb`    | Parallel node execution       | Fan-out / fan-in, reducers, parallel LLM calls               |
| 2   | `sub-graph.ipynb`          | Sub-graphs                    | Isolated state, input/output schemas, composing sub-graphs   |
| 3   | `map-reduce.ipynb`         | Map-Reduce with `Send()`      | Dynamic parallelism, `Send()` API, collecting results        |
| 4   | `research-assistant.ipynb` | Capstone — Research Assistant | Human-in-the-loop, multi-agent interviews, report generation |

---

## 1. Parallelization (`parallelization.ipynb`)

### What it covers

- **Fan-out / Fan-in**: Running multiple nodes concurrently from a single parent, then joining results at a downstream node.
- **Reducers** (`operator.add`, custom sorting reducers): Required when parallel branches write to the **same state key**; without a reducer, LangGraph raises an `InvalidUpdateError`.
- **Waiting for nodes**: When parallel branches have unequal lengths (e.g., `b → b2` vs `c`), LangGraph waits for **all** branches to complete before moving to the join node.
- **Custom reducer ordering**: Demonstrates a `sorting_reducer` to control the order of state updates from parallel nodes.
- **LLM-powered parallelism**: A practical example that searches **Wikipedia** and **Tavily web search** in parallel, then passes the combined context to an LLM for answer generation.
- **LangGraph Studio**: Running the `parallelization` graph via the LangGraph API and Studio UI.

### Key code patterns

```python
# Fan-out from node "a" to "b" and "c" simultaneously
builder.add_edge("a", "b")
builder.add_edge("a", "c")

# Fan-in: both "b2" and "c" must complete before "d"
builder.add_edge(["b2", "c"], "d")

# Reducer to accumulate parallel results
class State(TypedDict):
    context: Annotated[list, operator.add]
```

---

## 2. Sub-graphs (`sub-graph.ipynb`)

### What it covers

- **Isolated state management**: Each sub-graph maintains its own `TypedDict` state, separate from the parent graph.
- **Input / Output schemas**: Sub-graphs use `output_schema` to control which keys are surfaced back to the parent (e.g., `FailureAnalysisOutputState`).
- **Composing sub-graphs**: Adding a compiled sub-graph as a node in a parent graph:
  ```python
  entry_builder.add_node("failure_analysis", fa_builder.compile())
  ```
- **Shared keys with reducers**: When parallel sub-graphs return the same key (e.g., `processed_logs`), the parent state must use a reducer (`operator.add`) to merge results.

### Example architecture

```
           ┌─── failure_analysis (sub-graph) ───┐
clean_logs ┤                                     ├──▶ END
           └─── question_summarization (sub-graph)┘
```

- **Failure Analysis sub-graph**: Filters logs by grade → generates a failure summary.
- **Question Summarization sub-graph**: Summarizes question themes → generates a Slack report.

---

## 3. Map-Reduce (`map-reduce.ipynb`)

### What it covers

- **`Send()` API**: Dynamically spawns parallel node invocations at runtime — the number of parallel tasks is determined by the data, not the graph structure.
- **Map step**: Breaks a topic into sub-topics, then generates a joke for each sub-topic in parallel using `Send()`.
- **Reduce step**: Collects all jokes and uses an LLM to pick the best one.
- **Private state per worker**: Each `generate_joke` call receives its own `JokeState` (just `subject: str`), decoupled from the `OverallState`.

### Key code patterns

```python
from langgraph.types import Send

def continue_to_jokes(state: OverallState):
    """Dynamically route to N parallel joke generators"""
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

# Wire it up
graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
```

### Flow

```
START → generate_topics → [Send × N] → generate_joke (parallel) → best_joke → END
```

---

## 4. Research Assistant (`research-assistant.ipynb`) — Capstone

### What it covers

This notebook brings together **every concept from Modules 1–4** into a multi-agent research assistant inspired by the [STORM paper](https://arxiv.org/abs/2402.14207).

#### Phase 1 — Analyst Generation (Human-in-the-Loop)

- An LLM generates a team of **AI analyst personas** based on a user-provided topic.
- A **human feedback interrupt** lets the user review, refine, or approve the analysts before proceeding.

#### Phase 2 — Expert Interviews (Parallelized Map via `Send()`)

- Each analyst conducts a **multi-turn interview** with an AI expert.
- The expert gathers context from **Tavily web search** and **Wikipedia** in parallel.
- Interviews continue for a configurable number of turns (`max_num_turns`).
- A routing function checks for the "Thank you" signal or turn limit to end each interview.

#### Phase 3 — Report Generation (Reduce)

- Each analyst writes a **section** of the report from their interview context.
- Parallel nodes generate the **report body**, **introduction**, and **conclusion**.
- A final `finalize_report` node stitches everything into the complete report.

### Architecture

```
                          ┌── conduct_interview (analyst 1) ──┐
START → create_analysts → │   conduct_interview (analyst 2)   │
         ↕ human_feedback │   conduct_interview (analyst N)   │
                          └───────────────┬───────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
             write_report        write_introduction      write_conclusion
                    └─────────────────────┼─────────────────────┘
                                          ▼
                                   finalize_report → END
```

Each **`conduct_interview`** is itself a sub-graph:

```
ask_question ──┬── search_web ──────┬── answer_question ──▶ (loop or save)
               └── search_wikipedia ┘
                                         │
                                   save_interview → write_section → END
```

### Key schemas

| Schema                  | Purpose                                                                   |
| ----------------------- | ------------------------------------------------------------------------- |
| `Analyst`               | Pydantic model for analyst persona (name, role, affiliation, description) |
| `GenerateAnalystsState` | State for analyst creation with human feedback                            |
| `InterviewState`        | Extends `MessagesState` for multi-turn interview conversations            |
| `ResearchGraphState`    | Top-level state tying analysts, sections, and final report together       |

---

## 🛠️ Studio

The `studio/` subdirectory contains production-ready versions of all four graphs, configured for use with **LangSmith Studio** (formerly LangGraph Studio).

| File                           | Graph                                        |
| ------------------------------ | -------------------------------------------- |
| `studio/parallelization.py`    | Web + Wikipedia parallel search → LLM answer |
| `studio/sub_graphs.py`         | Failure analysis + question summarization    |
| `studio/map_reduce.py`         | Topic → jokes → best joke                    |
| `studio/research_assistant.py` | Full multi-agent research assistant          |

### Running Studio locally

```bash
cd module-4/studio
langgraph dev
```

Then open: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`

---

## 🔑 Environment Variables

| Variable                             | Required By                         | Purpose               |
| ------------------------------------ | ----------------------------------- | --------------------- |
| `OPENAI_API_KEY` or `GEMINI_API_KEY` | All notebooks                       | LLM provider          |
| `TAVILY_API_KEY`                     | parallelization, research-assistant | Web search            |
| `LANGSMITH_API_KEY`                  | All (optional)                      | Tracing via LangSmith |

---

## 📚 Key Takeaways

1. **Parallelization** lets you run independent nodes concurrently — always use a **reducer** when parallel nodes write to the same key.
2. **Sub-graphs** provide **state isolation** — use `output_schema` to control what flows back to the parent.
3. **`Send()` API** enables **dynamic, data-driven parallelism** — the number of parallel tasks is determined at runtime.
4. **Combining patterns** (human-in-the-loop + sub-graphs + map-reduce) enables sophisticated multi-agent architectures like the research assistant.
