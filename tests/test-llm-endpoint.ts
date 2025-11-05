/**
 * Test script for LLM query endpoint
 *
 * Run with: npx tsx test-llm-endpoint.ts
 */

async function testLLMEndpoint() {
  console.log('\n🧪 Testing LLM query endpoint...\n');

  try {
    const response = await fetch('http://localhost:3002/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'user',
            content: 'What are the latest Bundesliga news? Give me a brief summary.',
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('✅ Successfully connected to LLM endpoint');
    console.log('📡 Streaming response:\n');

    // Read the streaming response
    const reader = response.body?.getReader();
    if (!reader) {
      console.error('❌ Response body is not available');
      return;
    }

    const decoder = new TextDecoder();
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      fullResponse += chunk;
      process.stdout.write(chunk); // Show streaming in real-time
    }

    console.log('\n\n✅ Streaming complete!');
    console.log(`📊 Total response length: ${fullResponse.length} characters`);
  } catch (error) {
    console.error('❌ Error testing LLM endpoint:', error);
  }
}

testLLMEndpoint().catch(console.error);
