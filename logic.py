import random

# Bulls & Cows generator
def generate_bulls_cows_number():
    digits = list("0123456789")
    random.shuffle(digits)
    return "".join(digits[:4])

def check_bulls_cows(secret, guess):
    bulls = sum(secret[i] == guess[i] for i in range(4))
    cows = sum(min(secret.count(d), guess.count(d)) for d in set(guess)) - bulls
    return bulls, cows