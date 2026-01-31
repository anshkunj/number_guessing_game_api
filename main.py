from fastapi import FastAPI, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
import random

# ===== Internal imports (package-style) =====
from database import Base, engine
from models import User, Game
from schemas import Register, Guess, BullsCowsGuess
from logic import generate_bulls_cows_number, check_bulls_cows
from auth import (
    get_db,
    hash_password,
    verify_password,
    create_token,
    get_current_user,
    oauth2_scheme
)
from chat import manager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

# ===== DB init =====
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multiplayer Number Game API")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= AUTH =================

@app.post("/register")
def register(data: Register, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    return {"message": "Logged out successfully. Delete token on client side."}

# ================= NUMBER GUESS GAME =================

@app.post("/guess/start")
def start_guess(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    return {
    "message": "Number Guess game started",
    "lives": game.lives,
    "attempts": 0
}

@app.post("/guess/play")
def play_guess(
    data: Guess,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(
        Game.user_id == user.id,
        Game.game_type == "guess",
        Game.status == "active"
    ).first()
    if not game:
        raise HTTPException(status_code=400, detail="No active game")

    game.attempts += 1

    if data.guess == int(game.secret):
        game.status = "won"
        bonus = game.lives * 5
        user.score += 50 + bonus
        user.wins += 1
        db.commit()
        return {
            "result": "WIN 🎉",
            "attempts": game.attempts,
            "points": 50 + bonus,
            "total_score": user.score
        }

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
def start_bulls_cows(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    return {
    "message": "Bulls & Cows started",
    "lives": game.lives,
    "attempts": 0
}

@app.post("/bulls-cows/play")
def play_bulls_cows(
    data: BullsCowsGuess,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(
        Game.user_id == user.id,
        Game.game_type == "bulls_cows",
        Game.status == "active"
    ).first()
    if not game:
        raise HTTPException(status_code=400, detail="No active game")

    if len(data.guess) != 4 or not data.guess.isdigit() or len(set(data.guess)) != 4:
        raise HTTPException(status_code=400, detail="Guess must be 4 unique digits")

    game.attempts += 1
    bulls, cows = check_bulls_cows(game.secret, data.guess)

    if bulls == 4:
        game.status = "won"
        bonus = game.lives * 5
        user.score += 50 + bonus
        user.wins += 1
        db.commit()
        return {
            "result": "WIN 🎉",
            "attempts": game.attempts,
            "points": 50 + bonus,
            "total_score": user.score
        }

    game.lives -= 1
    if game.lives <= 0:
        game.status = "lost"
        db.commit()
        return {"result": "GAME OVER 💀", "secret": game.secret}

    db.commit()
    return {
    "bulls": bulls,
    "cows": cows,
    "lives": game.lives,
    "attempts": game.attempts
}

# ================= LEADERBOARD =================

@app.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.score.desc()).limit(10).all()
    return [
        {"rank": i + 1, "username": u.username, "score": u.score, "wins": u.wins}
        for i, u in enumerate(users)
    ]

# ================= GLOBAL CHAT =================

from jose import JWTError, jwt
from auth import SECRET_KEY, ALGORITHM
from fastapi import WebSocketDisconnect

@app.websocket("/ws/chat")
async def global_chat(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise JWTError
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)