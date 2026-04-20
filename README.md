# JailbrokeGPT

An uncensored AI chat interface powered by Dolphin-2.9.4-Llama3.1-8B, built with Flask and React.

## Features

- 🔐 **User Authentication** - Secure login/register system with JWT tokens
- 💬 **Conversation Management** - Save, load, and manage multiple chat sessions
- 📝 **Auto Summarization** - Reduces RAM usage by condensing older messages
- 🎨 **Clean UI** - ChatGPT-inspired interface with sidebar navigation
- 🚫 **Uncensored AI** - No content guardrails for maximum coding assistance
- 💾 **MySQL Database** - Multi-user support with persistent storage
- 🖥️ **Self-Hosted** - Run entirely on your own hardware

## Tech Stack

**Backend:**
- Python 3.13
- Flask 3.0 + Flask-CORS
- llama-cpp-python 0.3.16 (CPU inference)
- SQLAlchemy 2.0 + PyMySQL
- JWT Authentication
- bcrypt password hashing

**Frontend:**
- React 18 with TypeScript
- Vite 5 (fast development)
- Tailwind CSS 3 (styling)
- Axios (API client)

**Database:**
- MySQL 8.0+
- Tables: users, conversations, messages

## Quick Start

See **[SETUP.md](SETUP.md)** for detailed installation instructions.

### Prerequisites
- MySQL installed and running
- Python 3.9+
- Node.js 18+

### Basic Setup
```bash
# 1. Create MySQL database
mysql -u root -p -e "CREATE DATABASE jailbrokegpt;"

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # Edit with your DB credentials
python -c "from models import init_db; init_db()"
python app.py

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` and register an account!

## Architecture

```
┌─────────────────────┐
│   React Frontend    │  Port 5173
│   (TypeScript)      │
└──────────┬──────────┘
           │ HTTP + JWT
           ▼
┌─────────────────────┐
│   Flask Backend     │  Port 5000
│   - Auth (JWT)      │
│   - Chat API        │
│   - Conversations   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌─────────────────┐
│  MySQL  │  │ Llama Model     │
│  DB     │  │ (llama.cpp)     │
└─────────┘  └─────────────────┘
```

## Key Features Explained

### Conversation Summarization
To keep RAM usage low, conversations are automatically summarized after 15 messages:
- Recent 5 messages kept in full context
- Older messages condensed into summary
- Model sees: `[summary] + [recent messages]`
- Enables long conversations without RAM bloat

### Authentication Flow
1. User registers/logs in → receives JWT token
2. Token stored in localStorage
3. All API requests include `Authorization: Bearer <token>`
4. Token valid for 7 days

### Model Configuration
Edit `backend/.env` to change models:
```env
MODEL_REPO=bartowski/dolphin-2.9.4-llama3.1-8b-GGUF
MODEL_FILE=dolphin-2.9.4-llama3.1-8b-Q4_K_S.gguf
```

Other recommended models:
- **Dolphin Q3_K_M** (4.0GB) - Faster, slightly less quality
- **Phi-3-mini** (2.3GB) - Smaller, good for testing
- **Mistral-7B** (4.1GB) - Alternative 7B model

## Project Structure

```
jailbrokegpt/
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── models.py              # SQLAlchemy database models
│   ├── auth.py                # JWT authentication
│   ├── routes.py              # API routes
│   ├── summarization.py       # Conversation summarization
│   ├── model_loader.py        # AI model loader
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   └── models/               # Downloaded AI models (auto-created)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # Main chat UI
│   │   │   ├── Sidebar.tsx         # Conversation list
│   │   │   ├── Login.tsx           # Auth UI
│   │   │   └── Message.tsx         # Message display
│   │   ├── App.tsx                 # Root component
│   │   └── api/
│   │       └── chat.ts             # API client (deprecated)
│   ├── package.json
│   └── vite.config.ts
├── README.md              # This file
└── SETUP.md              # Detailed setup guide
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get JWT token

### Conversations
- `GET /api/conversations` - List user's conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/:id` - Get conversation with messages
- `DELETE /api/conversations/:id` - Delete conversation
- `PATCH /api/conversations/:id/title` - Update conversation title

