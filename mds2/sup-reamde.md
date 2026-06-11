Q: What do you call a programmer from Boston? A: "a coda" 

@TODO: This README is being neglected in favour of working on the actual functionality, but will clean up soon.

## Coda: Multi-agentic generative coding harness 


## SupportBot: Event-Sourced Knowledge Graph Agent
A deterministic support agent architecture that treats the conversation as an append-only event log and uses Global Workspace Theory to build a transient world model (Knowledge Graph) for every inference turn.

1. Architectural Philosophy
Unlike "stateless" chat completion loops, this agent operates on a Data Plane vs. Control Plane separation:

Data Plane (The Log): Every user message, tool execution, and system state change is recorded as a discrete AgentEvent.

Control Plane (The Brain): A reducer function (rebuildGraph) collapses the event log into a directed graph of known entities (Orders, Issues, Users) before the LLM is even called.

2. Core Components
rebuildGraph (The Reducer)
The heart of the system. It consumes AgentSession.events and outputs a WorldModel.

Entity Extraction: Automatically promotes regex-matched IDs (e.g., #999) from USER_UPDATE events into Graph Nodes.

State Reconciliation: Merges TOOL_RESULT data into existing nodes, changing their state from UNRESOLVED to RESOLVED or CONFLICT.

resolveProtocol (The Router)
A dynamic system prompt selector. Based on the current graph state (e.g., an UNRESOLVED_CONFLICT node), it swaps the system instructions from General Support to Conflict Resolution.

supportAgent (The Async Generator)
An AsyncGenerator<AgentStep> that streams the internal "thinking" process.

Append USER_UPDATE to the log.

Rebuild the Knowledge Graph.

Serialize the graph into the System Prompt.

Inference via generateText.

Tool Execution (Oracle calls) and subsequent log append.

3. Data Flow & Event Schema
Events are strictly typed to prevent "hallucinated history."

TypeScript

type AgentEvent = 
  | { type: 'USER_UPDATE'; payload: { text: string }; timestamp: number }
  | { type: 'TOOL_RESULT'; payload: { toolId: string; result: any }; timestamp: number }
  | { type: 'STATE_TRANSITION'; payload: { from: string; to: string } };
The Serialization Pattern
To prevent the LLM from ignoring graph data (the "Lost in the Middle" problem), the system prompt is constructed as a prioritized array:

Context Primacy: The KNOWLEDGE_GRAPH_STATE is injected at the top of the prompt.

Constraints: Explicit "Operational Directives" (e.g., "Do not ask for IDs found in the graph").

Logic: The 1500+ character Protocol instructions follow.

4. Operational Guardrails
Tool Hallucination Recovery
The agent handles "Lazy LLM" syndrome where models return a tool's index (e.g., "0") instead of its name ("entity-lookup").

Normalization: The agent checks call.toolName against an alias map.

Key Mapping: Automatically maps varied LLM output keys (order_id, id, entityId) to a stable internal schema.

Regex Fallback
If the LLM fails to trigger a native tool call but emits a JSON-like block in the text stream, the agent uses a Regex + Zod parser to catch the intent and execute the tool anyway.

5. Testing & Instrumentation
Tests are located in tests/unit/support-agent.test.ts.

Debugging the "Blindness" Bug
If the agent asks for an ID it should already know, check the GRAPH_CONTEXT_SENT log.

Empty Graph: Check the Reducer's regex patterns.

Ignored Graph: Check the Prompt Hierarchy. The Knowledge Graph must occupy the Primacy position in the system array.

Next Steps:

Implement PERSISTENCE_LAYER to move the event log from memory to Postgres/Redis.

Add MULTI_ENTITY_RESOLVER for sessions involving multiple orders.
