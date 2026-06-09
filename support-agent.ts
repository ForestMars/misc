/**
 * @file support-agent.ts
 * @description Event-Sourced Graph-Based Support Agent.
 */

import { generateText } from 'ai';
import { ollama } from 'ai-sdk-ollama';
import { entityLookupTool } from '@/tools/order-tools';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { z } from 'zod';
import { rebuildGraph } from '@/lib/graph-reducer';
import type { AgentStep, AgentConfig, AgentSession, AgentEvent } from '@/types/agent-types';
import { resolveProtocol } from '@/lib/protocol-resolver';
import { CONTEXT_ANCHOR } from '@/agents/config';

// --- CONFIGURATION ---
const DEFAULT_MODEL = 'qwen2.5:7b';
const TEMPERATURE = 0; 

const __dirname = dirname(fileURLToPath(import.meta.url));
const instructions = readFileSync(join(__dirname, '..', '..', 'config', 'agent-instructions.txt'), 'utf-8');

const supportAgentConfig: AgentConfig = {
  name: 'SupportBot',
  model: process.env.SUPPORT_AGENT_MODEL || DEFAULT_MODEL,
  instructions,
  temperature: TEMPERATURE,
  tools: [entityLookupTool]
};

const toolCallSchema = z.object({
  tool: z.string(),
  entityId: z.string().or(z.number()).transform(v => String(v))
});

// --- HELPERS ---

/**
 * Reconstruct a human-readable conversation history from the event log.
 * This is what gives the LLM a coherent "memory" of the conversation —
 * structured graph state alone is not enough for the model to resolve
 * pronoun/entity references across turns.
 */
function buildConversationHistory(events: AgentEvent[]): string {
  return events
    .filter(e => e.type === 'USER_UPDATE' || e.type === 'TOOL_RESULT')
    .map(e => {
      if (e.type === 'USER_UPDATE') {
        return `User: ${e.payload.text}`;
      }
      if (e.type === 'TOOL_RESULT') {
        return `System: Retrieved entity ${e.payload.entityId} → ${JSON.stringify(e.payload.result)}`;
      }
      return null;
    })
    .filter(Boolean)
    .join('\n');
}

/**
 * Generator-based support agent using Global Workspace Theory.
 */
