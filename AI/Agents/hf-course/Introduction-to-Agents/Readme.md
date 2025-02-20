
# Introduction to Agents

## **What is an Agent**
An Agent is a system that leverages an AI model to interact with its environment in order to achieve a user-defined objective. In simple terms, we can break down it into two parts
1. Mind- It is the part where the actual thinking happens which involves reasoning and planning keeping in mind the capabilities or available tools.
    - The most common model used nowadays is Large Language Model which majorly takes text as input and output. The popeular models involve GPT-4 by openai, LLama by Meta. 
2. Body- It defines the scope of the possible actions based on the capabilities (tool) it is equipped with.

Agents can act as Peronsal Virtual Assistant which can schedule meetings, setup alarms and many other personal tasks on behalf of the user; Customer service Chatbots which interacts with customers to resolve queries, troubleshooting based on the pre-defined objectives of decreasing wait time, increasing sales conversion etc. They also enable to create dynamic Non-Playable Characters in games which helps create more lifelike, engaging characters that evolve alongside the player’s actions.

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

3. Next token prediction- The model taked tokenized text as input, encode it and outputs scores that rank the likelihood of each token in its vocabulary as being the next one in the sequence.
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