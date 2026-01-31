// ================= CONFIG =================
const BACKEND_URL = "https://multiplayer-game-1x2u.onrender.com";

// ================= GLOBAL STATE =================
let token = null;
let ws = null;
let currentGame = null;

// ================= LOGIN =================
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        alert("Username & password required");
        return;
    }

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch(`${BACKEND_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData
});

    const data = await res.json();

    if (!data.access_token) {
        alert("Login failed");
        return;
    }

    token = data.access_token;

    document.getElementById("login").style.display = "none";
    document.getElementById("dashboard").style.display = "block";

    if (ws) ws.close();
    connectChat();
}

// ================= LOGOUT =================
function logout() {
    token = null;
    currentGame = null;

    if (ws) {
        ws.close();
        ws = null;
    }

    // reset UI
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("login").style.display = "block";
    document.getElementById("chatBox").innerHTML = "";
    document.getElementById("lives").innerText = "";
    document.getElementById("attempts").innerText = "";
    document.getElementById("gameHint").innerText = "";
    document.getElementById("guessInput").value = "";

    alert("Logged out");
}

// ================= NUMBER GUESS =================
async function startNumberGuess() {
    const res = await fetch(`${BACKEND_URL}/guess/start`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await res.json();

    document.getElementById("lives").innerText = `Lives: ${data.lives}`;
    document.getElementById("attempts").innerText = "Attempts: 0";
    document.getElementById("gameHint").innerText = "Game Started! Guess a number.";

    currentGame = "guess";
}

// ================= BULLS & COWS =================
async function startBullsCows() {
    const res = await fetch(`${BACKEND_URL}/bulls-cows/start`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await res.json();

    document.getElementById("lives").innerText = `Lives: ${data.lives}`;
    document.getElementById("attempts").innerText = "Attempts: 0";
    document.getElementById("gameHint").innerText = "Game Started! Enter 4 digits.";

    currentGame = "bulls_cows";
}

// ================= MAKE GUESS =================
async function makeGuess() {
    if (!currentGame) {
        alert("Start a game first");
        return;
    }

    const guessInput = document.getElementById("guessInput");
    const guess = guessInput.value.trim();
    if (!guess) return;

    const endpoint =
        currentGame === "guess" ? "/guess/play" : "/bulls-cows/play";

    const body =
        currentGame === "guess"
            ? { guess: parseInt(guess) }
            : { guess };

    const res = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });

    const data = await res.json();

    if (data.lives !== undefined)
        document.getElementById("lives").innerText = `Lives: ${data.lives}`;

    if (data.attempts !== undefined)
        document.getElementById("attempts").innerText = `Attempts: ${data.attempts}`;

    if (data.hint)
        document.getElementById("gameHint").innerText = data.hint;

    if (data.bulls !== undefined)
        document.getElementById("gameHint").innerText =
            `Bulls: ${data.bulls}, Cows: ${data.cows}`;

    if (data.result) alert(data.result);

    guessInput.value = "";
}

// ================= CHAT =================
function connectChat() {
    ws = new WebSocket(
        `${BACKEND_URL.replace(/^http/, "ws")}/ws/chat`
    );

    ws.onopen = () => {
        console.log("✅ Chat connected");
    };

    ws.onmessage = (event) => {
        const chatBox = document.getElementById("chatBox");
        chatBox.innerHTML += event.data + "<br>";
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    ws.onerror = (e) => {
        console.error("❌ Chat error", e);
    };

    ws.onclose = () => {
        console.log("🔌 Chat disconnected");
    };
}

// ================= SEND CHAT =================
function sendChat() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();

    if (!msg || !ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(msg);

    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<b>You:</b> ${msg}<br>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    input.value = "";
}