
# Introduction to Agents

## **What is an Agent**
An Agent is a system that leverages an AI model to interact with its environment in order to achieve a user-defined objective. In simple terms, we can break down it into two parts
1. Mind- It is the part where the actual thinking happens which involves reasoning and planning keeping in mind the capabilities or available tools.
    - The most common model used nowadays is Large Language Model which majorly takes text as input and output. The popular models involve GPT-4 by openai, LLama by Meta. 
2. Body- It defines the scope of the possible actions based on the capabilities (tool) it is equipped with.

Agents can act as Personal Virtual Assistant which can schedule meetings, setup alarms and many other personal tasks on behalf of the user; Customer service Chatbots which interacts with customers to resolve queries, troubleshooting based on the pre-defined objectives of decreasing wait time, increasing sales conversion etc. They also enable to create dynamic Non-Playable Characters in games which helps create more lifelike, engaging characters that evolve alongside the player’s actions.

## **What are LLMs**
1. Large Language Model- It is a type of AI model that excels at understanding and generating human language. Most LLMs nowadays are built on the Transformer architecture which are of three types
    - Encoders- It takes text (or other data) as input and outputs a dense representation; typically has millions of parameters. Used for semantic search, NER and classication.
    - Decoders- It focuses on generating new tokens to complete a sequence, one token at a time; billions (in the US sense, i.e., 10^9) of parameters. Used for textbot, chatbots etc.
    - SeqSeq- The encoder first processes the input sequence into a context representation, then the decoder generates an output sequence; typically has millions of parameters. Used for translation, summarization and paraphrasing.
    - LLMs are typically decoder-based models with the underlying principle- to predict the next token, given a sequence of previous tokens.
2. Tokens- Unit of information an LLM works with
    - English has an estimated 600,000 words, an LLM might have a vocabulary of around 32,000 tokens (as is the case with Llama 2)
    - Tokenize Playground- "show me similar products as per the image under 2000, from brands like zara, H&M", GPT-4 creates 21 tokens, LLama creates 21 tokens. gork-1 creates 24 tokens
    - Special Tokens- Each LLM has some special tokens specific to the model like to indicate the start or end of a sequence, message, or response. 

| Model      | Provider                     | EOS Token             | Functionality                 |
|------------|------------------------------|-----------------------|-------------------------------|
| GPT4       | OpenAI                       | `<\|endoftext\|>`     | End of message text           |
| Llama 3    | Meta (Facebook AI Research)  | `<\|eot_id\|>`          | End of sequence               |
| Deepseek-R1| DeepSeek                     | `<\|end_of_sentence\|>` | End of message text           |
| SmolLM2    | Hugging Face                 | `<\|im_end\|>`          | End of instruction or message |
| Gemma      | Google                       | `<end_of_turn>`       | End of conversation turn      |

3. Next token prediction- The model takes tokenized text as input, encode it and outputs scores that rank the likelihood of each token in its vocabulary as being the next one in the sequence.
    - Simple strategy- It would be to always take the token with the maximum score.
    - Bit advanced strategies- Beam search explores multiple candidate sequences to find the one with the maximum total score–even if some individual tokens have lower scores.
4. How are LLMs trained
    - LLMs are trained on large datasets of text, where they learn to predict the next word in a sequence through a self-supervised or masked language modeling objective. From this unsupervised learning, the model learns the structure of the language and **underlying patterns in text, allowing the model to generalize to unseen data.**
5. After this initial pre-training, LLMs can be fine-tuned on a supervised learning objective to perform specific tasks.

## Chat Template

