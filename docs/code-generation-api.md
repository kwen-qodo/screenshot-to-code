# Code Generation API

The Code Generation API is the core functionality of the Screenshot-to-Code service, converting images and videos into functional code using advanced AI models.

## WebSocket Endpoint

### `/generate-code`

**Protocol**: WebSocket  
**Description**: Real-time streaming code generation from visual inputs

## Connection Flow

1. **Establish WebSocket Connection**
2. **Send Parameters** (JSON object)
3. **Receive Status Updates** (streaming)
4. **Receive Code Chunks** (streaming)
5. **Receive Final Code** (complete)
6. **Connection Closes**

## Request Parameters

### Required Parameters

| Parameter | Type | Description | Valid Values |
|-----------|------|-------------|--------------|
| `generatedCodeConfig` | string | Technology stack for code generation | `"html_css"`, `"html_tailwind"`, `"react_tailwind"`, `"bootstrap"`, `"ionic_tailwind"`, `"vue_tailwind"`, `"svg"` |
| `inputMode` | string | Type of input being processed | `"image"`, `"video"` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `openAiApiKey` | string | null | OpenAI API key for GPT models |
| `anthropicApiKey` | string | null | Anthropic API key for Claude models |
| `openAiBaseURL` | string | null | Custom OpenAI API base URL |
| `isImageGenerationEnabled` | boolean | true | Enable AI image generation in output |
| `generationType` | string | "create" | Generation mode: `"create"` or `"update"` |

### Input Data Parameters

For image input mode, you'll also need to include:
- Image data (base64 encoded)
- Any additional context or instructions

## Response Messages

The WebSocket sends JSON messages with the following structure:

```json
{
    "type": "message_type",
    "value": "message_content", 
    "variantIndex": 0
}
```

### Message Types

| Type | Description | Example Value |
|------|-------------|---------------|
| `status` | Progress updates | `"Generating code..."`, `"Generating images..."`, `"Code generation complete."` |
| `chunk` | Streaming code content | `"<html>\n<head>"` |
| `setCode` | Complete generated code | `"<html><head>...</head><body>...</body></html>"` |
| `error` | Error messages | `"No OpenAI API key found"` |

## Usage Examples

### JavaScript/TypeScript Example

```javascript
class CodeGenerator {
    constructor(baseUrl = 'ws://localhost:7001') {
        this.baseUrl = baseUrl;
        this.ws = null;
    }

    async generateCode(params) {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(`${this.baseUrl}/generate-code`);
            
            let generatedCode = '';
            let currentVariant = 0;
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.ws.send(JSON.stringify(params));
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                switch(data.type) {
                    case 'status':
                        console.log(`Status (variant ${data.variantIndex}): ${data.value}`);
                        break;
                        
                    case 'chunk':
                        generatedCode += data.value;
                        // Update UI with streaming content
                        this.updateCodeDisplay(generatedCode, data.variantIndex);
                        break;
                        
                    case 'setCode':
                        console.log(`Code generation complete for variant ${data.variantIndex}`);
                        resolve({
                            code: data.value,
                            variant: data.variantIndex
                        });
                        break;
                        
                    case 'error':
                        console.error(`Error: ${data.value}`);
                        reject(new Error(data.value));
                        break;
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
            };
        });
    }
    
    updateCodeDisplay(code, variantIndex) {
        // Update your UI with the streaming code
        const codeElement = document.getElementById(`code-variant-${variantIndex}`);
        if (codeElement) {
            codeElement.textContent = code;
        }
    }
}

// Usage
const generator = new CodeGenerator();

const params = {
    generatedCodeConfig: 'html_tailwind',
    inputMode: 'image',
    openAiApiKey: 'your-openai-api-key',
    isImageGenerationEnabled: true,
    generationType: 'create',
    // Include your image data here
    imageUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
};

generator.generateCode(params)
    .then(result => {
        console.log('Generated code:', result.code);
    })
    .catch(error => {
        console.error('Generation failed:', error);
    });
```

### Python Example

