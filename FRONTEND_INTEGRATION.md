# Frontend Integration Instructions

## Backend API Ready ✅

The backend API is running and ready to accept connections from your frontend.

### Backend Details

- **URL**: `http://localhost:3002/api/query`
- **Method**: POST
- **CORS**: Enabled for `http://localhost:3000`
- **Response**: Streaming (Server-Sent Events)

### Frontend Configuration

Tell your frontend agent to configure the `useChat` hook like this:

```typescript
import { useChat } from '@ai-sdk/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: 'http://localhost:3002/api/query',  // Backend API endpoint
  });

  // ... rest of your component
}
```

### Request Format

The backend expects this JSON structure:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are the latest Bundesliga news?"
    }
  ]
}
```

### Response Format

The backend returns a streaming response with AI messages about Bundesliga, using real-time data from:
- Kicker RSS feed
- (More data sources coming in Week 2)

### Testing

1. **Backend is running**: http://localhost:3002
2. **API endpoint**: http://localhost:3002/api/query
3. **Test query**: "What's happening in Bundesliga this week?"

### Architecture

```
Frontend (port 3000)
    ↓ POST request
Backend API (port 3002)
    ↓ Fetches Bundesliga data
    ↓ Calls Claude 3.5 Sonnet
    ↓ Streams response
Frontend receives streaming AI response
```

### CORS Enabled

The backend has been configured to accept requests from `http://localhost:3000`, so cross-origin requests will work.

### Environment Variables

The backend already has:
- `ANTHROPIC_API_KEY` (for Claude API)
- All other API keys from the Python project

No additional configuration needed on the frontend side.
