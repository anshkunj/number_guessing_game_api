const BACKEND_URL = "https://multiplayer-game-1x2u.onrender.com";

let token = null;
let ws = null;
let currentGame = null;

// ===== LOGIN / REGISTER =====
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    if (!username || !password) { alert("Username & password required"); return; }

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch(`${BACKEND_URL}/login`, { method:"POST", headers:{"Content-Type":"application/x-www-form-urlencoded"}, body:formData });
    const data = await res.json();

    if (!data.access_token) { alert("Login failed"); return; }

    token = data.access_token;
    document.getElementById("login").style.display="none";
    document.getElementById("register").style.display="none";
    document.getElementById("dashboard").style.display="block";

    connectChat();
    loadLeaderboard();
}

function showRegister() { document.getElementById("login").style.display="none"; document.getElementById("register").style.display="block"; }
function showLogin() { document.getElementById("register").style.display="none"; document.getElementById("login").style.display="block"; }

async function registerUser() {
    const username = document.getElementById("regUsername").value.trim();
    const password = document.getElementById("regPassword").value.trim();
    if(!username || !password){ alert("Fill all fields"); return; }

    const res = await fetch(`${BACKEND_URL}/register`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({username,password}) });
    const data = await res.json();
    alert(data.message || "Registered");
    showLogin();
}

// ===== LOGOUT =====
function logout() {
    token=null;
    if(ws) ws.close();
    document.getElementById("dashboard").style.display="none";
    document.getElementById("login").style.display="block";
    alert("Logged out");
}

// ===== START GAMES =====
async function startNumberGuess() { await startGame("/guess/start","guess"); }
async function startBullsCows() { await startGame("/bulls-cows/start","bulls_cows"); }

async function startGame(endpoint,gameType){
    const res = await fetch(BACKEND_URL+endpoint,{ method:"POST", headers:{"Authorization":`Bearer ${token}`} });
    const data = await res.json();
    document.getElementById("lives").innerText=`Lives: ${data.lives}`;
    document.getElementById("attempts").innerText=`Attempts: ${data.attempts}`;
    document.getElementById("gameHint").innerText="Game Started! Make your guess.";
    currentGame = gameType;
}

// ===== MAKE GUESS =====
async function makeGuess() {
    if(!currentGame){ alert("Start a game"); return; }
    const guess=document.getElementById("guessInput").value.trim();
    if(!guess) return;

    const endpoint=currentGame==="guess"?"/guess/play":"/bulls-cows/play";
    const body=currentGame==="guess"?{guess:parseInt(guess)}:{guess};

    const res=await fetch(BACKEND_URL+endpoint,{ method:"POST", headers:{"Authorization":`Bearer ${token}`,"Content-Type":"application/json"}, body:JSON.stringify(body)});
    const data=await res.json();

    if(data.lives!==undefined) document.getElementById("lives").innerText=`Lives: ${data.lives}`;
    if(data.attempts!==undefined) document.getElementById("attempts").innerText=`Attempts: ${data.attempts}`;
    if(data.hint) document.getElementById("gameHint").innerText=data.hint;
    if(data.bulls!==undefined) document.getElementById("gameHint").innerText=`Bulls: ${data.bulls}, Cows: ${data.cows}`;
    if(data.result) alert(data.result);

    loadLeaderboard();
}

// ===== LEADERBOARD =====
async function loadLeaderboard() {
    const res = await fetch(BACKEND_URL+"/leaderboard");
    const data = await res.json();
    const lb=document.getElementById("leaderboard");
    lb.innerHTML="";
    data.forEach(u=>{
        const li=document.createElement("li");
        li.innerText=`#${u.rank} ${u.username} - Score:${u.score} Wins:${u.wins}`;
        lb.appendChild(li);
    });
}

// ===== CHAT =====
function connectChat(){
    ws = new WebSocket(`${BACKEND_URL.replace(/^http/,"ws")}/ws/chat?token=${token}`);
    ws.onmessage=(e)=>{ const box=document.getElementById("chatBox"); box.innerHTML+=e.data+"<br>"; box.scrollTop=box.scrollHeight; }
    ws.onopen=()=>console.log("Chat connected");
    ws.onclose=()=>console.log("Chat disconnected");
}

function sendChat() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();

    if (!msg) return;

    ws.send(msg);

    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<b>You:</b> ${msg}<br>`;

    input.value = "";
}