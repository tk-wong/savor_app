# Savor

Savor is a mobile application for recipe creation and chat-assisted cooking workflows.

## Components

1. Database and database tooling (PostgreSQL + pgAdmin)
2. Backend API (Flask)
3. Frontend app (Expo React Native)
4. AI cooking agent service (Flask + LangChain + Ollama)
5. Image generation service (Flask + Diffusers)

## Global Build Requirements

- Docker Desktop (for PostgreSQL and pgAdmin)
- Python 3.13 (backend, image generation service)
- Python 3.12+ (AI cooking agent)
- Node.js 20+ and npm (frontend)
- uv (recommended Python package/dependency manager)
- Ollama (required by AI cooking agent)

Optional:

- CUDA-capable GPU for faster image generation

## Build Order (Recommended)

1. Start database services with Docker Compose.
2. Build and run AI cooking agent.
3. Build and run image generation service.
4. Build and run backend API.
5. Build and run frontend.

## Helper Scripts

Path: ./

Two convenience scripts are provided at the project root:

- `start.sh`: starts db + pgAdmin (Docker), backend, ngrok, AI cooking agent, and image generation service.
- `stop.sh`: stops backend/AI/image/ngrok processes and then runs `docker compose down`.

Make scripts executable (one-time):

```bash
chmod u+x start.sh stop.sh
```

### Start all core services

```bash
./start.sh
```

What it starts:

- PostgreSQL on `54321` and pgAdmin on `8888`
- Backend API on `5000`
- AI cooking agent on `5010`
- Image generation service on `5020`
- ngrok tunnel for backend (`ngrok http 5000`)

### Service logs

`start.sh` writes service logs to `./logs/`:

- `logs/backend.log`
- `logs/ngrok.log`
- `logs/ai_agent.log`
- `logs/image_gen.log`

Watch all logs live:

```bash
tail -f logs/*.log
```

Note:

- ANSI color/control escape sequences are stripped before writing to these log files.

Docker logs (db and pgAdmin) are separate:

```bash
docker compose logs -f db pgadmin
```

### Stop all core services

```bash
./stop.sh
```

This script stops listeners on ports `5000`, `5010`, and `5020`, stops the ngrok process, then shuts down compose services.

## 1) Database and pgAdmin

Path: ./

### Build requirements

- Docker Desktop running
- Root env file: .db-env

Current .db-env keys used by Docker Compose:

- POSTGRES_USER
- POSTGRES_PASSWORD
- PGDATA
- PGADMIN_DEFAULT_EMAIL
- PGADMIN_DEFAULT_PASSWORD

### Build and run procedure

```powershell
docker compose up -d db pgadmin
docker compose ps
```

Exposed ports:

- PostgreSQL: 54321 (host) -> 5432 (container)
- pgAdmin: 8888

## 2) Backend API (Flask)

Path: ./backend

### Build requirements

- Python 3.13+
- uv
- PostgreSQL running (from Step 1)
- Backend env file: backend/backend/.env_dev

Required backend env keys (in backend/backend/.env_dev):

- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- DB_NAME
- SECRET_KEY (optional, random fallback exists)

Service endpoint env keys read by backend config (optional):

- AI_COOKING_AGENT_HOST (default: localhost)
- AI_COOKING_AGENT_PORT (default: 5010)
- IMAGE_GENERATION_HOST (default: localhost)
- IMAGE_GENERATION_PORT (default: 5020)
- MOCK_AI_MODELS (default: 0, meaning real models are used)
- MOCK_IMAGE_URL (default: static/images/temp.png, which is used for testing and mock mode)

Important port note:

- If backend runs on host and database is from docker-compose, set DB_PORT=54321.

### Build and run procedure

```powershell
cd backend
uv venv
uv sync
uv run python backend/main.py
```

Backend default bind:

- URL: http://\<ip-address\>:5000
- replace \<ip-address\> with localhost for local access or server IP.

### Run tests

```powershell
cd backend
uv run pytest
```

## 3) Frontend (Expo React Native)

Path: ./frontend

### Build requirements

- Node.js 20+
- npm
- Expo-compatible Android/iOS/web environment
- Frontend env file with backend URL

Required frontend env keys:

- EXPO_PUBLIC_BACKEND_URL (used by frontend/src/api/client.ts)

Example frontend env file:

```dotenv
EXPO_PUBLIC_BACKEND_URL=http://127.0.0.1:5000/api
```

### Build and run procedure

```powershell
cd frontend
npm install
npm run start
```

Common targets:

```powershell
npm run android
npm run ios
npm run web
```

### Test and lint

```powershell
npm run test
npm run lint
```

## 4) AI Cooking Agent Service

Path: ./models/AI_cooking_agent

### Build requirements

- Python 3.12+
- uv
- Ollama installed and running
- PostgreSQL access (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

The service initializes:

- OllamaLLM model: qwen3:1.7b
- OllamaLLM model: qwen3:0.6b
- Ollama embedding model: qwen3-embedding:0.6b

Make sure these are available in Ollama before startup.

Optional env keys:

- DROP_TABLES_ON_INIT (default: false)

### Build and run procedure

```powershell
cd models/AI_cooking_agent
uv venv
uv sync
uv run python main.py
```

Service bind:

- URL: http://\<ip-address\>:5010
    -  replace \<ip-address\> with localhost for local access or server IP.
- Endpoint: POST /recipe_generation

## 5) Image Generation Service

link to fine-tuned LoRA parameters: https://huggingface.co/wongtk/savor-image-generation-model

Path: ./models/image_generation_model

### Build requirements

- Python 3.13+
- uv
- Recommended: CUDA GPU for practical inference speed


### Build and run procedure (local Python)

```powershell
cd models/image_generation_model
uv venv
uv sync
uv run python main.py
```

Service bind:

- URL: http://\<ip-address\>:5020
    -  replace \<ip-address\> with localhost for local access or server IP.
- Endpoint: POST /create_image

### Build and run procedure (Docker)

```powershell
cd models/image_generation_model
docker build -t savor-image-service .
docker run --rm -p 5020:5020 -e HF_TOKEN=<your_hf_token> savor-image-service
```

## Full System Startup Checklist

1. Start db and pgAdmin with docker compose.
2. Confirm DB connection settings in backend/backend/.env_dev and AI agent env.
3. Start AI cooking agent on port 5010.
4. Start image generation service on port 5020.
5. Start backend on port 5000.
6. Set EXPO_PUBLIC_BACKEND_URL in frontend env.
7. Start frontend using Expo.
