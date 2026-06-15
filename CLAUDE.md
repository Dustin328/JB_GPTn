# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JailbrokeGPT is a self-hosted AI chat interface (Flask + React) that runs GGUF-quantized LLMs locally via llama-cpp-python (CPU-only). It supports multi-user conversations with JWT auth and MySQL persistence.

## Repository Layout

**Important:** Despite the README describing a `backend/` / `frontend/` split, all files live at the repo root. Python backend files and React/TypeScript frontend files are co-located.

Backend files: `app.py`, `models.py`, `routes.py`, `auth.py`, `model_loader.py`, `summarization.py`, `init_db.py`, `requirements.txt`

Frontend files: `main.tsx`, `App.tsx`, `ChatInterface.tsx`, `Sidebar.tsx`, `Login.tsx`, `Message.tsx`, `base.ts`, `chat.ts` (deprecated), `index.html`, `index.css`, `vite.config.ts`, `package.json`, `tailwind.config.js`

## Commands

### Backend
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -c "from models import init_db; init_db()"  # Create DB tables
python app.py                                        # Start Flask on port 5000
```

### Frontend
```bash
npm install
npm run dev       # Vite dev server on port 5173, proxies /api/* to localhost:5000
npm run build     # TypeScript check + Vite build → dist/
npm run build:backend  # Build → ../backend/frontend_dist (for packaged/production use)
npm run lint      # ESLint (0 warnings allowed)
```

### Database schema changes (no migrations)
```bash
python -c "from models import Base, init_db; engine, _ = init_db(); Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
```

## Environment Configuration

Copy `.env.example` to `.env` (example path: repo root or `backend/.env`). Required variables:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=jailbrokegpt
SECRET_KEY=<generate with secrets.token_hex(32)>

MODEL_REPO=bartowski/dolphin-2.9.4-llama3.1-8b-GGUF
MODEL_FILE=dolphin-2.9.4-llama3.1-8b-Q4_K_S.gguf
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.9
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
```

Frontend env: set `VITE_API_BASE_URL` if the backend is not on localhost.

## Architecture

### Request flow
1. React frontend (`ChatInterface.tsx`) POSTs to `/api/chat` with `{prompt, conversation_id}`
2. `@token_required` decorator in `auth.py` validates the JWT and injects `current_user`
3. `app.py` saves the user message, checks for summarization, builds context, calls the model, saves the response
4. All conversation CRUD (list/create/get/delete/rename) is in the blueprint at `routes.py`

### Key modules

**`model_loader.py`** — `ModelLoader` class. Downloads GGUF from HuggingFace Hub into `./models/` on first run (~4.7 GB). Loads with `n_gpu_layers=0` (CPU only), `n_ctx=2048`, `n_threads=4` — these are hardcoded, not in `.env`. Stop sequences `["</s>", "User:", "Human:"]` are hardcoded in `generate()`. Change `MODEL_REPO`/`MODEL_FILE` in `.env` to swap models; restart required.

**`summarization.py`** — Three functions called from `app.py`:
- `should_summarize(conversation_id)` — returns True at ≥15 messages
- `summarize_conversation(model_loader, conversation_id)` — uses the model to condense all-but-last-5 messages into a text summary stored on `Conversation.summary`
- `get_context_for_generation(conversation_id)` — returns `"Previous summary\n...\nRecent conversation:\n..."` string used as the prompt prefix
- `auto_generate_title()` — fires after the first 2 messages, only if title is still `'New Chat'`

**`models.py`** — SQLAlchemy ORM. `get_db_session()` creates a new engine + session on every call (no connection pool). Each route/function must call `db.close()` in a `finally` block.

**`auth.py`** — `@token_required` injects `current_user` as a **kwarg** (not positional arg). Flask route variables remain positional; `current_user` comes after:
```python
def get_conversation(conversation_id, current_user):
```

### Route patterns

**Per-user isolation** — Every query for a user-owned resource must include `user_id=current_user.id` to prevent cross-user access:
```python
conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=current_user.id).first()
```

**DB session lifecycle** — All routes follow this pattern; `db.rollback()` is required on error:
```python
db = get_db_session()
try:
    # ...
    db.commit()
except Exception:
    db.rollback()
    return jsonify({'error': ...}), 500
finally:
    db.close()
```

### API endpoints

```
POST /api/auth/register       — create user (username ≥3 chars, password ≥6 chars)
POST /api/auth/login          — returns JWT
GET  /api/conversations       — list user's conversations
POST /api/conversations       — create new conversation
GET  /api/conversations/<id>  — get with messages array
DELETE /api/conversations/<id>
PATCH /api/conversations/<id>/title
POST /api/chat                — send message; triggers summarization + title generation
GET  /health
GET  /model-info
```

### Known issues to be aware of
- **`Sidebar.tsx` hardcodes `http://localhost:5000`** instead of using the `apiUrl()` helper from `base.ts`. Any deployment to a non-localhost backend will break the sidebar.
- **No connection pooling** — `get_db_session()` creates a new engine on every call. Under load this may exhaust MySQL connections.
- **No JWT refresh** — tokens expire after 7 days; users must log in again.
- **`auto_generate_title` fires at `len(conversation.messages) == 2`** but checks message count *before* the assistant message is committed, so it actually fires after the first user message is saved.

### Frontend state management
Auth state (`token`, `username`) lives in `App.tsx` via `localStorage`. `currentConversationId` is lifted to `App.tsx` and passed down. There is no global state library — prop drilling connects `App` → `Sidebar` + `ChatInterface`.

### Production build
Run `npm run build:backend` to output the frontend into `backend/frontend_dist/`. Flask's `serve_frontend` catch-all route serves `index.html` for any non-API path when that directory exists.