### Chat Messages
When we chat with systems like ChatGPt, you’re actually exchanging messages. Behind the scenes, these messages are concatenated and formatted into a prompt that the model can understand. Chat Templates convert conversations, represented as lists of messages, into a single tokenizable string in the format that the model expects. They are part of tokenizer.
1. System Message- System messages (also called System Prompts) define **how the model should behave**. They serve as **persistent instructions**, guiding every subsequent interaction.  System Message also gives information about the **available tools**, provides instructions to the model on **how to format the actions** to take, and includes guidelines on how the thought process should be segmented.
2. User and Assistant Messages- A conversation consists of alternating messages between a Human (user) and an LLM (assistant). Chat templates help maintain context by preserving conversation history, storing previous exchanges between the user and the assistant. The same conversation would translated into different prompt when using different LLM models.
```
conversation = [
    {"role": "user", "content": "I need help with my order"},
    {"role": "assistant", "content": "I'd be happy to help. Could you provide your order number?"},
    {"role": "user", "content": "It's ORDER-123"},
]

# SmolLM2
<|im_start|>system
You are a helpful AI assistant named SmolLM, trained by Hugging Face<|im_end|>
<|im_start|>user
I need help with my order<|im_end|>
<|im_start|>assistant
I'd be happy to help. Could you provide your order number?<|im_end|>
<|im_start|>user
It's ORDER-123<|im_end|>
<|im_start|>assistant

# Llama 3.2
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 10 Feb 2025

<|eot_id|><|start_header_id|>user<|end_header_id|>

I need help with my order<|eot_id|><|start_header_id|>assistant<|end_header_id|>

I'd be happy to help. Could you provide your order number?<|eot_id|><|start_header_id|>user<|end_header_id|>

It's ORDER-123<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```
### Chat Templates
1. Base Models vs. Instruct Models
    - A Base Model is trained on raw text data to predict the next token. To make a Base Model behave like an instruct model, format `prompts in a consistent way`
    - An Instruct Model is fine-tuned specifically to follow instructions and engage in conversations. For example, `SmolLM2-135M` is a base model, while `SmolLM2-135M-Instruct` is its instruction-tuned variant. Make sure to use the correct chat template.
    ```
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-1.7B-Instruct")
    rendered_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ```
2. In transformers, chat templates include Jinja2 code that describes how to transform the ChatML list of JSON messages.

```
# SmolLM2-135M-Instruct chat template
{% for message in messages %}
{% if loop.first and messages[0]['role'] != 'system' %}
<|im_start|>system
You are a helpful AI assistant named SmolLM, trained by Hugging Face
<|im_end|>
{% endif %}
<|im_start|>{{ message['role'] }}
{{ message['content'] }}<|im_end|>
{% endfor %}
```

## What are tools?

### What are AI tools
A Tool is a **function given to the LLM**. This function should **fulfill a clear objective**.

|Tool	|Description|
|-------|---------|
|Web Search	| Allows the agent to fetch up-to-date information from the internet.|
|Image Generation	| Creates images based on text descriptions.|
|Retrieval	| Retrieves information from an external source.|
|API Interface	| Interacts with an external API (GitHub, YouTube, Spotify, etc.).|

A tool should contain
- A textual description of what the function does.
- A Callable (something to perform an action).
- Arguments with typings.
- (Optional) Outputs with typings.

### How do tools work?
We teach the LLM about the existence of tools, and ask the model to generate text that will invoke tools when it needs to. The LLM will generate text, in the form of code, to invoke that tool. It is the responsibility of the Agent to parse the LLM’s output, recognize that a tool call is required, and invoke the tool on the LLM’s behalf.

### How do we give tools to an LLM?
We essentially use the system prompt to provide textual descriptions of available tools to the model.
Example, to implement a calculator tool-
```
Python Implementation
def calculator(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
    
Tool Definition string for LLM
Tool Name: calculator, Description: Multiply two integers., Arguments: a: int, b: int, Outputs: int

# To build description automatically
@tool
def calculator(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

print(calculator.to_string())
```
The description is **injected** in the system prompt.

## AI Agent Workflow

