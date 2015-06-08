# coding: utf8

from flask import Flask
import socket
import json

try:
    with open('/DATA/config.json','r') as f:
        param = json.load(f)
except Exception as e:
    print("Erreur de lecture du fichier de paramétrage",e)
    sys.exit(1)

reponse = """
    <html>
        <head>
            <title>Appli</title>
        </head>
        <body>
            <h1>TEXTE</h1>
        </body>
    </html>"""

def gethostname():
    if socket.gethostname().find('.')>=0:
        return socket.gethostname()
    else:
        return socket.gethostbyaddr(socket.gethostname())[0]

def log(something):
    with open("/LOGS/" + "logs_" + gethostname() + ".log","a+") as logfile:
        logfile.write(something + "\n")
    
app = Flask(__name__)

@app.route("/")
def hello():
    log("j'ai reçu un message")
    return reponse.replace("TEXTE",param["texte"]), 200

if __name__ == "__main__":
    print "Demarrage"

    app.run(host='0.0.0.0')