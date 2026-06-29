from flask import Flask
from flask_socketio import SocketIO

app= Flask(__name__)
app.config["SECRET_KEY"]= "chat-secret"

socketio=SocketIO(app)

@app.route("/")
def inicio():
    return "Servidor del chat funcionando"

if __name__=="__main__":
    socketio.run(app, debug=True)