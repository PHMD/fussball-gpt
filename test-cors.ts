/**
 * Test CORS headers from frontend perspective
 */

async function testCORS() {
  console.log('🧪 Testing CORS from simulated frontend (port 3000)...\n');

  try {
    const response = await fetch('http://localhost:3002/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000',  // Simulate frontend origin
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'user',
            content: 'Quick test - is Bundesliga data available?',
          },
        ],
      }),
    });

    console.log('Status:', response.status);
    console.log('\nCORS Headers:');
    console.log('  Access-Control-Allow-Origin:', response.headers.get('Access-Control-Allow-Origin'));
    console.log('  Access-Control-Allow-Methods:', response.headers.get('Access-Control-Allow-Methods'));
    console.log('  Access-Control-Allow-Headers:', response.headers.get('Access-Control-Allow-Headers'));

    if (response.ok) {
      console.log('\n✅ CORS working! Frontend will be able to connect.');

      // Read first few chunks
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let chunks = 0;

      if (reader) {
        console.log('\n📡 Streaming test (first 3 chunks):');
        while (chunks < 3) {
          const { done, value } = await reader.read();
          if (done) break;
          console.log(`  Chunk ${chunks + 1}:`, decoder.decode(value).substring(0, 50) + '...');
          chunks++;
        }
      }
    } else {
      console.log('\n❌ CORS failed!');
    }
  } catch (error) {
    console.error('❌ Error testing CORS:', error);
  }
}

testCORS().catch(console.error);
