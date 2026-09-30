# Text-to-Image Generative AI

A modern, production-ready web application for generating high-fidelity digital artwork and photorealistic imagery from natural language descriptions using latent diffusion models.

Built with **Flask**, **PyTorch**, and **Hugging Face Diffusers**, this application provides a sleek cyberpunk-inspired user interface for generating, previewing, and downloading images directly in the browser.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Stable Diffusion Model](#stable-diffusion-model)
- [Project Structure](#project-structure)
- [Local Installation Steps](#local-installation-steps)
- [How to Run Locally](#how-to-run-locally)
- [How to Use the Application](#how-to-use-the-application)
- [Render Deployment Instructions](#render-deployment-instructions)
  - [Build and Start Commands](#build-and-start-commands)
  - [Render Service Configuration](#render-service-configuration)
- [CPU / GPU Execution & Performance](#cpu--gpu-execution--performance)
- [Known Limitations & Hardware Considerations](#known-limitations--hardware-considerations)
- [Render Free Tier Feasibility Analysis](#render-free-tier-feasibility-analysis)

---

## Project Overview

This project bridges state-of-the-art text-to-image synthesis with an accessible web interface. Originally a standalone CLI script, it has been engineered into a container-ready web service suitable for deployment on cloud platforms such as **Render**.

Images are generated entirely in memory (buffered as base64 data URIs), eliminating unnecessary disk I/O and making the application compatible with ephemeral cloud file systems.

---

## Key Features

- **Intuitive Web UI**: Dark cyber-aesthetic interface with responsive layout for desktop, tablet, and mobile.
- **Dynamic Device Support**: Automatically selects CUDA GPU acceleration if available, seamlessly falling back to CPU.
- **In-Memory Image Streaming**: Generates and serves images via base64 encoded data without saving permanent files on disk.
- **Real-Time Generation Feedback**: Interactive loading spinner with an elapsed timer giving immediate visual feedback while the diffusion steps run.
- **One-Click Download**: Direct download button to save generated artwork locally as high-resolution PNGs.
- **Preset Inspiration Chips**: Built-in prompt suggestions for rapid testing and creative exploration.
- **Dual API Support**: Supports both modern asynchronous JSON requests (`fetch`/AJAX) and traditional HTML form submissions.
- **Production Server Ready**: Integrated with Gunicorn WSGI server and dynamic `$PORT` environment variable binding.

---

## Technologies Used

- **Language**: Python 3.10+
- **Web Framework**: [Flask](https://flask.palletsprojects.com/)
- **WSGI Server**: [Gunicorn](https://gunicorn.org/)
- **Deep Learning Framework**: [PyTorch](https://pytorch.org/) (`torch`, `torchvision`)
- **Generative AI Framework**: [Hugging Face Diffusers](https://huggingface.co/docs/diffusers) (`diffusers`, `transformers`, `accelerate`, `safetensors`)
- **Image Processing**: [Pillow](https://python-pillow.org/)
- **Frontend**: HTML5, Modern CSS (Glassmorphism, CSS Variables, Flexbox/Grid), Vanilla JavaScript (Async/Await Fetch API)

---

## Stable Diffusion Model

- **Model ID**: [`runwayml/stable-diffusion-v1-5`](https://huggingface.co/runwayml/stable-diffusion-v1-5)
- **Architecture**: Latent Diffusion Model (LDM) conditioned on text embeddings from a frozen CLIP ViT-L/14 text encoder.
- **Default Inference Parameters**:
  - `num_inference_steps`: `20` (optimized balance between visual detail and generation speed)
  - `guidance_scale`: `7.5` (controls adherence to the input text prompt)
  - `torch_dtype`: `torch.float16` when running on CUDA, `torch.float32` when running on CPU
- **Memory Optimization**: Attention slicing enabled (`pipe.enable_attention_slicing()`) to minimize peak RAM/VRAM consumption.

---

## Project Structure

```text
Text-to-Image-Generative-AI/
│
├── .gitignore              # Git ignore rules for virtual environments, caches, and media
├── app.py                  # Core Flask web application and pipeline management
├── requirements.txt        # Production Python dependencies
├── README.md               # Complete project documentation
│
├── templates/
│   └── index.html          # Cyber-themed frontend interface
│
└── generated_image*.png    # Historical sample outputs
```

---

## Local Installation Steps

### Prerequisites
- Python 3.10, 3.11, or 3.12+ installed
- Git installed
- Minimum 8 GB RAM (16 GB recommended for CPU inference) or an NVIDIA GPU with at least 4 GB VRAM

### Step 1: Clone the Repository
```bash
git clone https://github.com/michanagatlavishnu/Text-to-Image-Generative-AI.git
cd Text-to-Image-Generative-AI
```

### Step 2: Create and Activate a Virtual Environment
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note for NVIDIA GPU users**: To leverage CUDA acceleration, install the CUDA-enabled PyTorch build for your system by following instructions at [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/).

---

## How to Run Locally

### Development Server
Run the Flask application directly:
```bash
python app.py
```
By default, the server will start on:
```text
http://127.0.0.1:5000
```

### Production WSGI (Linux/macOS)
```bash
export PORT=5000
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

---

## How to Use the Application

1. Open your browser and navigate to `http://localhost:5000` (or your deployed Render URL).
2. Enter your descriptive prompt into the text area (e.g. *"A futuristic cyberpunk city at dusk with neon reflections"*), or click one of the preset inspiration chips.
3. Click **Generate Image**.
4. The generation loader will activate and track the elapsed time while the diffusion steps execute.
5. Once complete, the generated image will display on the canvas.
6. Click **Download Image** to save the generated PNG file to your computer.

---

## Render Deployment Instructions

### Service Configuration
1. Sign in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository: `michanagatlavishnu/Text-to-Image-Generative-AI`.
4. Configure the service settings as follows:

| Setting | Value |
| :--- | :--- |
| **Name** | `text-to-image-ai` (or your choice) |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Region** | Choose closest to you (e.g., Oregon, Frankfurt) |
| **Root Directory** | *(leave blank)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300` |

### Environment Variables
No custom environment variables are strictly required. Render will automatically inject the `$PORT` variable into the runtime environment.

---

## CPU / GPU Execution & Performance

- **CUDA GPU**: If an NVIDIA GPU with CUDA support is present, the pipeline executes in half-precision (`float16`). Generation time typically ranges between **2 to 8 seconds** per image.
- **CPU Mode**: If no GPU is detected, the pipeline automatically defaults to full-precision (`float32`) on the CPU. Generation time typically ranges between **60 to 180 seconds** per image depending on CPU clock speed and core count.

---

## Known Limitations & Hardware Considerations

1. **Model Size**: Stable Diffusion v1-5 requires downloading approximately 4 GB of model checkpoints during initial startup or first inference.
2. **Memory Footprint**: Running inference on CPU requires approximately **4 GB to 7 GB of RAM**.
3. **Execution Latency**: On CPU environments, HTTP requests can take up to 2–3 minutes. The Gunicorn `--timeout 300` parameter ensures the WSGI worker does not prematurely terminate slow diffusion requests.

---

## Render Free Tier Feasibility Analysis

> [!WARNING]
> **Is the Render Free Plan realistically sufficient?**
>
> **No.** The Render Free tier provides:
> - **512 MB RAM**
> - **Shared 0.1–0.5 CPU vCPU**
> - **100-second HTTP request timeout**
>
> Running `runwayml/stable-diffusion-v1-5` requires at least **4 GB to 7 GB of RAM** to load the UNet, VAE, and text encoder into system memory. On the Free tier (512 MB), the Linux kernel's Out-Of-Memory killer (`OOMKilled`) will immediately terminate the Python/Gunicorn process when attempting to load the model.
>
> **Recommended Alternatives for Cloud Hosting**:
> - **Render Paid Instances**: Standard instance with at least **8 GB RAM** (e.g., Starter Plus / Pro).
> - **GPU Cloud Platforms**: Hugging Face Spaces (T4 GPU), RunPod, Modal, Replicate, or Google Cloud Run with GPU.
> - **Hybrid Architecture**: Deploy the Flask UI on Render Free and route the `/generate` endpoint to an external serverless inference API (such as Hugging Face Inference API or Replicate).
