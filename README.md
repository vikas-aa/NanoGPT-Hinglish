# NanoGPT — Hinglish AI Chatbot

A production-ready full-stack AI chatbot built around a custom-trained 5.24M parameter NanoGPT model.  
The model was trained from scratch on Roman Hinglish conversational data and runs entirely **locally on CPU**.  
No OpenAI. No Gemini. No Claude. No external LLM.

---

## Architecture

```
Browser (http://localhost:3000)
  ↓  HTTP POST /api/chat
Next.js / React Frontend (frontend/)
  ↓  fetch()
Python FastAPI Backend (backend/server.py)
  ↓  generate_response()
NanoGPT model  ← checkpoints/best_nanogpt.pt
Tokenizer      ← data/tokenizer.json
  ↓
JSON response
  ↑
Next.js Chat UI
```

---

## Project Structure

```
Nano Gpt/
├── backend/
│   ├── server.py          ← FastAPI backend (main entry point)
│   └── requirements.txt   ← Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ChatLayout.tsx     ← main orchestrator
│   │   ├── ChatHeader.tsx
│   │   ├── ChatMessages.tsx
│   │   ├── LoadingMessage.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageInput.tsx
│   │   ├── Sidebar.tsx
│   │   └── WelcomeScreen.tsx
│   ├── lib/
│   │   ├── api.ts         ← HTTP client (uses NEXT_PUBLIC_API_URL)
│   │   └── storage.ts     ← localStorage conversation management
│   ├── types/
│   │   └── chat.ts        ← TypeScript types
│   ├── .env.local         ← NEXT_PUBLIC_API_URL (not committed)
│   └── package.json
│
├── checkpoints/
│   ├── best_nanogpt.pt    ← best validation checkpoint (used by chatbot)
│   └── nanogpt.pt         ← final training checkpoint
│
├── data/
│   ├── tokenizer.json     ← BPE tokenizer (vocab_size=8000)
│   ├── train.bin          ← encoded training data
│   └── val.bin            ← encoded validation data
│
├── model.py               ← NanoGPT architecture
├── chat.py                ← CLI chat (kept for testing)
├── train.py               ← training script
└── README.md
```

---

## Model Information

| Property | Value |
|---|---|
| Architecture | NanoGPT (Transformer) |
| Parameters | ~5.24 million |
| vocab_size | 8000 |
| block_size | 128 |
| n_embd | 256 |
| n_head | 4 |
| n_layer | 4 |
| dropout | 0.1 |
| Training tokens | ~36.9M |
| Best val loss | ~3.7356 |
| Device | CPU (CUDA if available) |
| Dataset | Roman Hinglish + English + Devanagari |

---

## Requirements

### Python
- Python 3.10+
- pip

### Node.js
- Node.js 18+ 
- npm

---

## Python Setup

```bash
# Activate virtual environment (from project root)
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux/macOS
```

---

## Backend Setup

```bash
# From project root, with venv active
pip install -r backend/requirements.txt
```

---

## Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
```

---

## Running Locally

### Step 1: Start the Backend

Open a terminal in the project root and run:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start the FastAPI server
uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
Device: CPU
Loading tokenizer from ...
Loading checkpoint from ...
Model loaded. Parameters: 5,243,136
NanoGPT backend ready.
```

### Step 2: Start the Frontend

Open a second terminal and run:

```bash
cd frontend
npm run dev
```

### Step 3: Open the Chat

Open your browser at: **http://localhost:3000**

---

## Environment Variables

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

This is the only variable the frontend needs. Change it for production deployment.

### Backend

```
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Set this environment variable to control which frontend origins can connect.

---

## API Endpoints

### Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "model": "NanoGPT",
  "device": "cpu"
}
```

### Chat

```
POST /api/chat
Content-Type: application/json
```

Single message:
```json
{
  "message": "Python kya hai?"
}
```

Multi-turn conversation:
```json
{
  "messages": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello!" },
    { "role": "user", "content": "Python kya hai?" }
  ],
  "max_new_tokens": 100,
  "temperature": 0.8,
  "top_k": 50
}
```

Response:
```json
{
  "response": "Python ek programming language hai..."
}
```

### Generation Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| max_new_tokens | 100 | 10–300 | Maximum tokens to generate |
| temperature | 0.8 | 0.1–1.5 | Sampling temperature |
| top_k | 50 | 1–100 | Top-K sampling |

---

## How the NanoGPT Model is Connected

1. `backend/server.py` uses Python's `sys.path` to import `model.py` and `GPTConfig`/`NanoGPT` from the project root.
2. On startup, it loads `data/tokenizer.json` using the `tokenizers` library (HuggingFace).
3. It loads `checkpoints/best_nanogpt.pt` with `torch.load()`, reads the config stored inside the checkpoint, and rebuilds the model architecture.
4. The model is set to `.eval()` mode and stays loaded for the lifetime of the server process.
5. When a `/api/chat` request arrives, the conversation is formatted as:
   ```
   <|user|>
   user message
   <|assistant|>
   ```
6. The formatted prompt is tokenized, passed to `NanoGPT.forward()`, and new tokens are sampled using temperature + top-K.
7. Generation stops when `<|user|>` is encountered or `max_new_tokens` is reached.
8. The generated tokens are decoded, cleaned, and returned.

---

## Vercel Deployment (Frontend)

The frontend is Vercel-compatible. To deploy:

1. Push the `frontend/` folder to a GitHub repository.
2. Import it in Vercel.
3. Set the environment variable in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   ```
4. Deploy.

**Important:** The frontend does not run PyTorch. The backend must be hosted separately (see below).

---

## Backend Deployment

The FastAPI + PyTorch backend must be hosted on a server that supports Python and PyTorch.

**Recommended options:**
- Railway.app (supports Python, can upload model file)
- Render.com (Docker support)
- Any VPS (Ubuntu + Python + uvicorn)
- Modal.app (serverless GPU/CPU Python)

**Steps:**
1. Copy the project to the server.
2. Install: `pip install -r backend/requirements.txt`
3. Set `ALLOWED_ORIGINS=https://your-frontend-domain.com`
4. Run: `uvicorn backend.server:app --host 0.0.0.0 --port 8000`

For production, run behind nginx or use gunicorn + uvicorn workers.

---

## Troubleshooting

**Backend won't start:**
- Check that `.venv` is activated.
- Check that `checkpoints/best_nanogpt.pt` exists.
- Check that `data/tokenizer.json` exists.
- Run `pip install -r backend/requirements.txt` again.

**Frontend shows "NanoGPT is currently unavailable":**
- Make sure the backend is running on port 8000.
- Check `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`.
- Check CORS: backend `ALLOWED_ORIGINS` must include `http://localhost:3000`.

**Responses are empty or very short:**
- This is a 5.24M parameter model trained on limited data. Output quality varies.
- Try increasing `max_new_tokens` in the settings panel.
- Try lowering `temperature` slightly (e.g. 0.7).

**Port already in use:**
- Change backend port: `uvicorn backend.server:app --port 8001`
- Update `.env.local`: `NEXT_PUBLIC_API_URL=http://127.0.0.1:8001`

---

## CLI Testing

The original `chat.py` is preserved for terminal testing:

```bash
# From project root, with venv active
python chat.py
```

---

## Notes

- Conversation history is stored in browser `localStorage`. Clearing browser data removes all conversations.
- The model is not retrained when users chat — it only does inference.
- The Devanagari script in training data is preserved intentionally.
