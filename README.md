# Multiplayer Number Game Backend 🎮🌍

A real-time multiplayer-style game backend built with FastAPI, featuring:

- Number Guess Game (1–100)
- Bulls & Cows Game (4 unique digits)
- Lives ♥️ & attempts tracking
- Leaderboard with ranking
- Global Chat Room (WebSocket)
- JWT authentication & secure login

This project is fully modular and production-ready for learning, portfolio, or deployment purposes.

---

## Features

### 🔐 User Authentication
- Register / Login with username & password
- JWT token-based authentication
- Secure password hashing (bcrypt)
- Track scores and wins per user

### 🎯 Games
- Number Guess
    - Guess the number 1–100
    - Lives ♥️ decrease with each wrong attempt
    - Win → points added
- Bulls & Cows
    - Guess 4 unique digits
    - Receive bulls & cows hints
    - Lives ♥️ tracking & scoring

### 🏆 Leaderboard
- Global ranking by score
- Top 10 players displayed
- Points based on:
    - Wins: +50 pts
    - Remaining lives bonus: +5 pts per life
    - Attempts efficiency

### 🌍 Global Chat Room
- Real-time WebSocket chat
- All logged-in users can send/receive messages
- System messages (rank updates, wins) can be pushed
- Fun, interactive multiplayer feel

### ❤️ Lives System
- Each game has limited lives
- Wrong guesses reduce lives
- Game over if lives = 0
- Win bonuses depend on remaining lives

---

## Project Structure

multiplayer_game/
    main.py             # Entry point, routes
    models.py           # Database models (User, Game)
    logic.py            # Game logic (Bulls & Cows, hints)
    auth.py             # JWT auth, register/login, password hashing
    chat.py             # WebSocket chat manager
    database.py         # DB setup & session
    schemas.py          # Pydantic request/response schemas
    requirements.txt    # Python dependencies
    README.md           # Project documentation

---

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy (SQLite, can upgrade to Postgres)
- WebSockets for chat
- JWT authentication
- Passlib (bcrypt hashing)

---

## Setup & Installation

1. Clone the repo:

    git clone https://github.com/yourusername/multiplayer-game.git
    cd multiplayer-game

2. Install dependencies:

    pip install -r requirements.txt

3. Run the server:

    uvicorn main:app --reload

4. Open API docs to explore endpoints:

    http://127.0.0.1:8000/docs

5. Connect to global chat WebSocket:

    ws://127.0.0.1:8000/ws/chat

---

## Usage

1. Register / Login
    - POST /register with username and password
    - POST /login to get JWT token

2. Start a Game
    - Number Guess: POST /guess/start
    - Bulls & Cows: POST /bulls-cows/start

3. Play
    - Number Guess: POST /guess/play with guess (int)
    - Bulls & Cows: POST /bulls-cows/play with guess (str, 4 unique digits)

4. Leaderboard
    - GET /leaderboard shows top 10 players

5. Global Chat
    - Connect WebSocket to /ws/chat
    - Send/receive messages in real-time

---

## Scoring System

- Win = +50 points
- Remaining lives bonus = +5 points per life
- Leaderboard ranks players by total score
- Efficient guesses = higher ranking

---

## Future Improvements

- Friends-only chat
- Daily/weekly leaderboard reset
- Additional games
- Frontend UI integration
- Redis caching for chat & leaderboard
- Mobile/web app deployment

---

## License

MIT License  
Free to use, modify, and extend.  

---

## Contact

Made with ❤️ by Kunj  
- Portfolio: [Your Portfolio URL]  
- LinkedIn: [Your LinkedIn URL]  

---

> “Play, compete, chat, and climb the leaderboard — all in one real-time multiplayer-style game backend!”