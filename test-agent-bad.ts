import { supportAgent } from './agents/support-agent';

async function testSupportFlow() {
  const agent = supportAgent;

  console.log('--- Test 1: Tool Usage ---');
  // This should trigger the orderLookup tool
  const res1 = await agent.generate("I need the status of order #999");
  console.log('User: I need the status of order #999');
  console.log('Agent:', res1.text);

  console.log('\n--- Test 2: General Inquiry ---');
  // This should NOT trigger a tool (just conversational)
  const res2 = await agent.generate("What is your name?");
  console.log('User: What is your name?');
  console.log('Agent:', res2.text);
}

testSupportFlow().catch(console.error);



// Add this to your test-agent.ts logic (in index.ts which doesn't exist.) 
const result = await supportAgent.generate("Check order #456");

// If using a model that supports tool calling, Mastra handles the handshake.
// Check if the agent actually called the tool:
const toolCalled = result.steps.some(s => s.type === 'tool-call');

console.log(`Did the local model use the tool? ${toolCalled ? '✅ Yes' : '❌ No'}`);
console.log('Response:', result.text);