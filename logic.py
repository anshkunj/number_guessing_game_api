import random

def generate_bulls_cows_number() -> str:
    """
    Generate a 4-digit number with unique digits
    and first digit non-zero.
    Example: 5827
    """
    digits = list("0123456789")
    first = random.choice(digits[1:])  # non-zero first digit
    digits.remove(first)

    remaining = random.sample(digits, 3)
    return first + "".join(remaining)


def check_bulls_cows(secret: str, guess: str) -> tuple[int, int]:
    """
    Compare secret and guess.
    Bulls = correct digit at correct position
    Cows  = correct digit at wrong position
    """
    bulls = sum(
        1 for i in range(4)
        if guess[i] == secret[i]
    )

    cows = sum(
        1 for ch in guess
        if ch in secret
    ) - bulls

    return bulls, cows