### Chat
- `POST /api/chat` - Send message and get AI response
  - Requires: `conversation_id`, `prompt`
  - Auto-summarizes after 15 messages
  - Auto-generates title after first exchange

## Model Information

**Currently using:** Dolphin-2.9.4-Llama3.1-8B (Q4_K_S quantization)
- **Repository:** bartowski/dolphin-2.9.4-llama3.1-8b-GGUF
- **File Size:** 4.69GB download
- **RAM Usage:** ~7-8GB during inference
- **Context Window:** 512 tokens (configurable up to 131K)
- **Inference:** CPU-only via llama.cpp
- **Training:** Uncensored fine-tune ideal for coding without restrictions

### Performance
- **First Response:** ~30-60 seconds (model loading + generation)
- **Subsequent Responses:** ~10-30 seconds on modern CPUs
- **Throughput:** ~5-10 tokens/second on Intel i5/AMD Ryzen 5

### Upgrading Models

When you upgrade your server RAM, try larger models:

**8B Models (need ~10-12GB RAM):**
- Dolphin-2.9.4-Llama3.1-8B Q4_K_M (better quality)
- Mistral-7B-Instruct Q5_K_M

**13B-24B Models (need 20GB+ RAM):**
- Xortron-24B Q4_K_S (criminology/security focused)
- Nous-Hermes-2-Yi-34B Q3_K_M

Edit `backend/.env`:
```env
MODEL_REPO=your-chosen-repo/model-name
MODEL_FILE=specific-quantization.gguf
```

## Deployment to Home Server

### Requirements
- Ubuntu/Debian server (or Windows Server)
- 16GB RAM minimum (8GB for current model + OS + MySQL)
- 20GB disk space (models + database)
- Static IP or DDNS
- Port forwarding (5000, 80/443)

### Production Checklist
- [ ] Generate secure SECRET_KEY
- [ ] Use strong MySQL passwords  
- [ ] Set up HTTPS with Let's Encrypt
- [ ] Configure firewall (ufw/iptables)
- [ ] Set up automatic backups
- [ ] Use Gunicorn/waitress for Flask
- [ ] Serve frontend with nginx
- [ ] Set up systemd service for auto-start
- [ ] Monitor logs and resource usage
- [ ] Consider rate limiting

See [SETUP.md](SETUP.md) for detailed production deployment guide.

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python app.py  # Auto-reloads disabled for Windows compatibility
```

### Frontend Development
```bash
cd frontend
npm run dev  # Hot reload enabled
```

### Database Migrations
No automated migrations yet. For schema changes:
1. Update `models.py`
2. Drop and recreate tables: `python -c "from models import Base, init_db; engine, _ = init_db(); Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"`
3. Or write manual migration SQL

## Troubleshooting

See [SETUP.md](SETUP.md) for comprehensive troubleshooting guide.

**Common Issues:**
- **"Can't connect to MySQL"** - Check MySQL is running and credentials in `.env`
- **"Invalid token"** - Login again or clear browser localStorage
- **Slow responses** - Normal for CPU inference; reduce MAX_TOKENS or use smaller model
- **Out of memory** - Close other applications or upgrade RAM

## Future Enhancements

Potential features to add:
- [ ] Markdown rendering for code blocks
- [ ] Export conversations to JSON/text
- [ ] Multi-model support (switch models per conversation)
- [ ] Voice input/output
- [ ] Fine-tuning on custom datasets
- [ ] GPU acceleration support
- [ ] Dark/light theme toggle
- [ ] Conversation sharing
- [ ] Admin panel
- [ ] API rate limiting

## Contributing

This is a personal project, but feel free to fork and customize!

## Security Disclaimer

This application runs AI models locally without content filtering. You are responsible for:
- Complying with local laws regarding AI usage
- Securing your deployment
- Not using for illegal activities  
- Understanding model outputs may be inaccurate or biased

## License

MIT License - See LICENSE file

## Author

Built by Peter Surowski | Copyright 2026

---

**Need help?** Check [SETUP.md](SETUP.md) or create an issue on GitHub.
