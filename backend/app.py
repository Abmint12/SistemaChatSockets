import os
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

#  Rutas base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates")
)

app.config["SECRET_KEY"] = "chat-secret"

socketio = SocketIO(app)

usuarios = []

# Login
@app.route("/")
def login():
    return render_template("login.html")


#  Chat (recibe usuario)
@app.route("/chat", methods=["POST", "GET"])
def chat():
    if request.method == "POST":
        usuario = request.form["usuario"]
        return render_template("chat.html", usuario=usuario)

    return redirect(url_for("login"))


#  SocketIO connect
@socketio.on("connect")
def conectar():
    print("Un usuario se conectó")


#  Ejecutar servidor
if __name__ == "__main__":
    socketio.run(app, debug=True)