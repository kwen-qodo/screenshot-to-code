# Evaluations API

The Evaluations API provides comprehensive tools for testing, comparing, and analyzing the quality of generated HTML outputs. It supports single folder evaluations, pairwise comparisons, and best-of-n evaluations across multiple models and configurations.

## Overview

The evaluation system helps you:
- **Test model performance** across different inputs
- **Compare outputs** from different AI models
- **Analyze quality** of generated code
- **Run batch evaluations** on multiple inputs
- **Track improvements** over time

## Endpoints

### 1. Single Folder Evaluation

#### `GET /evals`

**Description**: Retrieve evaluations from a single folder containing HTML outputs.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder` | string | Yes | Absolute path to folder containing HTML output files |

**Response**: Array of `Eval` objects

```json
[
    {
        "input": "data:image/png;base64,...",
        "outputs": ["<html>...</html>"]
    }
]
```

**Usage Example**:
```bash
curl -X GET "http://localhost:7001/evals?folder=/path/to/html/outputs"
```

---

### 2. Pairwise Comparison

#### `GET /pairwise-evals`

**Description**: Compare HTML outputs from two folders for side-by-side evaluation.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder1` | string | Yes | Path to first folder containing HTML outputs |
| `folder2` | string | Yes | Path to second folder containing HTML outputs |

**Response**:
```json
{
    "evals": [
        {
            "input": "data:image/png;base64,...",
            "outputs": ["<html>output1</html>", "<html>output2</html>"]
        }
    ],
    "folder1_name": "model_a_outputs",
    "folder2_name": "model_b_outputs"
}
```

**Usage Example**:
```bash
curl -X GET "http://localhost:7001/pairwise-evals?folder1=/path/to/outputs1&folder2=/path/to/outputs2"
```

---

### 3. Best-of-N Comparison

#### `GET /best-of-n-evals`

**Description**: Compare HTML outputs from multiple folders (3 or more) for comprehensive evaluation.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder1` | string | Yes | Path to first folder |
| `folder2` | string | Yes | Path to second folder |
| `folder3` | string | Optional | Path to third folder |
| `folderN` | string | Optional | Additional folders (folder4, folder5, etc.) |

**Response**:
```json
{
    "evals": [
        {
            "input": "data:image/png;base64,...",
            "outputs": ["<html>output1</html>", "<html>output2</html>", "<html>output3</html>"]
        }
    ],
    "folder_names": ["model_a", "model_b", "model_c"]
}
```

**Usage Example**:
```bash
curl -X GET "http://localhost:7001/best-of-n-evals?folder1=/path/to/outputs1&folder2=/path/to/outputs2&folder3=/path/to/outputs3&folder4=/path/to/outputs4"
```

---

### 4. Run Evaluations

#### `POST /run_evals`

**Description**: Execute evaluations on all input images using specified models and technology stack.

**Request Body**:
```json
{
    "models": ["string"],  // Array of model names
    "stack": "string"      // Technology stack identifier
}
```

**Response**: Array of generated output file paths
```json
[
    "/path/to/output1.html",
    "/path/to/output2.html",
    "/path/to/output3.html"
]
```

**Usage Example**:
```bash
curl -X POST "http://localhost:7001/run_evals" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4o-2024-11-20", "claude-3-5-sonnet-2024-10-22"],
    "stack": "html_tailwind"
  }'
```

---

### 5. Available Models and Stacks

#### `GET /models`

**Description**: Retrieve lists of available AI models and technology stacks for evaluation.

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

**Usage Example**:
```bash
curl -X GET "http://localhost:7001/models"
```

## Data Models

### Eval Object
```json
{
    "input": "string",      // Base64-encoded data URL of input image
    "outputs": ["string"]   // Array of HTML output strings to evaluate
}
```

### RunEvalsRequest
```json
{
    "models": ["string"],   // Array of model identifiers
    "stack": "string"       // Technology stack (html_tailwind, react_tailwind, etc.)
}
```

### PairwiseEvalResponse
```json
{
    "evals": [Eval],        // Array of evaluation objects with 2 outputs each
    "folder1_name": "string",
    "folder2_name": "string"
}
```

### BestOfNEvalsResponse
```json
{
    "evals": [Eval],        // Array of evaluation objects with N outputs each
    "folder_names": ["string"]  // Array of folder display names
}
```

## File Structure and Naming Conventions

### Input Images
- **Location**: `{EVALS_DIR}/inputs/`
- **Format**: PNG files
- **Naming**: `{base_name}.png`
- **Example**: `login_form.png`, `dashboard.png`

### Output HTML Files
- **Location**: Any folder you specify
- **Format**: HTML files
- **Naming**: `{base_name}[_suffix].html`
- **Examples**: 
  - `login_form.html`
  - `login_form_gpt4.html`
  - `dashboard_claude.html`

### Matching Logic
The system matches input images with output HTML files based on the base name:
- Input: `login_form.png`
- Outputs: `login_form.html`, `login_form_v2.html`, `login_form_claude.html`

## Usage Examples

### Python Evaluation Runner

```python
import requests
import json
from pathlib import Path
from typing import List, Dict