### Thought-Action-Observation Cycle
1. Thought: The LLM part of the Agent decides what the next step should be.
2. Action: The agent takes an action, by calling the tools with the associated arguments.
3. Observation: The model reflects on the response from the tool.
4. These three components work together in a continuous loop until the objective of the agent has been fulfilled.
5. In many Agent frameworks, **the rules and guidelines are embedded directly into the system prompt**, ensuring that every cycle adheres to a defined logic.
```
# EXAMPLE
system_message="""You are an AI assistant designed to help users efficiently and accurately. Your
primary goal is to provide helpful, precise, and clear responses.

You have access to the following tools:
Tool Name: calculator, Description: Multiply two integers., Arguments: a: int, b: int, Outputs: int

You should think step by step in order to fulfill the objective with a reasoning divided in
Thought/Action/Observation that can repeat multiple times if needed.

You should first reflect with ‘Thought: {your_thoughts}’ on the current situation,
then (if necessary ), call a tool with the proper JSON formatting ‘Action: {JSON_BLOB}’, or your print
your final answer starting with the prefix ‘Final Answer:’"""
```

### Thought: Internal Reasoning and the Re-Act Approach
Thoughts represent the Agent’s internal reasoning and planning processes to solve the task. In the case of LLMs fine-tuned for function-calling, the thought process is optional. In case you’re not familiar with function-calling, there will be more details in the Actions section.
1. Planning- “I need to break this task into three steps: 1) gather data, 2) analyze trends, 3) generate report”
2. Analysis- “Based on the error message, the issue appears to be with the database connection parameters”
3. Decision Making-	“Given the user’s budget constraints, I should recommend the mid-tier option”
4. Problem Solving-	“To optimize this code, I should first profile it to identify bottlenecks”
5. Memory Integration- “The user mentioned their preference for Python earlier, so I’ll provide examples in Python”
6. Self-Reflection-	“My last approach didn’t work well, I should try a different strategy”
7. Goal Setting- “To complete this task, I need to first establish the acceptance criteria”
8. Prioritization- “The security vulnerability should be addressed before adding new features”

**The Re-Act Approach**
ReAct is a simple prompting technique that appends “Let’s think step by step” before letting the LLM decode the next tokens. Indeed, prompting the model to think “step by step” encourages the decoding process toward next tokens that generate a plan, rather than a final solution, since the model is encouraged to decompose the problem into sub-tasks.
Recent models have been trained to always include specific thinking sections (enclosed between <think> and </think> special tokens). This is not just a prompting technique like ReAct, but a training method where the model learns to generate these sections after analyzing thousands of examples that show what we expect it to do.

### Actions: Enabling the Agent to Engage with Its Environment
Actions are the **concrete steps an AI agent takes to interact with its environment.**

There are multiple types of Agents that take actions differently:
1. JSON Agent - The Action to take is specified in JSON format.
2. Code Agent - The Agent writes a code block that is interpreted externally.
3. Function-calling Agent- It is a subcategory of the JSON Agent which has been fine-tuned to generate a new message for each action.

One crucial part of an agent is the **ability to STOP generating new tokens when an action is complete.**

**Stop and Parse Approach**
1. Generation in a Structured Format: The agent outputs its intended action in a clear, predetermined format (JSON or code).
2. Halting Further Generation: Once the action is complete, the agent stops generating additional tokens. This prevents extra or erroneous output.
3. Parsing the Output: An external parser reads the formatted action, determines which Tool to call, and extracts the required parameters.

**Code Agents**
The idea is: instead of outputting a simple JSON object, a Code Agent **generates an executable code block—typically in a high-level language like Python.**
Code offers greater expressiveness, modularity, and reusability than JSON, making it more flexible for complex logic. It enhances debugability through structured syntax and allows direct integration with external libraries and APIs for advanced operations.
![Alt text](./code-vs-json-actions.png)

### Observe: Integrating Feedback to Reflect and Adapt
1. Observations are how an Agent perceives the consequences of its actions.
2. Observations can take various forms, including system feedback, data changes, environmental data, and time-based events, all of which are appended after executing an action to guide future decisions effectively.

## Build your agent

## Using smolagent
`smolagent` is a library that provides a framework for developing your agents with ease.
1. Gradio space for the first agent- https://huggingface.co/spaces/vinm007/First_agent_template



