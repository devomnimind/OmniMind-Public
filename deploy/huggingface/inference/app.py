"""
OmniMind Inference API for Hugging Face Spaces
===========================================

This is the main application for the OmniMind inference Space on Hugging Face.
It provides a REST API for text generation using local models.

API Endpoints:
- GET / : Health check and interface
- POST /generate : Text generation endpoint
- GET /health : Health check

Author: OmniMind Team
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OmniMind Inference API",
    description="Text generation API for OmniMind autonomous AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class GenerateRequest(BaseModel):
    inputs: str
    parameters: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    generated_text: str
    model: str
    latency_ms: float

class HealthResponse(BaseModel):
    status: str
    model: str
    timestamp: float

# Global model instance (lazy loaded)
_model = None
_tokenizer = None
_model_name = "gpt2"  # Default model

def load_model():
    """Load the model and tokenizer."""
    global _model, _tokenizer

    if _model is not None:
        return

    try:
        from transformers import pipeline
        import torch

        logger.info(f"Loading model: {_model_name}")

        # Determine device (GPU if available, else CPU)
        device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Using device: {'GPU' if device == 0 else 'CPU'}")

        # Load pipeline
        _model = pipeline(
            "text-generation",
            model=_model_name,
            device=device,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            trust_remote_code=True,
        )

        logger.info(f"Model {_model_name} loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load model {_model_name}: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "OmniMind Inference API",
        "status": "running",
        "model": _model_name,
        "endpoints": {
            "generate": "POST /generate",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health() -> HealthResponse:
    """Health check endpoint."""
    try:
        # Try to load model if not loaded
        if _model is None:
            load_model()

        return HealthResponse(
            status="healthy",
            model=_model_name,
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/generate")
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate text from input prompt."""
    try:
        # Load model if not loaded
        if _model is None:
            load_model()

        start_time = time.time()

        # Extract parameters
        params = request.parameters or {}
        max_new_tokens = params.get("max_new_tokens", 50)
        temperature = params.get("temperature", 0.7)
        do_sample = params.get("do_sample", True)
        top_p = params.get("top_p", 0.9)

        logger.info(f"Generating text for input: {request.inputs[:50]}...")

        # Generate text
        outputs = _model(
            request.inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            top_p=top_p,
            pad_token_id=_model.tokenizer.eos_token_id,
            return_full_text=False,
        )

        # Extract generated text
        if isinstance(outputs, list) and outputs:
            generated_text = outputs[0].get("generated_text", "")
        else:
            generated_text = str(outputs)

        latency = (time.time() - start_time) * 1000

        logger.info(f"Generated text in {latency:.2f}ms")

        return GenerateResponse(
            generated_text=generated_text.strip(),
            model=_model_name,
            latency_ms=latency
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    # Get port from environment (Hugging Face Spaces sets this)
    port = int(os.environ.get("PORT", 7860))

    logger.info(f"Starting OmniMind Inference API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)