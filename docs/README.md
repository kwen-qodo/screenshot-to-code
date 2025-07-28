# Screenshot-to-Code API Documentation

This documentation provides comprehensive information about the Screenshot-to-Code API endpoints, their structure, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
   - [Home](#home)
   - [Code Generation](#code-generation)
   - [Screenshot Capture](#screenshot-capture)
   - [Evaluations](#evaluations)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)

## Overview

The Screenshot-to-Code API is a FastAPI-based service that converts screenshots and images into functional code using AI models. It supports multiple technology stacks and provides evaluation capabilities for comparing generated outputs.

## Base URL

```
http://localhost:7001
```

## Authentication

Most endpoints require API keys for AI services:
- **OpenAI API Key**: Required for GPT models
- **Anthropic API Key**: Required for Claude models
- **Screenshot API Key**: Required for screenshot capture functionality

API keys can be provided either through environment variables or in request parameters.

## API Endpoints

### Home

#### GET /
**Description**: Health check endpoint to verify the backend is running.

**Response**: HTML content indicating the backend status.

**Example**:
```bash
curl -X GET "http://localhost:7001/"
```

**Response**:
```html
<h3>Your backend is running correctly. Please open the front-end URL (default is http://localhost:5173) to use screenshot-to-code.</h3>
```

---

### Code Generation

#### WebSocket /generate-code
**Description**: Real-time code generation from images or videos using AI models.

**Protocol**: WebSocket

**Parameters** (sent as JSON):
- `generatedCodeConfig` (string, required): Technology stack to use
  - Options: `"html_css"`, `"html_tailwind"`, `"react_tailwind"`, `"bootstrap"`, `"ionic_tailwind"`, `"vue_tailwind"`, `"svg"`
- `inputMode` (string, required): Type of input
  - Options: `"image"`, `"video"`
- `openAiApiKey` (string, optional): OpenAI API key
- `anthropicApiKey` (string, optional): Anthropic API key
- `openAiBaseURL` (string, optional): Custom OpenAI base URL
- `isImageGenerationEnabled` (boolean, optional): Enable image generation (default: true)
- `generationType` (string, optional): Type of generation
  - Options: `"create"`, `"update"` (default: `"create"`)

**WebSocket Messages**:
- **Outgoing** (client to server): Parameters object
- **Incoming** (server to client): 
  - `{"type": "status", "value": "message", "variantIndex": 0}`
  - `{"type": "chunk", "value": "code_chunk", "variantIndex": 0}`
  - `{"type": "setCode", "value": "complete_code", "variantIndex": 0}`
  - `{"type": "error", "value": "error_message", "variantIndex": 0}`

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:7001/generate-code');

ws.onopen = function() {
    // Send parameters
    ws.send(JSON.stringify({
        generatedCodeConfig: "html_tailwind",
        inputMode: "image",
        openAiApiKey: "your-openai-key",
        isImageGenerationEnabled: true,
        generationType: "create",
        // Include image data and other parameters
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(`${data.type}: ${data.value} (variant ${data.variantIndex})`);
};
```

---

### Screenshot Capture

#### POST /api/screenshot
**Description**: Capture a screenshot of a given URL.

**Request Body**:
```json
{
    "url": "string",
    "apiKey": "string"
}
```

**Response**:
```json
{
    "url": "data:image/png;base64,..."
}
```

**Example**:
```bash
curl -X POST "http://localhost:7001/api/screenshot" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "apiKey": "your-screenshot-api-key"
  }'
```

**Response**:
```json
{
    "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
}
```

---

### Evaluations

#### GET /evals
**Description**: Retrieve evaluations from a single folder containing HTML outputs.

**Query Parameters**:
- `folder` (string, required): Path to folder containing HTML output files

**Response**: Array of evaluation objects with input images and HTML outputs.

**Example**:
```bash
curl -X GET "http://localhost:7001/evals?folder=/path/to/outputs"
```

**Response**:
```json
[
    {
        "input": "data:image/png;base64,...",
        "outputs": ["<html>...</html>"]
    }
]
```

#### GET /pairwise-evals
**Description**: Compare HTML outputs from two folders for pairwise evaluation.

**Query Parameters**:
- `folder1` (string, required): Path to first folder containing HTML outputs
- `folder2` (string, required): Path to second folder containing HTML outputs

**Response**:
```json
{
    "evals": [
        {
            "input": "data:image/png;base64,...",
            "outputs": ["<html>output1</html>", "<html>output2</html>"]
        }
    ],
    "folder1_name": "folder1",
    "folder2_name": "folder2"
}
```

**Example**:
```bash
curl -X GET "http://localhost:7001/pairwise-evals?folder1=/path/to/outputs1&folder2=/path/to/outputs2"
```

#### GET /best-of-n-evals
**Description**: Compare HTML outputs from multiple folders for best-of-n evaluation.

**Query Parameters**:
- `folder1` (string, required): Path to first folder
- `folder2` (string, required): Path to second folder
- `folder3` (string, optional): Path to third folder
- `folderN` (string, optional): Additional folders as needed

**Response**:
```json
{
    "evals": [
        {
            "input": "data:image/png;base64,...",
            "outputs": ["<html>output1</html>", "<html>output2</html>", "<html>output3</html>"]
        }
    ],
    "folder_names": ["folder1", "folder2", "folder3"]
}
```

**Example**:
```bash
curl -X GET "http://localhost:7001/best-of-n-evals?folder1=/path/to/outputs1&folder2=/path/to/outputs2&folder3=/path/to/outputs3"
```

#### POST /run_evals
**Description**: Execute evaluations on all input images using specified models.

**Request Body**:
```json
{
    "models": ["string"],
    "stack": "string"
}
```

**Response**: Array of output file paths generated during evaluation.

**Example**:
```bash
curl -X POST "http://localhost:7001/run_evals" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4o-2024-11-20", "claude-3-5-sonnet-2024-10-22"],
    "stack": "html_tailwind"
  }'
```

**Response**:
```json
[
    "/path/to/output1.html",
    "/path/to/output2.html"
]
```

#### GET /models
**Description**: Retrieve available models and technology stacks for evaluation.

**Response**:
```json
{
    "models": [
        "gpt-4o-2024-11-20",
        "claude-3-5-sonnet-2024-10-22",
        "claude-3-5-sonnet-2024-06-20",
        "gemini-2.0-flash-exp"
    ],
    "stacks": [
        "html_css",
        "html_tailwind", 
        "react_tailwind",
        "bootstrap",
        "ionic_tailwind",
        "vue_tailwind",
        "svg"
    ]
}
```

**Example**:
```bash
curl -X GET "http://localhost:7001/models"
```

---

## Data Models

### Eval
```json
{
    "input": "string",      // Base64-encoded data URL of input image
    "outputs": ["string"]   // Array of HTML output strings
}
```

### ScreenshotRequest
```json
{
    "url": "string",        // URL to capture
    "apiKey": "string"      // Screenshot service API key
}
```

### ScreenshotResponse
```json
{
    "url": "string"         // Base64-encoded data URL of captured screenshot
}
```

### RunEvalsRequest
```json
{
    "models": ["string"],   // Array of model names
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

---

## Error Handling

The API uses standard HTTP status codes and returns error messages in JSON format:

```json
{
    "detail": "Error message description"
}
```

Common error codes:
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server processing error

For WebSocket connections, errors are sent as messages:
```json
{
    "type": "error",
    "value": "Error message",
    "variantIndex": 0
}
```

---

## Technology Stacks

The API supports the following technology stacks for code generation:

- **html_css**: Plain HTML with CSS
- **html_tailwind**: HTML with Tailwind CSS
- **react_tailwind**: React components with Tailwind CSS
- **bootstrap**: HTML with Bootstrap framework
- **ionic_tailwind**: Ionic framework with Tailwind CSS
- **vue_tailwind**: Vue.js components with Tailwind CSS
- **svg**: SVG graphics generation

---

## Input Modes

- **image**: Static image input for code generation
- **video**: Video input for code generation (requires Anthropic API key)

---

## AI Models

The API supports various AI models:

### OpenAI Models
- `gpt-4o-2024-11-20`: Latest GPT-4 Omni model
- `o1-2024-12-17`: OpenAI O1 reasoning model

### Anthropic Models
- `claude-3-5-sonnet-2024-10-22`: Latest Claude 3.5 Sonnet
- `claude-3-5-sonnet-2024-06-20`: Previous Claude 3.5 Sonnet

### Google Models
- `gemini-2.0-flash-exp`: Gemini 2.0 Flash Experimental

The system automatically selects appropriate models based on available API keys and generation type (create vs update).