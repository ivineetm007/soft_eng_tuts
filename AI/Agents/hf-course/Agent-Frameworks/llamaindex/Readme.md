# LLamaIndex
## Intro 

Key parts
1. Components- It is the building block that includes model, prompt etc.
2. Tools- It is the component that provide specific capabilities aloowing agent to take action.
3. Agents- It is the autonomous component that perform tasks using tools and LLM.
4. Workflows- It is a step-by-step processes that process logic together. These workflows are way to structure agentic behaviour without the explicit use of agents.

What Makes LlamaIndex Special?
1. Clear workflow system- Event driven and async-first syntax. It helps to clearly compose and organize the logic.
2. Advanced document parsing with LlamaParse- It's paid though
3. Many ready-to-use component- Like LLMs, retrievers, indexes and more.
4. LlamaHub- It is a registry of these component, agents and tools.

## Creating a RAG pipeline using components in LLamaIndex

### Five stages of RAG

1. Loading: Import data from various sources such as text files, PDFs, websites, databases, or APIs into your workflow.
2. Indexing: Generate data structures, typically vector embeddings, that represent the semantic meaning of the data for efficient querying. 
3. Storing: Save the indexed data and associated metadata to prevent the need for re-indexing in future operations. 
4. Querying: Utilize LLMs and LlamaIndex data structures to perform various querying strategies, including sub-queries and multi-step queries.
5. Evaluation: Assess the effectiveness of the workflow by measuring accuracy, faithfulness, and response time to ensure optimal performance.

**Loading and Embedding Documents**
1. Methods to Load Data:
    - SimpleDirectoryReader: A built-in loader that imports various file types from a specified local directory. 
    - LlamaParse: An official tool provided by LlamaIndex for parsing PDFs, available as a managed API. 
    - LlamaHub: A registry offering numerous data-loading libraries to ingest data from diverse sources. 
2. Creating Node Objects:
   - Purpose: Break down documents into smaller, manageable chunks called Node objects, which retain references to the original documents. 
   - IngestionPipeline: Facilitates the creation of nodes through transformations such as:
     - SentenceSplitter: Divides documents into chunks at natural sentence boundaries. 
     - HuggingFaceEmbedding: Converts each chunk into numerical embeddings that capture semantic meaning.

**Storing and Indexing Documents**
1. **Vector Store Integration**:
  - **Chroma**: A vector store used to store documents and their embeddings.
2. **Creating an Index**:
  - **VectorStoreIndex**: Handles embedding queries and nodes in the same vector space for relevant matches

**Querying a VectorStoreIndex with Prompts and LLMs**
1. **Conversion Options**:
  - **as_retriever**: For basic document retrieval, returning a list of `NodeWithScore` objects with similarity scores.
  - **as_query_engine**: For single question-answer interactions, returning a written response.
  - **as_chat_engine**: For conversational interactions that maintain memory across multiple messages, returning responses using chat history and indexed context.


**Response Processing**
Under the hood, the query engine doesn’t only use the LLM to answer the question but also uses a ResponseSynthesizer as a strategy to process the response. 
1. **ResponseSynthesizer Strategies**: Three main strategies that work well out of the box
  - **refine**: Creates and refines an answer by sequentially processing each retrieved text chunk, making separate LLM calls per chunk.
  - **compact**: Similar to refine but concatenates chunks beforehand, resulting in fewer LLM calls.
  - **tree_summarize**: Generates a detailed answer by creating a tree structure from each retrieved text chunk.

**Evaluation and observability**
LlamaIndex provides built-in evaluation tools to assess response quality. These evaluators leverage LLMs to analyze responses across different dimensions. Let’s look at the three main evaluators available:
1. FaithfulnessEvaluator: Evaluates the faithfulness of the answer by checking if the answer is supported by the context.
2. AnswerRelevancyEvaluator: Evaluate the relevance of the answer by checking if the answer is relevant to the question.
3. CorrectnessEvaluator: Evaluate the correctness of the answer by checking if the answer is correct.

Even without direct evaluation, we can gain insights into how our system is **performing through observability** using platform such as LLamaTrace.



