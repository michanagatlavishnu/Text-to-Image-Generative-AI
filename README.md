# Text-to-Image Generative AI

A modern, cloud-optimized web application for generating high-fidelity digital artwork and photorealistic imagery from natural language descriptions.

Built with **Flask**, **Gunicorn**, and **Hugging Face Inference Providers** via the official `huggingface_hub` Python SDK, this application delivers rapid serverless text-to-image synthesis with minimal server resource consumption—making it fully compatible with cloud platforms like **Render** (including the Free tier).

---

## Key Features

- **Intuitive Web UI**: Dark cyber-aesthetic interface with responsive layout for desktop, tablet, and mobile.
- **Serverless AI Inference**: Powered by Hugging Face Inference Providers (using `black-forest-labs/FLUX.1-schnell` by default) with automatic provider routing.
- **Zero Local GPU/VRAM Overhead**: Offloads heavy model computation to Hugging Face, running comfortably on 512 MB RAM environments without memory exhaustion.
- **In-Memory Image Streaming**: Generates and serves images via base64 encoded data URIs without writing to ephemeral cloud disks.
- **Real-Time Generation Feedback**: Interactive loading spinner with elapsed timer giving immediate visual feedback during generation.
- **One-Click Download**: Direct download button to save generated artwork locally as high-resolution PNGs.
- **Preset Inspiration Chips**: Built-in prompt suggestions for rapid testing and creative exploration.
- **Production Server Ready**: Integrated with Gunicorn WSGI server and dynamic `$PORT` environment variable binding.

---

## Technologies Used

- **Language**: Python 3.10+
- **Web Framework**: [Flask](https://flask.palletsprojects.com/)
- **WSGI Server**: [Gunicorn](https://gunicorn.org/)
- **Inference SDK**: [Hugging Face Hub (`huggingface_hub`)](https://huggingface.co/docs/huggingface_hub)
- **Image Processing**: [Pillow](https://python-pillow.org/)
- **Frontend**: HTML5, Modern CSS (Glassmorphism, CSS Variables, Flexbox/Grid), Vanilla JavaScript (Async/Await Fetch API)

---

## Project Structure

```text
Text-to-Image-Generative-AI/
│
├── .env.example            # Example environment variable template (HF_TOKEN)
├── .gitignore              # Rules ignoring pycache, virtual envs, media, and secrets
├── app.py                  # Core Flask web application using huggingface_hub.InferenceClient
├── requirements.txt        # Production Python dependencies (Flask, gunicorn, huggingface_hub, Pillow)
├── README.md               # Complete project documentation
│
├── templates/
│   └── index.html          # Responsive cyber/AI dark theme interface
│
└── generated_image*.png    # Historical sample outputs
```

---

## Local Installation Steps

### Prerequisites
- Python 3.10+ installed
- Git installed
- A Hugging Face account and User Access Token

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

### Step 4: Configure Your Hugging Face Token
Create a `.env` file or export your token in your terminal:
- **Windows PowerShell**:
  ```powershell
  $env:HF_TOKEN="your_huggingface_token_here"
  ```
- **Linux / macOS**:
  ```bash
  export HF_TOKEN="your_huggingface_token_here"
  ```

---

## How to Run Locally

Run the Flask application directly:
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## Render Deployment Instructions

### Step 1: Create a Hugging Face User Access Token
1. Go to [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens).
2. Click **Create new token**.
3. Choose token type:
   - **Fine-grained**: Ensure it has **Make calls to Inference Providers** permission enabled.
   - Or **Read** token with Inference access.
4. Copy the token securely (never commit or expose this token publicly).

### Step 2: Configure Render Web Service
1. Sign in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository: `michanagatlavishnu/Text-to-Image-Generative-AI`.
4. Configure the service settings:

| Setting | Value |
| :--- | :--- |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300` |
| **Health Check Path** | `/health` |
| **Instance Type** | Free tier is fully supported (only requires ~50 MB RAM) |

### Step 3: Add Render Environment Variable
Under the **Environment** tab in your Render Web Service settings, add:

| Key | Value |
| :--- | :--- |
| `HF_TOKEN` | `<your_huggingface_token_here>` |

*(Optional)* You may also set `HF_MODEL` if you wish to override the default text-to-image model (e.g. `black-forest-labs/FLUX.1-schnell`).

Click **Deploy Web Service**. Render will install the lightweight dependencies and start the app in seconds!
