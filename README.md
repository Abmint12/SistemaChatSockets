# SistemaChatSockets

## Proyecto Segundo Parcial - Aplicaciones Distribuidas

Sistema de Chat en Tiempo Real desarrollado con **Python, Flask y Flask-SocketIO**.

## Integrantes

* Michael Goya Medina
* Joselyne Sarmiento Amaya
* Zambrano Valverde Luis

---

## Tecnologías utilizadas

* Python 3.10+
* Flask
* Flask-SocketIO
* Eventlet
* HTML5
* CSS3
* JavaScript
* Git y GitHub

---

## Funcionalidades implementadas

* Pantalla de inicio de sesión.
* Comunicación cliente-servidor mediante Socket.IO.
* Servidor Flask.
* Interfaz web para el chat.
* Preparado para mensajería en tiempo real.

### Funcionalidades en desarrollo

* Envío y recepción de mensajes en tiempo real.
* Lista de usuarios conectados.
* Notificaciones de conexión y desconexión.
* Mejoras en la interfaz del chat.

---

## Estructura del proyecto

```
SistemaChatSockets/
│
├── backend/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── docs/
├── screenshots/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/Abmint12/SistemaChatSockets.git
```

Ingresar al proyecto:

```bash
cd SistemaChatSockets
```

Crear el entorno virtual:

```bash

py -m venv venv
```

Activar el entorno virtual (Windows):

```bash
.\venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecución del proyecto

Ingresar a la carpeta del backend:

```bash
cd backend
```

Ejecutar el servidor:

```bash
py app.py
```

Si el comando `python` no funciona:

```bash
py app.py
```

Abrir el navegador en:

```
http://127.0.0.1:5000
```

---
