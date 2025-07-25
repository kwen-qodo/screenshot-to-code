# Getting Started with Screenshot-to-Code API

This guide will help you quickly get started with the Screenshot-to-Code API, from setup to making your first API calls.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** (for frontend, optional)
- **Docker** (optional, for containerized deployment)
- **API Keys** for AI services (at least one):
  - OpenAI API key
  - Anthropic API key
  - Google Gemini API key (optional)
  - ScreenshotOne API key (for screenshot capture)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/abi/screenshot-to-code.git
cd screenshot-to-code

# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt
# OR using poetry
poetry install
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
# backend/.env

# Required: At least one AI service API key
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Additional services
GEMINI_API_KEY=your-gemini-key-here
REPLICATE_API_KEY=your-replicate-key-here

# Optional: Screenshot service
SCREENSHOTONE_API_KEY=your-screenshotone-key-here

# Optional: Custom configurations
OPENAI_BASE_URL=https://api.openai.com/v1
NUM_VARIANTS=2
```

### 3. Start the Server

```bash
# From the backend directory
python main.py

# OR using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 7001 --reload
```

The API will be available at `http://localhost:7001`

### 4. Verify Installation

Test the health endpoint:

```bash
curl http://localhost:7001/
```

You should see:
```html
<h3>Your backend is running correctly. Please open the front-end URL (default is http://localhost:5173) to use screenshot-to-code.</h3>
```

## Your First API Call

### Example 1: Generate Code from Image (WebSocket)

```javascript
// Create WebSocket connection
const ws = new WebSocket('ws://localhost:7001/generate-code');

ws.onopen = function() {
    // Send generation parameters
    const params = {
        generatedCodeConfig: 'html_tailwind',
        inputMode: 'image',
        openAiApiKey: 'your-openai-key',
        isImageGenerationEnabled: true,
        generationType: 'create',
        // Add your base64 image data here
        imageUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    };
    
    ws.send(JSON.stringify(params));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'status':
            console.log('Status:', data.value);
            break;
        case 'chunk':
            console.log('Code chunk received');
            break;
        case 'setCode':
            console.log('Complete code:', data.value);
            break;
        case 'error':
            console.error('Error:', data.value);
            break;
    }
};
```

### Example 2: Capture Screenshot

```bash
curl -X POST "http://localhost:7001/api/screenshot" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "apiKey": "your-screenshotone-api-key"
  }'
```

### Example 3: List Available Models

```bash
curl -X GET "http://localhost:7001/models"
```

## Common Use Cases

### 1. Screenshot to Code Workflow

```python
import requests
import websockets
import asyncio
import json
import base64

class ScreenshotToCode:
    def __init__(self, base_url="http://localhost:7001"):
        self.base_url = base_url
        self.ws_url = base_url.replace('http', 'ws')
    
    def capture_screenshot(self, url, api_key):
        """Capture screenshot of a webpage"""
        response = requests.post(f"{self.base_url}/api/screenshot", json={
            "url": url,
            "apiKey": api_key
        })
        return response.json()["url"]
    
    async def generate_code(self, image_data_url, stack="html_tailwind"):
        """Generate code from image using WebSocket"""
        uri = f"{self.ws_url}/generate-code"
        
        async with websockets.connect(uri) as websocket:
            # Send parameters
            params = {
                "generatedCodeConfig": stack,
                "inputMode": "image",
                "openAiApiKey": "your-openai-key",
                "imageUrl": image_data_url,
                "isImageGenerationEnabled": True,
                "generationType": "create"
            }
            
            await websocket.send(json.dumps(params))
            
            # Collect generated code
            generated_code = ""
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "chunk":
                    generated_code += data["value"]
                elif data["type"] == "setCode":
                    return data["value"]
                elif data["type"] == "error":
                    raise Exception(f"Generation error: {data['value']}")
    
    async def url_to_code(self, url, screenshot_api_key, stack="html_tailwind"):
        """Complete workflow: URL -> Screenshot -> Code"""
        # Step 1: Capture screenshot
        print(f"Capturing screenshot of {url}...")
        image_data_url = self.capture_screenshot(url, screenshot_api_key)
        
        # Step 2: Generate code
        print("Generating code from screenshot...")
        code = await self.generate_code(image_data_url, stack)
        
        return code

# Usage
async def main():
    converter = ScreenshotToCode()
    
    try:
        code = await converter.url_to_code(
            url="https://example.com",
            screenshot_api_key="your-screenshotone-key",
            stack="html_tailwind"
        )
        
        # Save generated code
        with open("generated_page.html", "w") as f:
            f.write(code)
        
        print("Code generated and saved to generated_page.html")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(main())
```

### 2. Batch Code Generation

