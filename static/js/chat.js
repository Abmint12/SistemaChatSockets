// Cliente del chat en tiempo real.
const token = localStorage.getItem("token");
const username = localStorage.getItem("username");

// Sin sesión no hay chat: volvemos al login.
if (!token) {
  window.location.href = "/";
}

// --- Referencias del DOM ---
const messagesEl = document.getElementById("messages");
const usersListEl = document.getElementById("users-list");
const usersCountEl = document.getElementById("users-count");
const connStateEl = document.getElementById("conn-state");
const typingEl = document.getElementById("typing-indicator");
const composer = document.getElementById("composer");
const input = document.getElementById("msg-input");
const meName = document.getElementById("me-name");
const meAvatar = document.getElementById("me-avatar");

meName.textContent = username;
meAvatar.textContent = (username || "?").charAt(0).toUpperCase();

// --- Utilidades ---
// Escapa HTML para evitar inyección de código (XSS) en los mensajes.
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString("es-EC", { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function atBottom() {
  return messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 80;
}
function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage({ username: user, content, timestamp }) {
  const stick = atBottom();
  const wrap = document.createElement("div");
  wrap.className = "msg" + (user === username ? " mine" : "");
  wrap.innerHTML =
    `<span class="meta">${escapeHtml(user)} · ${formatTime(timestamp)}</span>` +
    `<div class="bubble">${escapeHtml(content)}</div>`;
  messagesEl.appendChild(wrap);
  if (stick) scrollToBottom();
}

function addSystem(content) {
  const wrap = document.createElement("div");
  wrap.className = "msg system";
  wrap.innerHTML = `<div class="bubble">${escapeHtml(content)}</div>`;
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

function renderUsers(users) {
  usersCountEl.textContent = users.length;
  usersListEl.innerHTML = "";
  users.forEach((u) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="dot"></span> ${escapeHtml(u)}` + (u === username ? " (tú)" : "");
    usersListEl.appendChild(li);
  });
}

// --- Conexión WebSocket ---
let socket;
let typingTimeout;

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${proto}://${location.host}/ws?token=${encodeURIComponent(token)}`);

  socket.onopen = () => {
    connStateEl.textContent = "En línea";
    connStateEl.className = "conn-state online";
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
      case "history":
        data.messages.forEach(addMessage);
        scrollToBottom();
        break;
      case "message":
        addMessage(data);
        break;
      case "system":
        addSystem(data.content);
        break;
      case "users":
        renderUsers(data.users);
        break;
      case "typing":
        if (data.username !== username) showTyping(data.username);
        break;
    }
  };

  socket.onclose = (event) => {
    connStateEl.textContent = "Desconectado";
    connStateEl.className = "conn-state offline";
    // Código 1008 = token inválido/expirado -> cerramos sesión.
    if (event.code === 1008) {
      localStorage.clear();
      window.location.href = "/";
      return;
    }
    // Reintento automático de reconexión.
    setTimeout(connect, 2000);
  };
}

function showTyping(user) {
  typingEl.textContent = `${user} está escribiendo…`;
  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => (typingEl.textContent = ""), 1500);
}

// --- Envío de mensajes ---
composer.addEventListener("submit", (e) => {
  e.preventDefault();
  const content = input.value.trim();
  if (!content || !socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type: "message", content }));
  input.value = "";
});

// Aviso "está escribiendo…" (limitado para no saturar).
let lastTyping = 0;
input.addEventListener("input", () => {
  const now = Date.now();
  if (socket && socket.readyState === WebSocket.OPEN && now - lastTyping > 1200) {
    socket.send(JSON.stringify({ type: "typing" }));
    lastTyping = now;
  }
});

// --- Cerrar sesión ---
document.getElementById("btn-logout").addEventListener("click", () => {
  if (socket) socket.close();
  localStorage.clear();
  window.location.href = "/";
});

connect();