class EvaluationRunner:
    def __init__(self, base_url: str = "http://localhost:7001"):
        self.base_url = base_url
    
    def get_available_models_and_stacks(self) -> Dict:
        """Get available models and technology stacks."""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
    
    def run_evaluations(self, models: List[str], stack: str) -> List[str]:
        """Run evaluations on specified models and stack."""
        payload = {
            "models": models,
            "stack": stack
        }
        
        response = requests.post(
            f"{self.base_url}/run_evals",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_single_folder_evals(self, folder_path: str) -> List[Dict]:
        """Get evaluations from a single folder."""
        params = {"folder": folder_path}
        response = requests.get(f"{self.base_url}/evals", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_pairwise_evals(self, folder1: str, folder2: str) -> Dict:
        """Get pairwise comparison evaluations."""
        params = {
            "folder1": folder1,
            "folder2": folder2
        }
        response = requests.get(f"{self.base_url}/pairwise-evals", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_best_of_n_evals(self, folders: List[str]) -> Dict:
        """Get best-of-n comparison evaluations."""
        params = {f"folder{i+1}": folder for i, folder in enumerate(folders)}
        response = requests.get(f"{self.base_url}/best-of-n-evals", params=params)
        response.raise_for_status()
        return response.json()

# Usage example
def main():
    runner = EvaluationRunner()
    
    # Get available options
    options = runner.get_available_models_and_stacks()
    print("Available models:", options["models"])
    print("Available stacks:", options["stacks"])
    
    # Run evaluations
    models_to_test = ["gpt-4o-2024-11-20", "claude-3-5-sonnet-2024-10-22"]
    output_files = runner.run_evaluations(models_to_test, "html_tailwind")
    print(f"Generated {len(output_files)} output files")
    
    # Compare results
    if len(output_files) >= 2:
        # Assuming outputs are organized in separate folders
        folder1 = "/path/to/gpt4_outputs"
        folder2 = "/path/to/claude_outputs"
        
        comparison = runner.get_pairwise_evals(folder1, folder2)
        print(f"Found {len(comparison['evals'])} comparable evaluations")

if __name__ == "__main__":
    main()
```

### JavaScript Evaluation Dashboard

```javascript
class EvaluationDashboard {
    constructor(baseUrl = 'http://localhost:7001') {
        this.baseUrl = baseUrl;
    }

    async getModelsAndStacks() {
        const response = await fetch(`${this.baseUrl}/models`);
        return await response.json();
    }

    async runEvaluations(models, stack) {
        const response = await fetch(`${this.baseUrl}/run_evals`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ models, stack })
        });
        return await response.json();
    }

    async getPairwiseComparison(folder1, folder2) {
        const params = new URLSearchParams({ folder1, folder2 });
        const response = await fetch(`${this.baseUrl}/pairwise-evals?${params}`);
        return await response.json();
    }

    async getBestOfNComparison(folders) {
        const params = new URLSearchParams();
        folders.forEach((folder, index) => {
            params.append(`folder${index + 1}`, folder);
        });
        
        const response = await fetch(`${this.baseUrl}/best-of-n-evals?${params}`);
        return await response.json();
    }

    // Render evaluation results in HTML
    renderEvaluations(evals, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        evals.forEach((eval, index) => {
            const evalDiv = document.createElement('div');
            evalDiv.className = 'evaluation-item';
            evalDiv.innerHTML = `
                <div class="eval-header">
                    <h3>Evaluation ${index + 1}</h3>
                </div>
                <div class="eval-content">
                    <div class="input-section">
                        <h4>Input Image</h4>
                        <img src="${eval.input}" alt="Input" style="max-width: 300px;">
                    </div>
                    <div class="outputs-section">
                        <h4>Generated Outputs</h4>
                        ${eval.outputs.map((output, outputIndex) => `
                            <div class="output-item">
                                <h5>Output ${outputIndex + 1}</h5>
                                <iframe srcdoc="${output.replace(/"/g, '&quot;')}" 
                                        style="width: 100%; height: 400px; border: 1px solid #ccc;">
                                </iframe>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            container.appendChild(evalDiv);
        });
    }
}

// Usage
const dashboard = new EvaluationDashboard();

