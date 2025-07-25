# Screenshot API

The Screenshot API allows you to capture screenshots of web pages programmatically using the ScreenshotOne service.

## Endpoint

### `POST /api/screenshot`

**Description**: Capture a screenshot of a specified URL and return it as a base64-encoded data URL.

## Request

### Headers
```
Content-Type: application/json
```

### Request Body

```json
{
    "url": "string",      // Required: URL to capture
    "apiKey": "string"    // Required: ScreenshotOne API key
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The URL of the webpage to capture |
| `apiKey` | string | Yes | Your ScreenshotOne API key |

## Response

### Success Response

**Status Code**: `200 OK`

```json
{
    "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Base64-encoded data URL of the captured screenshot |

## Screenshot Configuration

The API automatically configures the following screenshot settings:

### Desktop Mode (Default)
- **Viewport**: 1280x832 pixels
- **Device Scale Factor**: 1
- **Format**: PNG
- **Full Page**: Yes
- **Ad Blocking**: Enabled
- **Cookie Banner Blocking**: Enabled
- **Tracker Blocking**: Enabled
- **Cache**: Disabled

### Mobile Mode
- **Viewport**: 342x684 pixels
- **Device Scale Factor**: 1
- **Format**: PNG
- **Full Page**: Yes
- **Ad Blocking**: Enabled
- **Cookie Banner Blocking**: Enabled
- **Tracker Blocking**: Enabled
- **Cache**: Disabled

*Note: Currently, the device mode is hardcoded to desktop. Mobile mode configuration is available in the code but not exposed via the API.*

## Usage Examples

### JavaScript/TypeScript

```javascript
class ScreenshotCapture {
    constructor(baseUrl = 'http://localhost:7001') {
        this.baseUrl = baseUrl;
    }

    async captureScreenshot(url, apiKey) {
        try {
            const response = await fetch(`${this.baseUrl}/api/screenshot`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    apiKey: apiKey
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.url; // Returns the base64 data URL
        } catch (error) {
            console.error('Screenshot capture failed:', error);
            throw error;
        }
    }

    // Helper method to display screenshot in an img element
    displayScreenshot(dataUrl, imgElementId) {
        const imgElement = document.getElementById(imgElementId);
        if (imgElement) {
            imgElement.src = dataUrl;
        }
    }

    // Helper method to download screenshot as file
    downloadScreenshot(dataUrl, filename = 'screenshot.png') {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Usage example
const screenshotService = new ScreenshotCapture();

async function captureAndDisplay() {
    try {
        const dataUrl = await screenshotService.captureScreenshot(
            'https://example.com',
            'your-screenshotone-api-key'
        );
        
        // Display in an img element
        screenshotService.displayScreenshot(dataUrl, 'screenshot-img');
        
        // Or download as file
        screenshotService.downloadScreenshot(dataUrl, 'example-screenshot.png');
        
    } catch (error) {
        console.error('Failed to capture screenshot:', error);
    }
}
```

### Python

```python
import requests
import base64
from typing import Optional

class ScreenshotCapture:
    def __init__(self, base_url: str = "http://localhost:7001"):
        self.base_url = base_url
    
    def capture_screenshot(self, url: str, api_key: str) -> str:
        """
        Capture a screenshot of the given URL.
        
        Args:
            url: The URL to capture
            api_key: ScreenshotOne API key
            
        Returns:
            Base64-encoded data URL of the screenshot
            
        Raises:
            requests.RequestException: If the request fails
        """
        endpoint = f"{self.base_url}/api/screenshot"
        
        payload = {
            "url": url,
            "apiKey": api_key
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # ScreenshotOne can take time
            )
            response.raise_for_status()
            
            data = response.json()
            return data["url"]
            
        except requests.RequestException as e:
            print(f"Screenshot capture failed: {e}")
            raise
    
    def save_screenshot_to_file(self, data_url: str, filename: str) -> None:
        """
        Save a base64 data URL screenshot to a file.
        
        Args:
            data_url: Base64-encoded data URL
            filename: Output filename
        """
        # Extract base64 data from data URL
        header, encoded = data_url.split(',', 1)
        image_data = base64.b64decode(encoded)
        
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"Screenshot saved to {filename}")

# Usage example
def main():
    screenshot_service = ScreenshotCapture()
    
    try:
        # Capture screenshot
        data_url = screenshot_service.capture_screenshot(
            url="https://example.com",
            api_key="your-screenshotone-api-key"
        )
        
        # Save to file
        screenshot_service.save_screenshot_to_file(
            data_url, 
            "example_screenshot.png"
        )
        
        print("Screenshot captured successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### cURL

```bash
# Basic screenshot capture
curl -X POST "http://localhost:7001/api/screenshot" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "apiKey": "your-screenshotone-api-key"
  }'

