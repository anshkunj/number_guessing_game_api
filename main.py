from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from database import Base, engine
from models import User, Game, Chat
from schemas import Register, Guess, BullsCowsGuess
from logic import generate_bulls_cows_number, check_bulls_cows
from auth import (
    get_db,
    hash_password,
    verify_password,
    create_token,
    get_current_user
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multiplayer Number Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= AUTH =================

@app.post("/register")
def register(data: Register, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username exists")

    user = User(username=data.username, password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"message": "Registered successfully"}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# ================= NUMBER GUESS =================

@app.post("/guess/start")
def start_guess(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = Game(
        user_id=user.id,
        game_type="guess",
        secret=str(random.randint(1, 100)),
        lives=7,
        attempts=0,
        status="active"
    )
    db.add(game)
    db.commit()
    return {"lives": game.lives, "attempts": 0}

@app.post("/guess/play")
def play_guess(data: Guess, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(
        user_id=user.id, game_type="guess", status="active"
    ).first()
    if not game:
        raise HTTPException(400, "No active game")

    game.attempts += 1

    if data.guess == int(game.secret):
        game.status = "won"
        user.score += 50 + game.lives * 5
        user.wins += 1
        db.commit()
        return {"result": "WIN 🎉"}

    game.lives -= 1
    if game.lives <= 0:
        game.status = "lost"
        db.commit()
        return {"result": "GAME OVER 💀", "number": game.secret}

    db.commit()
    return {
        "hint": "too low" if data.guess < int(game.secret) else "too high",
        "lives": game.lives,
        "attempts": game.attempts
    }

# ================= BULLS & COWS =================

@app.post("/bulls-cows/start")
def start_bc(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = Game(
        user_id=user.id,
        game_type="bulls_cows",
        secret=generate_bulls_cows_number(),
        lives=10,
        attempts=0,
        status="active"
    )
    db.add(game)
    db.commit()
    return {"lives": game.lives, "attempts": 0}

@app.post("/bulls-cows/play")
def play_bc(data: BullsCowsGuess, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(
        user_id=user.id, game_type="bulls_cows", status="active"
    ).first()
    if not game:
        raise HTTPException(400, "No active game")

    game.attempts += 1
    bulls, cows = check_bulls_cows(game.secret, data.guess)

    if bulls == 4:
        game.status = "won"
        user.score += 50 + game.lives * 5
        user.wins += 1
        db.commit()
        return {"result": "WIN 🎉"}

    game.lives -= 1
    if game.lives <= 0:
        game.status = "lost"
        db.commit()
        return {"result": "GAME OVER 💀", "secret": game.secret}

    db.commit()
    return {"bulls": bulls, "cows": cows, "lives": game.lives}

# ================= LEADERBOARD =================

@app.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.score.desc()).limit(10).all()
    return [
        {"rank": i+1, "username": u.username, "score": u.score, "wins": u.wins}
        for i, u in enumerate(users)
    ]

# ================= CHAT (HTTP) =================

@app.post("/chat/send")
def send_chat(msg: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = Chat(username=user.username, message=msg["message"])
    db.add(chat)
    db.commit()
    return {"status": "ok"}

@app.get("/chat/messages")
def get_chat(db: Session = Depends(get_db)):
    chats = db.query(Chat).order_by(Chat.id.desc()).limit(50).all()
    return chats[::-1]