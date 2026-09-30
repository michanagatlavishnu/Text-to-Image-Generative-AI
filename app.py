import base64
import io
import logging
import os
import re
from flask import Flask, jsonify, render_template, request
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Model configuration for Hugging Face Inference Providers
MODEL_ID = os.environ.get("HF_MODEL", "black-forest-labs/FLUX.1-schnell")


def sanitize_error(message: str) -> str:
    """Mask any accidental tokens or sensitive keys from error messages."""
    return re.sub(r"hf_[a-zA-Z0-9]+", "hf_***", message)


@app.route("/", methods=["GET"])
def index():
    """Render the main user interface."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Render service monitoring."""
    hf_token_set = bool(os.environ.get("HF_TOKEN"))
    return jsonify({
        "status": "healthy",
        "model": MODEL_ID,
        "provider": "huggingface-inference-providers",
        "token_configured": hf_token_set
    }), 200


@app.route("/generate", methods=["POST"])
def generate():
    """
    Generate an image using Hugging Face Inference Providers.
    Always returns valid JSON for both successful responses and errors.
    """
    # 1. Parse prompt from JSON payload or Form data
    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
    else:
        prompt = (request.form.get("prompt") or "").strip()

    # 2. Validate prompt
    if not prompt:
        return jsonify({
            "status": "error",
            "error": "Please enter a descriptive prompt to generate an image."
        }), 400

    # 3. Check for required Hugging Face Token
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token or not hf_token.strip():
        logger.warning("Generation requested but HF_TOKEN environment variable is not set.")
        return jsonify({
            "status": "error",
            "error": "Hugging Face token is not configured"
        }), 500

    # 4. Generate image using Hugging Face InferenceClient
    try:
        logger.info(f"Generating image with model '{MODEL_ID}' for prompt: '{prompt}'")
        client = InferenceClient(provider="auto", token=hf_token.strip())

        # Call text_to_image which returns a PIL Image
        image = client.text_to_image(prompt=prompt, model=MODEL_ID)

        # Convert PIL Image to PNG bytes and base64 Data URI
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_uri = f"data:image/png;base64,{img_base64}"

        logger.info("Image successfully generated and encoded.")

        return jsonify({
            "status": "success",
            "image": data_uri,
            "prompt": prompt
        }), 200

    except HfHubHTTPError as e:
        status_code = getattr(e.response, "status_code", 500) if hasattr(e, "response") else 500
        logger.error(f"Hugging Face HTTP error ({status_code}): {e}")

        if status_code == 401:
            err_msg = "Invalid or unauthorized Hugging Face token. Please verify that your HF_TOKEN has Inference Providers permission."
        elif status_code == 429:
            err_msg = "Hugging Face rate limit or quota exceeded. Please wait a moment and try again."
        elif status_code == 503:
            err_msg = "The AI model is currently busy or loading on Hugging Face. Please try again shortly."
        else:
            err_msg = f"Image generation failed: {sanitize_error(str(e))}"

        return jsonify({
            "status": "error",
            "error": err_msg
        }), 502

    except Exception as e:
        safe_msg = sanitize_error(str(e))
        logger.error(f"Image generation failed with unexpected error: {safe_msg}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": f"Image generation failed: {safe_msg}"
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """Return JSON for API 404s or fallback."""
    if request.path == "/generate":
        return jsonify({"status": "error", "error": "Endpoint not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Ensure internal errors return valid JSON on API endpoints."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "status": "error",
        "error": "An internal server error occurred. Please try again later."
    }), 500


if __name__ == "__main__":
    # Render binds dynamically via $PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)