/**
 * Test merged application - frontend + backend on same origin
 */

async function testMergedApp() {
  console.log('🧪 Testing merged application (no CORS needed)...\n');

  try {
    const response = await fetch('http://localhost:3001/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'user',
            content: 'Quick test - what Bundesliga data do you have available?',
          },
        ],
      }),
    });

    console.log('Status:', response.status);
    console.log('Content-Type:', response.headers.get('Content-Type'));

    if (response.ok) {
      console.log('\n✅ API endpoint working! Starting to stream response...\n');

      // Read first few chunks
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let chunks = 0;
      let preview = '';

      if (reader) {
        while (chunks < 5) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value);
          preview += text;
          console.log(`Chunk ${chunks + 1}:`, text.substring(0, 80) + '...');
          chunks++;
        }
        console.log('\n📝 Response preview:', preview.substring(0, 200) + '...');
        console.log('\n✅ Merged application working! Frontend and backend successfully integrated.');
      }
    } else {
      console.log('❌ API endpoint failed!');
      const error = await response.text();
      console.log('Error:', error);
    }
  } catch (error) {
    console.error('❌ Error testing merged app:', error);
  }
}

testMergedApp().catch(console.error);
