# AI Guardian

**Category:** AI  **Author:** Solvz

Run: `GROQ_API_KEY=... SECRET_FLAG='H7CTF{...}' docker compose up --build`, then POST to `http://localhost:5000/api/challenge` with `{"prompt": "..."}`.

The backend is a Groq `llama-3.1-8b-instant` chatbot ("SecureAI") with the flag in its system prompt. Input and output filtering live in `app/defenses.py`, the prompt is in `app/config.py`. Requests are globally rate limited (`RATE_LIMIT_SECONDS`).

Flag: set at deploy time through `SECRET_FLAG`.
