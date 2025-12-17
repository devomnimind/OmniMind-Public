# OmniMind Inference API

A REST API for text generation using local transformer models, deployed on Hugging Face Spaces.

## API Endpoints

### GET /
Returns basic API information and available endpoints.

**Response:**
```json
{
  "message": "OmniMind Inference API",
  "status": "running",
  "model": "gpt2",
  "endpoints": {
    "generate": "POST /generate",
    "health": "GET /health"
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "gpt2",
  "timestamp": 1703123456.789
}
```

### POST /generate
Generate text from a prompt.

**Request Body:**
```json
{
  "inputs": "Your prompt text here",
  "parameters": {
    "max_new_tokens": 50,
    "temperature": 0.7,
    "do_sample": true,
    "top_p": 0.9
  }
}
```

**Response:**
```json
{
  "generated_text": "Generated text response...",
  "model": "gpt2",
  "latency_ms": 1234.56
}
```

## Parameters

- `inputs` (string, required): The input prompt for text generation
- `parameters` (object, optional): Generation parameters
  - `max_new_tokens` (int, default: 50): Maximum number of tokens to generate
  - `temperature` (float, default: 0.7): Sampling temperature (0.0 to 1.0)
  - `do_sample` (bool, default: true): Whether to use sampling
  - `top_p` (float, default: 0.9): Nucleus sampling parameter

## Usage Example

```bash
curl -X POST "https://your-space.hf.space/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "The future of AI is",
    "parameters": {
      "max_new_tokens": 100,
      "temperature": 0.8
    }
  }'
```

## Model

Currently uses GPT-2 for text generation. The model runs on CPU by default, with GPU support if available on the Space hardware.

## Deployment

This API is designed to run on Hugging Face Spaces with the following configuration:

- **SDK:** Docker
- **Python:** 3.10+
- **Hardware:** CPU Upgrade recommended for better performance

## License

AGPL-3.0