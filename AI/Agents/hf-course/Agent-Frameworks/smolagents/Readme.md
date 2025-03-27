# smolagents

## Overview
1. Smolagents- smolagents is one of the many open-source agent frameworks available for application development. 
2. CodeAgents- CodeAgents are the primary type of agent in smolagents. Instead of generating JSON or text, these agents produce Python code to perform actions.
3. ToolCallingAgents- These agents rely on JSON/text blobs that the system must parse and interpret to execute actions. 
4. Tools- Tool class or the @tool decorator
5. Retrieval Agents- Retrieval agents allow models access to knowledge bases, making it possible to search, synthesize, and retrieve information from multiple sources.
6. Multi-Agent Systems- By combining agents with different capabilities—such as a web search agent with a code execution agent—you can create more sophisticated solutions.
7. Vision and Browser agents- Vision agents extend traditional agent capabilities by incorporating Vision-Language Models (VLMs)

## Why use smolagents?
1. Key advantages- Simplicity, flexible LLM support, code-first approach and HF Hub integration. 
2. When to use?- 
   - You need a lightweight and minimal solution.
   - You want to experiment quickly without complex configurations.
   - Your application logic is straightforward. 
3. Code vs. JSON Actions- smolagents focuses on tool calls in code
4. Agent types in smolagents- Agents in smolagents operate as multi-step agents. 
   - MultiStep Agent- One thought, one tool call and execution
5. CodeAgent is the primary type of agentbut it also supports **ToolCallingAgent**
6. Model Integration
   - TransformersModel: Implements a local transformers pipeline for seamless integration.
   - HfApiModel: Supports serverless inference calls through Hugging Face’s infrastructure, or via a growing number of third-party inference providers.
   - LiteLLMModel, OpenAIServer Model, AzureOpenAIModel

## Building Agents That Use Code


## Resources
1. smolagents Documentation - Official docs for the smolagents library
2. Building Effective Agents - Research paper on agent architectures
3. Agent Guidelines - Best practices for building reliable agents
4. LangGraph Agents - Additional examples of agent implementations
5. Function Calling Guide - Understanding function calling in LLMs
6. RAG Best Practices - Guide to implementing effective RAG
