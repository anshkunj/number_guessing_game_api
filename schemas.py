from pydantic import BaseModel

# Auth
class Register(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

# Games
class Guess(BaseModel):
    guess: int

class BullsCowsGuess(BaseModel):
    guess: str