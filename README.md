# SistemaChatSockets
Proyecto Segundo Parcial Aplicaciones Distribuidas
## Integrantes

- **Michael Goya Medina**
- **Joselyne Sarmiento Amaya**
- **Zambrano Valverde Luis**

# ChatRT — Sistema de Chat en Tiempo Real

Sistema de chat en tiempo real con **sockets (WebSockets)** que permite a múltiples
usuarios conectarse a un servidor centralizado y comunicarse de forma instantánea y
segura. Proyecto del **segundo parcial** de la asignatura *Aplicaciones Distribuidas*.

**Stack:** FastAPI · Uvicorn · WebSockets · SQLAlchemy · SQLite/PostgreSQL · JWT · bcrypt · HTML/CSS/JS

---

## ✨ Características

- Comunicación en **tiempo real** mediante WebSockets (bidireccional, baja latencia).
- **Servidor centralizado** que maneja múltiples conexiones simultáneas.
- **Registro e inicio de sesión** con contraseñas hasheadas (bcrypt) y tokens **JWT**.
- **Reenvío (broadcast)** de mensajes a todos los usuarios conectados.
- **Lista de usuarios en línea** que se actualiza automáticamente.
- **Historial** de los últimos mensajes al conectarse.
- Indicador de *"escribiendo…"* y **reconexión automática**.
- **Diseño responsivo**: funciona en computadora y móvil.
- Medidas de seguridad: validación con Pydantic, escape de XSS y control anti-spam.

---

## 📂 Estructura del proyecto

```
chat-tiempo-real/
├── app/                    # Backend (servidor)
│   ├── main.py             # App FastAPI: rutas REST y endpoint /ws
│   ├── database.py         # Conexión SQLAlchemy (SQLite/PostgreSQL)
│   ├── models.py           # Modelos: User y Message
│   ├── schemas.py          # Esquemas Pydantic (validación)
│   ├── auth.py             # bcrypt + JWT
│   └── manager.py          # ConnectionManager (broadcast WebSocket)
├── static/                 # Frontend (cliente)
│   ├── index.html          # Login / registro
│   ├── chat.html           # Sala de chat
│   ├── css/styles.css
│   └── js/{auth.js, chat.js}
├── docs/                   # Manuales y presentación
├── requirements.txt
├── render.yaml             # Despliegue en Render (Blueprint)
├── Procfile
├── runtime.txt
└── .env.example
```

---

## 🚀 Ejecución local

Requisitos: **Python 3.12+**.

```bash
git clone <URL-DEL-REPOSITORIO> chat-tiempo-real
cd chat-tiempo-real

# Entorno virtual
python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre **http://127.0.0.1:8000** en tu navegador. La documentación de la API queda en `/docs`.

> Opcional: copia `.env.example` como `.env` para personalizar `SECRET_KEY`, la
> expiración del token o la base de datos.

---

## ☁️ Despliegue en Render

Este repositorio incluye `render.yaml` (Blueprint). En Render:

1. Sube el proyecto a GitHub.
2. **New → Blueprint** y selecciona el repositorio. Render leerá `render.yaml` y creará
   el servicio web + la base de datos PostgreSQL automáticamente.
3. `SECRET_KEY` se genera de forma segura y `DATABASE_URL` se enlaza sola.
4. Al terminar el build, el sistema queda en una URL pública con **HTTPS/WSS**.

Comando de arranque en producción:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

> Si eliminas el bloque `databases` y la variable `DATABASE_URL` de `render.yaml`,
> la aplicación usa SQLite automáticamente.
https://chat-tiempo-real-dt0y.onrender.com/
---

## 🔌 API y protocolo

### REST

| Método y ruta        | Descripción                          |
|----------------------|--------------------------------------|
| `POST /api/register` | Crea un usuario y devuelve un JWT.    |
| `POST /api/login`    | Inicia sesión y devuelve un JWT.      |
| `GET /health`        | Estado del servicio.                  |
| `WS /ws?token=<JWT>` | Canal del chat en tiempo real.        |

### Mensajes WebSocket (JSON)

| `type`   | Dirección           | Propósito                                |
|----------|---------------------|------------------------------------------|
| message  | Cliente ⇄ Servidor  | Mensaje de chat (usuario, texto, hora).  |
| history  | Servidor → Cliente  | Últimos mensajes al conectarse.          |
| users    | Servidor → Cliente  | Lista de usuarios conectados.            |
| system   | Servidor → Cliente  | Avisos de entrada/salida.                |
| typing   | Cliente ⇄ Servidor  | Indicador de "escribiendo…".             |

---

## 📖 Documentación

En la carpeta [`docs/`](docs/) se incluyen:

- **Manual_Tecnico.docx** — arquitectura, instalación, servidor, cliente y despliegue.
- **Manual_Usuario.docx** — guía para el usuario final.
- **Presentacion_Sustentacion.pptx** — diapositivas de la sustentación.

---

## 🧪 Pruebas

El proyecto incluye pruebas de extremo a extremo (`test_e2e.py`) que verifican registro,
login, rechazo de credenciales/tokens inválidos y el broadcast de mensajes entre clientes.

---

*Universidad de Guayaquil · Ingeniería de Software · Aplicaciones Distribuidas*
