## Tools and Frameworks

1. LangSmith is a platform for building production-grade LLM applications. It allows you to closely monitor and evaluate your application, so you can ship quickly and with confidence.

# RAG from scratch

1. 95% of the world's data is "private", but we can "feed it" to LLMs
2. LLM are kind of a CPU of the new type of System
3. Retrieval Augmented Generation- Question-> Indexing-> Retrieval -> Generation

**Indexing**
Document Loading

1. Stastical and ML representations-
   - Bag of words, Sparse representation, Search Method- BM25
   - Embedding, Dense representation, Search Method- kNN,HNSW
2. Process
   - Loading
   - Splitting
   - Embedding

**Retrieval**
Embed question and search in the space to get the close documents

**Generation**
Pack relevant documents into the context window. Prompt are basically template.

1. LangChain expression language

## Query Transaltion

1. Sits at the first stage, the goal is to translate user input to improve retrieval.
   - If the query is poorly written, proper retrieval would be difficult.
2. 3 Options- Rewriting query= Less abstraction; Sub-question (least-to-most); More abstraction- Step-back quesion (Step-back prompting),

### Multi-Query

1. It involves taking a query and breaking it down into multiple queries.
2. The intuition behind this approach is that the initial wording of a question may not be well-aligned with a relevant document in a high-dimensional embedding space, but rewriting it in different ways can improve retrieval.
3. This approach can be combined with retrieval by taking the rewritten questions, performing retrieval on each one, and combining the results to perform RAG.

### RAG-Fusion

1. RAG Fusion is a rewriting approach that involves generating multiple search queries based on user input, retrieving documents for each query, and then applying reciprocal rank fusion to consolidate the results
2. The input stage is same as multi query, The novelty of RAG Fusion lies in the reciprocal rank fusion step, which aggregates the documents from each retrieval into a final output ranking.
3. We often retrieve documents using different retrieval models (BM25, vector search, hybrid search). Each model returns a different ranking. RRF helps fuse these rankings to improve retrieval quality.

### Decomposition

1. Decomposition is a technique that breaks down an input question into a set of sub-questions, which can be solved individually, and this approach has been explored in various papers, including one from Google [Least-to-Most].
2. Least-to-Most- Instead of tackling a difficult problem all at once, LTM breaks it down into smaller, easier subproblems and solves them sequentially.
   - Decomposition – Break the problem into smaller subproblems.
   - Step-by-Step Solving – Solve each subproblem in order.
   - Final Solution Construction – Use the intermediate answers to solve the full problem.
   - KEY IDEA- Later steps use previous solutions as additional context, making complex reasoning easier.
3. IR-CoT- Interleave retieval with CoT
4. Combine Ideas- Dynamically retrieve to aid in solving the subproblems. The alternative approach involves running the questions in parallel and concatenating the question-answer pairs to produce the final answer. It may suitable for the cases when the answer of question doesn't depend upon the other one.

### Step-back

1. Step-back prompting is a technique presented by Google that takes the opposite approach by **asking a more abstract question**, using few-shot prompting to produce step-back questions.
2. LLMs sometimes make superficial or biased mistakes because they only consider immediate patterns in the input.
   By "stepping back", the model can reason from first principles or broader concepts. Example - _Jan Sindel s was born in what coun
   try?_ -> _what is Jan Sindel’s personal his_
   tory?`
3. The process of step-back prompting involves
   - formulating a prompt using **few-shot examples**, which is then used to generate a more abstract question
   - Get the context for both stap back question and the the original query; the pass it together to the LLM.
   - This approach can be helpful when working with textbooks or technical documentation with independent chapters focused on high-level concepts and detailed implementations
4. Learnings from code
   - Direct Prompting (Plain Text) vs FewShotChatMessagePromptTemplate- FewShotChatMessagePromptTemplate in LangChain provides a structured, reusable, and dynamically updatable approach, making it ideal for scaling and integrating with more complex applications.

### HyDE

1. Questions are short, ill worded whereas documents are dense, well worded. Create a hypothetical document for the question which are better suited for retrieval.
2. Useful in domains such as research assistant, research papers, contract analysis etc.

## Routing

Routing is the process of directing a potentially decomposed question to the right source, which could be a different database, such as a vector store, relational DB, or graph DB

1. Logical Routing- Logical routing involves giving a large language model (LLM) knowledge of various data sources and letting it reason about which one to apply the question to.
2. Semantic Routing- Routing can be very general and can involve directing a question to different prompts, vector stores, or databases. Semantic routing involves embedding a question and prompts, computing the similarity between them, and choosing a prompt based on the similarity.

## Query Construction

Query construction is the process of taking natural language and converting it into a structured query that can be applied to metadata filters on a Vector store, GraphDB or SQL.

## Indexing

1. Multi-representation Indexing
   - The idea is to take a document, split it, and then use an LLM to produce a summary or proposition that is optimized for retrieval, which can be embedded in a vector store.
   - The raw document is independently stored in a document store, and when the summary is retrieved from the vector store, the full document is returned for the LLM to perform generation

# References

1. RAG from scratch- https://www.youtube.com/watch?v=sVcwVQRHIc8&ab_channel=freeCodeCamp.org, Github -https://github.com/langchain-ai/rag-from-scratch, Slides- https://docs.google.com/presentation/d/124I8jlBRCbb0LAUhdmDwbn4nREqxSxZU1RF_eTGXUGc/edit#slide=id.g267060cc54f_0_0
2. Least-to-Most- https://arxiv.org/pdf/2205.10625
3. RAG Fusion- https://arxiv.org/pdf/2402.03367
4. Step-back prompting- https://arxiv.org/pdf/2310.06117
