# Number Guessing Game API 🎯

A simple REST API that lets users play a number guessing game. The API generates a random number and responds to user guesses with hints like **Too High**, **Too Low**, or **Correct**. Built with **Python** and **FastAPI**.

---

## 🚀 Features
- Random number generation  
- Guess validation via API endpoints  
- Real-time feedback  
- Easy to integrate with frontend apps, bots, or games  
- Health check for API status 

---

## 🛠 Tech Stack
- Python  
- FastAPI  
- Uvicorn  

---

## 📌 Endpoints
### 0️⃣ /health
**Method:** GET  
Check if the API is up and running.  
**Responses:**  
- 200 OK – API is healthy.  
Example: "API is running!"

### 1️⃣ /guess/{number}
**Method:** GET  
Submit a guess for the current game.  
**Path Parameter:**  
- number (integer, required) – The number you are guessing.

**Responses:**  
- 200 OK – Successful response, returns hint like "Too High", "Too Low", or "Correct".  
Example: "Too High"  
- 422 Validation Error – Invalid input (e.g., non-integer).  
Example: 
{
  "detail": [
    {
      "loc": ["path", "number"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}

### 2️⃣ /reset
**Method:** GET  
Resets the current game and generates a new random number.  
**Responses:**  
- 200 OK – Game reset successfully.  
Example: "Game has been reset. Start guessing the new number!"

## 💡 Usage
1. Check API status with `/health`  
2. Submit guesses via `/guess/{number}`  
3. Reset game anytime with `/reset`  

## 🎯 Why this project?
- Learn **REST API design**  
- Practice **game logic backend**  
- Ready for **portfolio or freelancing demos**

---

## 📄 License

MIT License

---

## 🤝 Contributing
Contributors are welcome!  
• Add more games.

---

## 👤 Author
**anshkunj**  
GitHub: https://github.com/anshkunj  
Fiverr: https://www.fiverr.com/s/xX9mNXB  
LinkedIn: https://linkedin.com/in/anshkunj 

---

## ⭐ Support
If you found this project helpful, give it a star ⭐  
It motivates me to build more real-world APIs 🚀

---

## 🔹 Note
This repository is regularly updated with new scripts and improvements.