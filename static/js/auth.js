// Lógica de la pantalla de login / registro.
const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const formLogin = document.getElementById("form-login");
const formRegister = document.getElementById("form-register");
const msg = document.getElementById("auth-msg");

// Si ya hay sesión iniciada, vamos directo al chat.
if (localStorage.getItem("token")) {
  window.location.href = "/chat";
}

function showTab(which) {
  const isLogin = which === "login";
  tabLogin.classList.toggle("active", isLogin);
  tabRegister.classList.toggle("active", !isLogin);
  formLogin.classList.toggle("hidden", !isLogin);
  formRegister.classList.toggle("hidden", isLogin);
  msg.textContent = "";
}

tabLogin.addEventListener("click", () => showTab("login"));
tabRegister.addEventListener("click", () => showTab("register"));

function setMsg(text, ok = false) {
  msg.textContent = text;
  msg.className = "auth-msg " + (ok ? "ok" : "error");
}

async function submitAuth(url, payload) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      setMsg(data.detail || "Ocurrió un error.");
      return;
    }
    // Guardamos el token y el nombre, y entramos al chat.
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("username", data.username);
    window.location.href = "/chat";
  } catch (err) {
    setMsg("No se pudo conectar con el servidor.");
  }
}

formLogin.addEventListener("submit", (e) => {
  e.preventDefault();
  const f = new FormData(formLogin);
  submitAuth("/api/login", {
    username: f.get("username").trim(),
    password: f.get("password"),
  });
});

formRegister.addEventListener("submit", (e) => {
  e.preventDefault();
  const f = new FormData(formRegister);
  submitAuth("/api/register", {
    username: f.get("username").trim(),
    email: f.get("email").trim(),
    password: f.get("password"),
  });
});