export async function* supportAgent(
  userInput: string,
  session: AgentSession,
  opts?: { client?: any }
): AsyncGenerator<AgentStep, void, unknown> {

  if (!session) throw new Error("No session provided to Agent.");
  if (!session.events) session.events = [];

  const model = opts?.client || ollama(supportAgentConfig.model);

  // BROADCAST: Initialize and record the User Update to the Data Plane.
  // NOTE: We push to the event log BEFORE calling rebuildGraph so that
  // the current user message is visible to the router and world model.
  const userEvent: AgentEvent = { 
    type: 'USER_UPDATE', 
    payload: { text: userInput }, 
    timestamp: Date.now() 
  };
  session.events.push(userEvent);

  // REDUCR: Build the World Model from the append-only log.
  // This allows the agent to "remember" failures across devices.
  const worldModel = rebuildGraph(session.events);
  const graphContext = worldModel.serialize();

  // Use the central brain we built to decide how to act.
  const protocol = resolveProtocol(graphContext, session.activeDomain);

  console.log(`===========================[ROUTER] Engaging ${protocol.name} protocol.`);

  yield { 
    type: 'thinking', 
    timestamp: Date.now(), 
    message: 'Consulting internal knowledge graph...' 
  };

  console.log(`[DEBUG] Protocol System Prompt Length: ${protocol.systemPrompt?.length}`);
  console.log(`[DEBUG] Full System Prompt Sample: "${protocol.systemPrompt?.substring(0, 100)}..."`);
  console.log(`[DEBUG] EVENT_LOG_LENGTH: ${session.events.length}`);
  console.log(`[DEBUG] RECENT_EVENTS: ${JSON.stringify(session.events.slice(-2))}`);
  console.log(`[DEBUG] GRAPH_CONTEXT_SENT: """\n${graphContext}\n"""`);

  // INFERENCE: Call LLM with instructions and the serialized Graph State.
  // Prompt ordering matters for small models — place behavioral instructions
  // before the data they govern, and gate the graph with an explicit instruction
  // so the model treats it as authoritative memory, not just metadata.
  const systemPrompt = [
    instructions,           // Constitution — who you are, non-negotiables
    protocol.systemPrompt,  // What to do RIGHT NOW — close to the data it governs
    CONTEXT_ANCHOR,         // How to interpret what follows
    `### CURRENT KNOWLEDGE_GRAPH\n` +
    `The following represents your memory of this conversation. ` +
    `All entity IDs and states here are established facts — ` +
    `do NOT ask the user to re-provide information already present here.\n`,
    graphContext,           // The World Model — last thing read, most salient
  ].filter(Boolean).join('\n\n');

  // Include reconstructed conversation history in the prompt so the model
  // can resolve cross-turn references (e.g. "it" → order #999).
  // Without this, the model has no conversational grounding — structured
  // graph state alone is not sufficient for pronoun/entity resolution.
  const conversationHistory = buildConversationHistory(session.events);
  const fullPrompt = conversationHistory
    ? `${conversationHistory}\nUser: ${userInput}`
    : userInput;

  const response = await generateText({
    model,
    system: systemPrompt,
    tools: protocol.tools, 
    prompt: fullPrompt,
    temperature: supportAgentConfig.temperature
  });

  const text = response.text.trim();
  console.log(`\n[DEBUG] LLM Raw Output (Text Content): """\n${text}\n"""\n`);
  if (response.toolCalls.length > 0) {
    console.log(`\n[DEBUG] @@@@@@ Native Tool Calls Found:`, JSON.stringify(response.toolCalls, null, 2));
  }

  // TOOL CALL EXTRACTION
  // Priority 1: Native tool calls from the AI SDK
  let toolCall: { tool: string; entityId: string } | null = null;

  if (response.toolCalls && response.toolCalls.length > 0) {
    const call = response.toolCalls[0];

    // toolName === '0' is a known provider variant — see issue tracker
    const isLookup = call.toolName === 'entity-lookup' || call.toolName === '0';

    if (isLookup) {
      // Defensively find the arguments object.
      // Checks .args (standard AI SDK) OR .input (seen in some provider variants)
      const args = (call.args || (call as any).input || {}) as any;
      const rawId = args.entityId || args.order_id || args.order_number || args.id;

      if (rawId !== undefined) {
        toolCall = {
          tool: 'entity-lookup',
          entityId: String(rawId)
        };
      }
    } 
  }

  // Priority 2: JSON embedded in text output
  // REGEX FALLBACK — only if native extraction failed
  if (!toolCall && text) {
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const validated = toolCallSchema.safeParse(JSON.parse(jsonMatch[0]));
        if (validated.success) toolCall = validated.data;
      } catch (e) { /* Fallback to conversational */ }
    }
  }

  // EXECUTION & BROADCAST
  if (toolCall) {
    const { entityId } = toolCall;
    const toolId = toolCall.tool;

    yield { type: 'tool_call', timestamp: Date.now(), toolId, parameters: { entityId } };

    // Execute the tool (The "Oracle" call)
    const result = await entityLookupTool.execute({ entityId });

    // BROADCAST tool result to data plane.
    // This is key to preventing endless loops on re-hydration.
    session.events.push({
      type: 'TOOL_RESULT',
      payload: { toolId, entityId, result },
      timestamp: Date.now()
    }); 

    yield { type: 'tool_result', timestamp: Date.now(), toolId, result };

    // Rebuild with the tool result now included so the final synthesis
    // prompt reflects the fully updated world state.
    const updatedGraphContext = rebuildGraph(session.events).serialize();
    const historyWithResult = buildConversationHistory(session.events);

    // Final Synthesis using the updated tool data
    const finalResponse = await generateText({
      model,
      system: [
        protocol.systemPrompt,
        `### CURRENT KNOWLEDGE_GRAPH\n` +
        `Do NOT ask the user for information already present here.\n` +
        updatedGraphContext,
      ].filter(Boolean).join('\n\n'),
      prompt: `${historyWithResult}\n\nBased on the above, summarize the situation for the user.`,
      temperature: supportAgentConfig.temperature
    });

    console.log('[DEBUG] ToolCalls found:', response.toolCalls);
    console.log('[DEBUG] Raw Text found:', response.text);

    yield { type: 'final', timestamp: Date.now(), text: finalResponse.text };
  } else {
    yield { type: 'final', timestamp: Date.now(), text };
  }
}

export const supportAgentModelSpec = supportAgentConfig.model;
