from fastapi import FastAPI
import random

app = FastAPI()
secret = random.randint(1,100)

@app.get("/")
def home():
    return {"message": "Guess a number between 1 and 100"}

@app.get("/guess/{number}")
def number_guess(number: int):
    global secret
    if secret < number:
        return {"result": "Too large !"}
    elif secret > number:
        return {"result": "Too small !"}
    else:
        return {"result": "Correct ✅"}

@app.get("/reset")
def reset():
    global secret
    secret = random.randint(1,100)
    return {"message": "Game reset! New secret number generated"}