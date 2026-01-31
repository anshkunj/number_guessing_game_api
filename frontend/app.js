const BACKEND_URL = "https://YOUR_RENDER_URL.onrender.com";

let token = null;
let currentGame = null;

// ===== LOGIN =====
async function login() {
    const u = username.value.trim();
    const p = password.value.trim();
    if (!u || !p) return alert("Fill fields");

    const fd = new URLSearchParams();
    fd.append("username", u);
    fd.append("password", p);

    const res = await fetch(BACKEND_URL + "/login", {
        method: "POST",
        headers: {"Content-Type":"application/x-www-form-urlencoded"},
        body: fd
    });
    const data = await res.json();
    if (!data.access_token) return alert("Login failed");

    token = data.access_token;
    loginBox.style.display = "none";
    dashboard.style.display = "block";

    loadLeaderboard();
    loadChat();
    setInterval(loadChat, 2000);
}

// ===== START GAME =====
async function startGame(type) {
    const ep = type==="guess"?"/guess/start":"/bulls-cows/start";
    currentGame = type;

    const res = await fetch(BACKEND_URL+ep,{
        method:"POST",
        headers:{Authorization:`Bearer ${token}`}
    });
    const d = await res.json();
    lives.innerText = "Lives: "+d.lives;
    attempts.innerText = "Attempts: "+d.attempts;
}

// ===== GUESS =====
async function makeGuess() {
    const g = guessInput.value.trim();
    if (!g) return;

    const ep = currentGame==="guess"?"/guess/play":"/bulls-cows/play";
    const body = currentGame==="guess"?{guess:+g}:{guess:g};

    const res = await fetch(BACKEND_URL+ep,{
        method:"POST",
        headers:{
            Authorization:`Bearer ${token}`,
            "Content-Type":"application/json"
        },
        body:JSON.stringify(body)
    });
    const d = await res.json();

    if(d.lives!==undefined) lives.innerText="Lives: "+d.lives;
    if(d.bulls!==undefined) gameHint.innerText=`Bulls:${d.bulls} Cows:${d.cows}`;
    if(d.hint) gameHint.innerText=d.hint;
    if(d.result) alert(d.result);

    loadLeaderboard();
}

// ===== LEADERBOARD =====
async function loadLeaderboard() {
    const r = await fetch(BACKEND_URL+"/leaderboard");
    const d = await r.json();
    leaderboard.innerHTML="";
    d.forEach(u=>{
        leaderboard.innerHTML+=`<li>#${u.rank} ${u.username} (${u.score})</li>`;
    });
}

// ===== CHAT (HTTP POLLING) =====
async function sendChat() {
    const msg = chatInput.value.trim();
    if (!msg) return;

    await fetch(BACKEND_URL+"/chat/send",{
        method:"POST",
        headers:{
            Authorization:`Bearer ${token}`,
            "Content-Type":"application/json"
        },
        body:JSON.stringify({message:msg})
    });
    chatInput.value="";
}

async function loadChat() {
    const r = await fetch(BACKEND_URL+"/chat/messages");
    const d = await r.json();
    chatBox.innerHTML="";
    d.forEach(c=>{
        chatBox.innerHTML+=`<b>${c.username}:</b> ${c.message}<br>`;
    });
    chatBox.scrollTop = chatBox.scrollHeight;
}