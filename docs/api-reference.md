# API Reference

This document provides a complete reference for all API endpoints, data models, and configuration options in the Screenshot-to-Code service.

## Base Configuration

### Server Information
- **Base URL**: `http://localhost:7001`
- **Protocol**: HTTP/1.1, WebSocket
- **Framework**: FastAPI
- **CORS**: Enabled for all origins

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | No | None |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | No | None |
| `GEMINI_API_KEY` | Google Gemini API key | No | None |
| `REPLICATE_API_KEY` | Replicate API key for image generation | No | None |
| `OPENAI_BASE_URL` | Custom OpenAI API base URL | No | None |
| `SHOULD_MOCK_AI_RESPONSE` | Enable mock responses for testing | No | False |
| `NUM_VARIANTS` | Number of code variants to generate | No | 2 |

## Endpoints Summary

| Method | Endpoint | Description | Type |
|--------|----------|-------------|------|
| GET | `/` | Health check | HTTP |
| WebSocket | `/generate-code` | Real-time code generation | WebSocket |
| POST | `/api/screenshot` | Capture website screenshot | HTTP |
| GET | `/evals` | Single folder evaluation | HTTP |
| GET | `/pairwise-evals` | Two-folder comparison | HTTP |
| GET | `/best-of-n-evals` | Multi-folder comparison | HTTP |
| POST | `/run_evals` | Execute batch evaluations | HTTP |
| GET | `/models` | Available models and stacks | HTTP |

## Data Types and Enums

### InputMode
```python
InputMode = Literal["image", "video"]
```

### Stack (Technology Stacks)
```python
Stack = Literal[
    "html_css",
    "html_tailwind", 
    "react_tailwind",
    "bootstrap",
    "ionic_tailwind",
    "vue_tailwind",
    "svg"
]
```

### AI Models
```python
class Llm(Enum):
    GPT_4O_2024_11_20 = "gpt-4o-2024-11-20"
    O1_2024_12_17 = "o1-2024-12-17"
    CLAUDE_3_5_SONNET_2024_10_22 = "claude-3-5-sonnet-2024-10-22"
    CLAUDE_3_5_SONNET_2024_06_20 = "claude-3-5-sonnet-2024-06-20"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
```

### Generation Types
```python
GenerationType = Literal["create", "update"]
```

## Request/Response Models

### ScreenshotRequest
```json
{
    "url": "string",      // Required: URL to capture
    "apiKey": "string"    // Required: ScreenshotOne API key
}
```

### ScreenshotResponse
```json
{
    "url": "string"       // Base64-encoded data URL
}
```

### Eval
```json
{
    "input": "string",      // Base64-encoded input image data URL
    "outputs": ["string"]   // Array of HTML output strings
}
```

### RunEvalsRequest
```json
{
    "models": ["string"],   // Array of model identifiers
    "stack": "string"       // Technology stack identifier
}
```

### PairwiseEvalResponse
```json
{
    "evals": [Eval],        // Array of evaluation objects
    "folder1_name": "string",
    "folder2_name": "string"
}
```

### BestOfNEvalsResponse
```json
{
    "evals": [Eval],        // Array of evaluation objects  
    "folder_names": ["string"]  // Array of folder names
}
```

### ModelsResponse
```json
{
    "models": ["string"],   // Available AI model identifiers
    "stacks": ["string"]    // Available technology stacks
}
```

## WebSocket Protocol

### Connection
```
ws://localhost:7001/generate-code
```

### Message Format
All WebSocket messages use JSON format:

```json
{
    "type": "string",       // Message type identifier
    "value": "string",      // Message content
    "variantIndex": 0       // Variant index (0-based)
}
```

### Client to Server Messages

#### Initial Parameters
```json
{
    "generatedCodeConfig": "html_tailwind",
    "inputMode": "image",
    "openAiApiKey": "sk-...",
    "anthropicApiKey": "sk-ant-...",
    "openAiBaseURL": "https://api.openai.com/v1",
    "isImageGenerationEnabled": true,
    "generationType": "create",
    // Additional parameters based on input mode
}
```

### Server to Client Messages

#### Status Updates
```json
{
    "type": "status",
    "value": "Generating code...",
    "variantIndex": 0
}
```

#### Code Chunks (Streaming)
```json
{
    "type": "chunk", 
    "value": "<html>\n<head>",
    "variantIndex": 0
}
```

#### Complete Code
```json
{
    "type": "setCode",
    "value": "<html><head>...</head><body>...</body></html>",
    "variantIndex": 0
}
```

#### Error Messages
```json
{
    "type": "error",
    "value": "No OpenAI API key found",
    "variantIndex": 0
}
```