```python
import asyncio
import websockets
import json

class CodeGenerator:
    def __init__(self, base_url="ws://localhost:7001"):
        self.base_url = base_url
    
    async def generate_code(self, params):
        uri = f"{self.base_url}/generate-code"
        
        async with websockets.connect(uri) as websocket:
            # Send parameters
            await websocket.send(json.dumps(params))
            
            generated_code = ""
            
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "status":
                    print(f"Status (variant {data['variantIndex']}): {data['value']}")
                
                elif data["type"] == "chunk":
                    generated_code += data["value"]
                    print(f"Received chunk for variant {data['variantIndex']}")
                
                elif data["type"] == "setCode":
                    print(f"Code generation complete for variant {data['variantIndex']}")
                    return {
                        "code": data["value"],
                        "variant": data["variantIndex"]
                    }
                
                elif data["type"] == "error":
                    raise Exception(f"Generation error: {data['value']}")

# Usage
async def main():
    generator = CodeGenerator()
    
    params = {
        "generatedCodeConfig": "react_tailwind",
        "inputMode": "image", 
        "openAiApiKey": "your-openai-api-key",
        "isImageGenerationEnabled": True,
        "generationType": "create",
        # Include your image data
    }
    
    try:
        result = await generator.generate_code(params)
        print("Generated code:", result["code"])
    except Exception as e:
        print("Generation failed:", e)

# Run the example
asyncio.run(main())
```

### cURL Example (for testing connection)

```bash
# Note: cURL doesn't support WebSocket natively, but you can test with websocat
# Install websocat: cargo install websocat

echo '{
    "generatedCodeConfig": "html_tailwind",
    "inputMode": "image",
    "openAiApiKey": "your-openai-api-key",
    "isImageGenerationEnabled": true,
    "generationType": "create"
}' | websocat ws://localhost:7001/generate-code
```

## Technology Stack Details

### HTML + CSS (`html_css`)
- Generates clean HTML with embedded CSS
- Best for simple, static websites
- No external dependencies

### HTML + Tailwind (`html_tailwind`)
- HTML with Tailwind CSS classes
- Responsive design by default
- Requires Tailwind CSS CDN or build process

### React + Tailwind (`react_tailwind`)
- React functional components
- Tailwind CSS for styling
- Modern React patterns (hooks, etc.)

### Bootstrap (`bootstrap`)
- HTML with Bootstrap framework
- Responsive grid system
- Bootstrap component classes

### Ionic + Tailwind (`ionic_tailwind`)
- Ionic framework components
- Mobile-first design
- Tailwind CSS integration

### Vue + Tailwind (`vue_tailwind`)
- Vue.js single-file components
- Composition API
- Tailwind CSS styling

### SVG (`svg`)
- Scalable Vector Graphics
- Ideal for icons and illustrations
- XML-based format

## Error Handling

### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `"No OpenAI or Anthropic API key found"` | Missing API keys | Provide valid API keys in parameters or environment |
| `"Invalid generated code config"` | Invalid stack parameter | Use one of the supported stack values |
| `"Invalid input mode"` | Invalid input mode | Use `"image"` or `"video"` |
| `"Authentication failed"` | Invalid API key | Check API key validity |
| `"Rate limit exceeded"` | API quota exceeded | Wait or upgrade API plan |

### Error Response Format

```json
{
    "type": "error",
    "value": "Detailed error message",
    "variantIndex": 0
}
```

## Model Selection Logic

The system automatically selects AI models based on:

1. **Available API Keys**: Uses models for which you have valid keys
2. **Generation Type**: 
   - `"create"`: Uses Claude 3.5 Sonnet (2024-10-22) for better creativity
   - `"update"`: Uses Claude 3.5 Sonnet (2024-06-20) for more focused updates
3. **Input Mode**:
   - `"video"`: Requires Anthropic API key (Claude models only)
   - `"image"`: Can use any available model

### Model Priority

1. **Both OpenAI + Anthropic keys**: Runs Claude + GPT-4 in parallel
2. **OpenAI key only**: Runs GPT-4 variants
3. **Anthropic key only**: Runs Claude variants
4. **No keys**: Returns error

## Performance Considerations

- **Parallel Generation**: Multiple model variants run simultaneously
- **Streaming**: Code is delivered in real-time chunks
- **Image Generation**: Optional, can be disabled for faster response
- **Caching**: Images are cached during updates to avoid regeneration

## Best Practices

1. **API Key Management**: Store keys securely, prefer environment variables
2. **Error Handling**: Always implement proper error handling for WebSocket connections
3. **UI Updates**: Use streaming chunks to provide real-time feedback
4. **Resource Cleanup**: Properly close WebSocket connections
5. **Rate Limiting**: Implement client-side rate limiting for API calls