# Save response to file and extract image
curl -X POST "http://localhost:7001/api/screenshot" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "apiKey": "your-screenshotone-api-key"
  }' \
  -o screenshot_response.json

# Extract base64 data and save as image (requires jq)
cat screenshot_response.json | jq -r '.url' | sed 's/data:image\/png;base64,//' | base64 -d > screenshot.png
```

### Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

class ScreenshotCapture {
    constructor(baseUrl = 'http://localhost:7001') {
        this.baseUrl = baseUrl;
    }

    async captureScreenshot(url, apiKey) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/screenshot`, {
                url: url,
                apiKey: apiKey
            }, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 60000 // 60 second timeout
            });

            return response.data.url;
        } catch (error) {
            if (error.response) {
                console.error('Server error:', error.response.status, error.response.data);
            } else if (error.request) {
                console.error('Network error:', error.message);
            } else {
                console.error('Error:', error.message);
            }
            throw error;
        }
    }

    saveScreenshotToFile(dataUrl, filename) {
        // Extract base64 data
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, '');
        
        // Convert to buffer and save
        const buffer = Buffer.from(base64Data, 'base64');
        fs.writeFileSync(filename, buffer);
        
        console.log(`Screenshot saved to ${filename}`);
    }
}

// Usage
async function example() {
    const screenshotService = new ScreenshotCapture();
    
    try {
        const dataUrl = await screenshotService.captureScreenshot(
            'https://example.com',
            'your-screenshotone-api-key'
        );
        
        screenshotService.saveScreenshotToFile(dataUrl, 'example.png');
        
    } catch (error) {
        console.error('Screenshot failed:', error.message);
    }
}

example();
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `400 Bad Request` | Invalid URL or missing parameters | Check URL format and ensure all required fields are provided |
| `401 Unauthorized` | Invalid ScreenshotOne API key | Verify your API key is correct and active |
| `404 Not Found` | URL cannot be accessed | Ensure the target URL is accessible and valid |
| `500 Internal Server Error` | Screenshot service error | Check ScreenshotOne service status or try again later |
| `Timeout` | Request took too long | Increase timeout or try with a simpler page |

### Error Response Format

```json
{
    "detail": "Error message description"
}
```

## ScreenshotOne API Key

To use this endpoint, you need a ScreenshotOne API key:

1. **Sign up** at [ScreenshotOne](https://screenshotone.com/)
2. **Get your API key** from the dashboard
3. **Use the key** in your requests

### API Key Security

- Store API keys securely (environment variables, secure vaults)
- Don't expose keys in client-side code
- Rotate keys regularly
- Monitor usage to detect unauthorized access

## Rate Limits

The screenshot endpoint respects ScreenshotOne's rate limits:

- **Free tier**: Limited requests per month
- **Paid tiers**: Higher limits based on plan
- **Rate limit headers**: Check response headers for current usage

## Best Practices

1. **Timeout Handling**: Set appropriate timeouts (60+ seconds recommended)
2. **Error Retry**: Implement exponential backoff for failed requests
3. **Caching**: Cache screenshots when appropriate to reduce API calls
4. **URL Validation**: Validate URLs before sending requests
5. **Resource Management**: Handle large base64 responses efficiently
6. **Security**: Validate and sanitize URLs to prevent SSRF attacks

## Integration with Code Generation

The screenshot API is commonly used in conjunction with the code generation API:

```javascript
// Capture screenshot of existing site
const screenshotUrl = await screenshotService.captureScreenshot(
    'https://example.com',
    'your-api-key'
);

// Use screenshot for code generation
const ws = new WebSocket('ws://localhost:7001/generate-code');
ws.onopen = () => {
    ws.send(JSON.stringify({
        generatedCodeConfig: 'html_tailwind',
        inputMode: 'image',
        imageUrl: screenshotUrl, // Use captured screenshot
        openAiApiKey: 'your-openai-key'
    }));
};
```

This workflow allows you to:
1. Capture screenshots of existing websites
2. Generate code based on those screenshots
3. Create similar designs or layouts
4. Iterate and improve on existing designs