async function setupEvaluationDashboard() {
    // Get available options
    const options = await dashboard.getModelsAndStacks();
    
    // Populate model selection dropdown
    const modelSelect = document.getElementById('model-select');
    options.models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    
    // Run comparison
    const comparison = await dashboard.getPairwiseComparison(
        '/path/to/folder1',
        '/path/to/folder2'
    );
    
    // Render results
    dashboard.renderEvaluations(comparison.evals, 'evaluation-results');
}
```

### Bash Script for Batch Evaluation

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:7001"
MODELS=("gpt-4o-2024-11-20" "claude-3-5-sonnet-2024-10-22")
STACK="html_tailwind"
OUTPUT_DIR="/path/to/evaluation/outputs"

# Function to run evaluations
run_evaluations() {
    echo "Running evaluations with models: ${MODELS[@]}"
    echo "Using stack: $STACK"
    
    # Create JSON payload
    MODELS_JSON=$(printf '%s\n' "${MODELS[@]}" | jq -R . | jq -s .)
    PAYLOAD=$(jq -n \
        --argjson models "$MODELS_JSON" \
        --arg stack "$STACK" \
        '{models: $models, stack: $stack}')
    
    # Run evaluations
    curl -X POST "$BASE_URL/run_evals" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        -o evaluation_results.json
    
    echo "Evaluation results saved to evaluation_results.json"
}

# Function to compare results
compare_results() {
    local folder1="$1"
    local folder2="$2"
    
    echo "Comparing results from $folder1 and $folder2"
    
    curl -X GET "$BASE_URL/pairwise-evals" \
        -G \
        --data-urlencode "folder1=$folder1" \
        --data-urlencode "folder2=$folder2" \
        -o comparison_results.json
    
    echo "Comparison results saved to comparison_results.json"
}

# Function to get available models
get_models() {
    echo "Getting available models and stacks..."
    
    curl -X GET "$BASE_URL/models" \
        -o available_models.json
    
    echo "Available models saved to available_models.json"
    cat available_models.json | jq .
}

# Main execution
case "$1" in
    "run")
        run_evaluations
        ;;
    "compare")
        if [ $# -ne 3 ]; then
            echo "Usage: $0 compare <folder1> <folder2>"
            exit 1
        fi
        compare_results "$2" "$3"
        ;;
    "models")
        get_models
        ;;
    *)
        echo "Usage: $0 {run|compare|models}"
        echo "  run                    - Run evaluations"
        echo "  compare <f1> <f2>      - Compare two folders"
        echo "  models                 - List available models"
        exit 1
        ;;
esac
```

## Best Practices

### 1. Organizing Evaluation Data

```
evaluations/
├── inputs/
│   ├── login_form.png
│   ���── dashboard.png
│   └── checkout.png
├── outputs/
│   ├── gpt4_html_tailwind/
│   │   ├── login_form.html
│   │   ├── dashboard.html
│   │   └── checkout.html
│   ├── claude_html_tailwind/
│   │   ├── login_form.html
│   │   ├── dashboard.html
│   │   └── checkout.html
│   └── comparison_results/
│       ├── pairwise_gpt4_vs_claude.json
│       └── best_of_n_all_models.json
```

### 2. Evaluation Workflow

1. **Prepare Input Images**: Place test images in the inputs directory
2. **Run Evaluations**: Use `/run_evals` to generate outputs for multiple models
3. **Organize Outputs**: Sort generated files into model-specific folders
4. **Compare Results**: Use pairwise or best-of-n endpoints for comparison
5. **Analyze Results**: Review generated HTML and identify patterns
6. **Iterate**: Adjust models, stacks, or inputs based on findings

### 3. Quality Metrics

Consider tracking these metrics:
- **Visual Similarity**: How closely does the output match the input?
- **Code Quality**: Is the generated HTML clean and semantic?
- **Responsiveness**: Does the output work on different screen sizes?
- **Accessibility**: Are proper ARIA labels and semantic elements used?
- **Performance**: How fast does the generated code load and render?

### 4. Error Handling

```python
def safe_evaluation_run(runner, models, stack):
    try:
        results = runner.run_evaluations(models, stack)
        return results
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("Invalid parameters provided")
        elif e.response.status_code == 404:
            print("Folder not found")
        elif e.response.status_code == 500:
            print("Server error during evaluation")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        raise
```

### 5. Performance Considerations

- **Batch Size**: Run evaluations in reasonable batches to avoid timeouts
- **Parallel Processing**: The system runs multiple models in parallel
- **Storage**: Generated HTML files can be large; plan storage accordingly
- **API Limits**: Respect rate limits of underlying AI services
- **Caching**: Cache results to avoid re-running expensive evaluations

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/evaluation.yml
name: Model Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start evaluation service
        run: docker-compose up -d
        
      - name: Wait for service
        run: sleep 30
        
      - name: Run evaluations
        run: |
          curl -X POST "http://localhost:7001/run_evals" \
            -H "Content-Type: application/json" \
            -d '{"models": ["gpt-4o-2024-11-20"], "stack": "html_tailwind"}' \
            -o results.json
            
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: results.json
```

This comprehensive evaluation system enables systematic testing and comparison of AI-generated code outputs, helping you optimize model selection and improve generation quality over time.