from flask import Flask, render_template, request,redirect
from flask_socketio import SocketIO

app= Flask(__name__)
app.config["SECRET_KEY"]= "chat-secret"

socketio=SocketIO(app)

usuarios= []


@app.route("/")
def login():    
    return render_tmeplate("login.html")

@app.route("/chat",methods=["POST"])
def chat():
    
    usuario=request.form["usuario"]

    return render_template(
        "chat.html",
        usuario=usuario
    )

@app.route("/")
def inicio():
    return "Servidor del chat funcionando"

if __name__=="__main__":
    socketio.run(app, debug=True)