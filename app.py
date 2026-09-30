import base64
import io
import logging
import os
import threading
from flask import Flask, jsonify, render_template, request
import torch
from diffusers import StableDiffusionPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Model configuration
MODEL_ID = "runwayml/stable-diffusion-v1-5"
DEFAULT_INFERENCE_STEPS = 20
DEFAULT_GUIDANCE_SCALE = 7.5

# Device configuration (CUDA GPU if available, CPU fallback)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

logger.info(f"Target execution device: {DEVICE} (torch_dtype: {TORCH_DTYPE})")

# Thread-safe pipeline singleton
_pipeline = None
_pipeline_lock = threading.Lock()
_pipeline_error = None


def get_pipeline():
    """Thread-safe lazy loader for StableDiffusionPipeline."""
    global _pipeline, _pipeline_error

    if _pipeline is not None:
        return _pipeline, None
    if _pipeline_error is not None:
        return None, _pipeline_error

    with _pipeline_lock:
        if _pipeline is not None:
            return _pipeline, None

        logger.info(f"Loading Stable Diffusion model: {MODEL_ID} on {DEVICE}...")
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_ID,
                torch_dtype=TORCH_DTYPE
            )
            pipe = pipe.to(DEVICE)

            # Enable memory optimization if running on CPU or memory-constrained GPU
            if hasattr(pipe, "enable_attention_slicing"):
                pipe.enable_attention_slicing()

            _pipeline = pipe
            logger.info("Stable Diffusion pipeline initialized successfully.")
            return _pipeline, None
        except Exception as e:
            _pipeline_error = str(e)
            logger.error(f"Failed to initialize Stable Diffusion pipeline: {e}", exc_info=True)
            return None, _pipeline_error


@app.route("/", methods=["GET"])
def index():
    """Render the main user interface."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    Generate an image from the provided text prompt.
    Supports both JSON API requests and standard HTML form submissions.
    """
    # Parse prompt from JSON body or Form data
    is_json_request = request.is_json
    if is_json_request:
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
    else:
        prompt = (request.form.get("prompt") or "").strip()

    # Validate prompt input
    if not prompt:
        err_msg = "Please enter a descriptive prompt to generate an image."
        if is_json_request:
            return jsonify({"status": "error", "error": err_msg}), 400
        return render_template("index.html", error=err_msg), 400

    # Retrieve or initialize the Stable Diffusion model
    pipeline, err = get_pipeline()
    if err or pipeline is None:
        user_err = "The AI model is currently unavailable or failed to initialize. Please try again later."
        logger.error(f"Model retrieval error: {err}")
        if is_json_request:
            return jsonify({"status": "error", "error": user_err}), 503
        return render_template("index.html", error=user_err, prompt=prompt), 503

    # Generate image
    try:
        logger.info(f"Generating image for prompt: '{prompt}' (device: {DEVICE}, steps: {DEFAULT_INFERENCE_STEPS})")
        with torch.inference_mode():
            result = pipeline(
                prompt=prompt,
                num_inference_steps=DEFAULT_INFERENCE_STEPS,
                guidance_scale=DEFAULT_GUIDANCE_SCALE
            )
            image = result.images[0]

        # Convert PIL Image to base64 Data URI in-memory
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_uri = f"data:image/png;base64,{img_base64}"

        logger.info("Image generation complete.")

        if is_json_request:
            return jsonify({
                "status": "success",
                "image": data_uri,
                "prompt": prompt
            })

        return render_template("index.html", image=data_uri, prompt=prompt)

    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        user_err = "An error occurred during image generation. Please try again with a different prompt."
        if is_json_request:
            return jsonify({"status": "error", "error": user_err}), 500
        return render_template("index.html", error=user_err, prompt=prompt), 500


@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "device": DEVICE,
        "model": MODEL_ID
    }), 200


if __name__ == "__main__":
    # Render binds port dynamically via $PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)