<<<<<<< HEAD
# Emotion-Aware Mental Health Chatbot

Production-style full-stack chatbot that detects emotion from user text, responds empathetically, tracks emotional trends, and performs crisis-risk detection.

## 1. Project Structure

Emotion Aware Chatbot/
├── .env.example
├── README.md
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── auth.py
│       ├── config.py
│       ├── database.py
│       ├── emotion.py
│       ├── main.py
│       ├── models.py
│       ├── response.py
│       └── safety.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api.js
        ├── App.jsx
        ├── main.jsx
        ├── styles.css
        └── components/
            ├── AuthForm.jsx
            ├── ChatWindow.jsx
            └── TrendChart.jsx
```

## 2. Backend Code

- FastAPI endpoints:
  - `POST /register` - User registration
  - `POST /login` - User authentication
  - `GET /profile` - Get user profile
  - `POST /chat` - Send chat message (authenticated)
  - `GET /trends` - Get emotion trends (authenticated)
  - `GET /health` - Health check
- JWT authentication with bcrypt password hashing
- Advanced emotion detection with intensity levels (low, medium, high)
- Personalized responses based on user history and preferred tone
- Enhanced crisis detection for self-harm and severe distress
- MongoDB collections: users, messages, emotions, chats, sessions

### Key backend modules

- `auth.py`: JWT token handling and password verification
- `emotion.py`: Emotion classification with intensity detection
- `response.py`: LLM-style prompt engineering for empathetic responses
- `safety.py`: Enhanced crisis detection and intervention
- `database.py`: MongoDB repository with user management
- `database.py`: MongoDB repository for history and trend data.
- `main.py`: API orchestration, validation, and error handling.

## 3. Frontend Code

- React + Vite chat app
- WhatsApp-style bubble UI
- Typing animation
- Emotion indicator (emoji + label)
- Daily check-in button
- Trend chart visualization using `recharts`
- Calls backend APIs using `fetch`

## 4. Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas or local MongoDB (URI in `.env`)
- Hugging Face token with **Inference Providers** access ([create fine-grained token](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained)) — set `HF_API_TOKEN` in `backend/.env`

### Backend setup

1. Open terminal in `backend`.
2. Create virtual environment and activate:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Copy environment file:
   - From root `.env.example` values into `backend/.env`
   - Set **`HF_API_TOKEN`** (required for emotion detection)
5. Remove old ML packages if you previously installed them:
   - `pip uninstall torch transformers -y`
6. Run API:
   - `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend setup

1. Open terminal in `frontend`.
2. Install dependencies:
   - `npm install`
3. Start frontend:
   - `npm run dev`
4. Open [http://localhost:5173](http://localhost:5173).

## Requirements.txt

Located at `backend/requirements.txt`:

- fastapi
- uvicorn[standard]
- huggingface_hub>=0.28.0
- pymongo
- python-dotenv
- pydantic-settings
- passlib[bcrypt]
- python-jose[cryptography]
- python-multipart

## Sample API Requests

### Register User

`POST http://localhost:8000/register`

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword",
  "name": "Test User"
}
```

### Login

`POST http://localhost:8000/login`

```json
{
  "username": "testuser",
  "password": "securepassword"
}
```

Response includes JWT token.

### Send Chat Message

`POST http://localhost:8000/chat` (include Authorization: Bearer <token>)

```json
{
  "message": "I feel really anxious about work today."
}
```

### Response

```json
{
  "response": "Test User, I can sense this has been emotionally heavy. That sounds really overwhelming. Let's take this one step at a time together.",
  "emotion": "fear",
  "emotion_intensity": "high",
  "risk_detected": false,
  "disclaimer": "This chatbot offers emotional support but is not a therapist and does not provide medical advice, diagnosis, or prescriptions.",
  "timestamp": "2026-04-13T..."
}
```

## Ethics Note

This chatbot is **not a therapist** and does not diagnose conditions, prescribe treatment, or replace professional care. For crisis situations, it encourages immediate contact with emergency services or a qualified local crisis helpline.

# Emotion-Aware-Chatbot
 68ea9450df779904acd535bb0b93ed8cd1f35e27
=======
# Emotion Aware Chatbot

AI-powered chatbot that detects user emotions.

## Features
- Backend API
- Frontend UI
>>>>>>> 2b1347c513fad6b58ac4f095fdfa817dc014a64f