## HTTP Status Codes

### Success Codes
- `200 OK`: Request successful
- `101 Switching Protocols`: WebSocket upgrade successful

### Client Error Codes
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

### Server Error Codes
- `500 Internal Server Error`: Server processing error
- `503 Service Unavailable`: Service temporarily unavailable

### WebSocket Close Codes
- `1000`: Normal closure
- `1001`: Going away
- `4000`: Custom error code for application errors

## Error Response Format

### HTTP Errors
```json
{
    "detail": "Error message description"
}
```

### WebSocket Errors
```json
{
    "type": "error",
    "value": "Detailed error message",
    "variantIndex": 0
}
```

## Rate Limiting

### AI Service Limits
The API respects rate limits from underlying AI services:

- **OpenAI**: Based on your API plan
- **Anthropic**: Based on your API plan  
- **Google**: Based on your API plan
- **ScreenshotOne**: Based on your subscription

### Best Practices
- Implement exponential backoff for retries
- Monitor rate limit headers in responses
- Cache results when appropriate
- Use batch operations when available

## Authentication

### API Key Authentication
API keys are provided in request parameters or environment variables:

```json
{
    "openAiApiKey": "sk-...",
    "anthropicApiKey": "sk-ant-..."
}
```

### Security Considerations
- Store API keys securely (environment variables, vaults)
- Don't expose keys in client-side code
- Rotate keys regularly
- Monitor usage for unauthorized access

## CORS Configuration

The API is configured with permissive CORS settings for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Note**: Restrict origins in production environments.

## Content Types

### Supported Request Content Types
- `application/json`: JSON request bodies
- `text/plain`: WebSocket text messages

### Response Content Types
- `application/json`: JSON responses
- `text/html`: HTML responses (health check)
- `text/plain`: WebSocket text messages

## File Upload Handling

### Image Data Format
Images are handled as base64-encoded data URLs:

```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=
```

### Supported Image Formats
- PNG (recommended)
- JPEG
- GIF
- WebP

### Size Limits
- **Maximum file size**: Depends on AI service limits
- **Recommended size**: 1024x1024 pixels or smaller
- **Aspect ratio**: Any, but 16:9 or 4:3 recommended

## Caching

### Image Caching
The system caches generated images during updates:

```python
image_cache: Dict[str, str] = {}
```

### Cache Behavior
- **Create mode**: No caching
- **Update mode**: Caches images to avoid regeneration
- **Cache scope**: Per WebSocket connection
- **Cache lifetime**: Connection duration

## Logging

### Log Levels
- **INFO**: General information
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information

### Log Format
```
[TIMESTAMP] [LEVEL] [MODULE] Message
```

### Logged Events
- WebSocket connections/disconnections
- API key usage (masked)
- Model selection and timing
- Error conditions
- Generation completion

## Performance Metrics

### Response Times
- **Code generation**: 10-60 seconds (varies by model)
- **Screenshot capture**: 5-30 seconds
- **Evaluation queries**: 1-5 seconds
- **Model listing**: <1 second

### Throughput
- **Concurrent WebSocket connections**: Limited by server resources
- **Parallel model execution**: Up to 2 models simultaneously
- **Batch evaluations**: Depends on input size and models

### Resource Usage
- **Memory**: Varies by model and input size
- **CPU**: High during generation, low during idle
- **Network**: Depends on AI service latency
- **Storage**: Minimal (logs and temporary files)

## Development and Testing

### Mock Mode
Enable mock responses for testing:

```bash
export SHOULD_MOCK_AI_RESPONSE=true
```

### Health Check
```bash
curl http://localhost:7001/
```

### WebSocket Testing
Use tools like `websocat` or browser developer tools:

```bash
echo '{"generatedCodeConfig":"html_tailwind","inputMode":"image"}' | websocat ws://localhost:7001/generate-code
```

### Docker Support
The service includes Docker configuration:

```bash
docker-compose up -d
```

## API Versioning

### Current Version
- **Version**: 1.0
- **Stability**: Beta
- **Breaking Changes**: May occur without notice

### Future Versioning
- Semantic versioning will be adopted for stable releases
- Deprecation notices will be provided for breaking changes
- Multiple API versions may be supported simultaneously

## Support and Documentation

### Additional Resources
- **GitHub Repository**: Source code and issues
- **README.md**: Setup and configuration instructions
- **Troubleshooting.md**: Common issues and solutions
- **Docker Documentation**: Container deployment guide

### Community
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Community support and questions
- **Contributing**: Guidelines for code contributions

This API reference provides the complete technical specification for integrating with the Screenshot-to-Code service. For implementation examples and usage patterns, refer to the specific endpoint documentation files.