```python
import asyncio
import json
from pathlib import Path

async def batch_generate_codes(image_folder, output_folder):
    """Generate code for multiple images"""
    
    # Get list of available models
    response = requests.get("http://localhost:7001/models")
    available_models = response.json()["models"]
    
    # Run batch evaluation
    eval_request = {
        "models": available_models[:2],  # Use first 2 models
        "stack": "html_tailwind"
    }
    
    response = requests.post(
        "http://localhost:7001/run_evals",
        json=eval_request
    )
    
    output_files = response.json()
    print(f"Generated {len(output_files)} files")
    
    return output_files

# Usage
output_files = asyncio.run(batch_generate_codes(
    image_folder="/path/to/images",
    output_folder="/path/to/outputs"
))
```

### 3. Model Comparison

```python
def compare_models(folder1, folder2):
    """Compare outputs from two different models"""
    
    response = requests.get("http://localhost:7001/pairwise-evals", params={
        "folder1": folder1,
        "folder2": folder2
    })
    
    comparison = response.json()
    
    print(f"Comparing {comparison['folder1_name']} vs {comparison['folder2_name']}")
    print(f"Found {len(comparison['evals'])} comparable outputs")
    
    return comparison

# Usage
comparison = compare_models(
    folder1="/path/to/gpt4_outputs",
    folder2="/path/to/claude_outputs"
)
```

## Configuration Options

### Technology Stacks

| Stack | Description | Use Case |
|-------|-------------|----------|
| `html_css` | Plain HTML with CSS | Simple static websites |
| `html_tailwind` | HTML with Tailwind CSS | Modern responsive designs |
| `react_tailwind` | React components with Tailwind | Interactive web applications |
| `bootstrap` | HTML with Bootstrap | Rapid prototyping |
| `ionic_tailwind` | Ionic with Tailwind | Mobile applications |
| `vue_tailwind` | Vue.js with Tailwind | Vue-based applications |
| `svg` | SVG graphics | Icons and illustrations |

### AI Models

| Model | Provider | Best For |
|-------|----------|----------|
| `gpt-4o-2024-11-20` | OpenAI | General purpose, high quality |
| `claude-3-5-sonnet-2024-10-22` | Anthropic | Creative designs, latest features |
| `claude-3-5-sonnet-2024-06-20` | Anthropic | Reliable updates, stable |
| `gemini-2.0-flash-exp` | Google | Fast generation, experimental |

### Generation Types

- **`create`**: Generate new code from scratch (uses more creative models)
- **`update`**: Modify existing code (uses more focused models)

## Error Handling

### Common Issues and Solutions

#### 1. "No API key found"
```bash
# Solution: Set environment variables
export OPENAI_API_KEY=your-key-here
export ANTHROPIC_API_KEY=your-key-here
```

#### 2. "WebSocket connection failed"
```javascript
// Solution: Add error handling
ws.onerror = function(error) {
    console.error('WebSocket error:', error);
    // Implement retry logic
};
```

#### 3. "Rate limit exceeded"
```python
# Solution: Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

#### 4. "Invalid image format"
```python
# Solution: Ensure proper base64 encoding
import base64

def image_to_data_url(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{image_data}"
```

## Best Practices

### 1. API Key Management
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

# Never hardcode keys in source code
# ❌ Bad
api_key = "sk-1234567890abcdef"

# ✅ Good  
api_key = os.getenv('OPENAI_API_KEY')
```

### 2. WebSocket Connection Management
```javascript
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('Connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onclose = () => {
            this.handleReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
        }
    }
}
```

### 3. Image Optimization
```python
from PIL import Image
import io
import base64

def optimize_image_for_api(image_path, max_size=(1024, 1024)):
    """Optimize image for API consumption"""
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save as optimized PNG
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        
        # Convert to base64
        image_data = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_data}"
```

### 4. Response Streaming
```javascript
function handleStreamingResponse(ws) {
    let accumulatedCode = '';
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'chunk':
                accumulatedCode += data.value;
                // Update UI incrementally
                updateCodePreview(accumulatedCode);
                break;
                
            case 'setCode':
                // Final code received
                displayFinalCode(data.value);
                break;
        }
    };
}
```

## Next Steps

1. **Explore the API**: Try different technology stacks and models
2. **Build Integration**: Integrate the API into your application
3. **Run Evaluations**: Compare model performance on your use cases
4. **Optimize Performance**: Implement caching and error handling
5. **Scale Up**: Consider rate limiting and resource management

## Additional Resources

- [Code Generation API Documentation](./code-generation-api.md)
- [Screenshot API Documentation](./screenshot-api.md)
- [Evaluations API Documentation](./evaluations-api.md)
- [Complete API Reference](./api-reference.md)
- [Troubleshooting Guide](../Troubleshooting.md)

## Support

If you encounter issues:

1. Check the [Troubleshooting Guide](../Troubleshooting.md)
2. Review server logs for error details
3. Verify API key validity and permissions
4. Test with minimal examples first
5. Report bugs on the GitHub repository

Happy coding! 🚀