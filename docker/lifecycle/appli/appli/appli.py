# coding: utf8

from flask import Flask
import os

reponse = """
    <html>
        <head>
            <title>Appli</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>"""


def log(something):
    try:
        with open(os.environ.get('HOSTNAME')+ "logs_" + hostname + ".log") as logfile:
            logfile.write(something + "\n")
    except:
        pass

app = Flask(__name__)

@app.route("/")
def hello():
    log("J'ai été appelé")
    return reponse, 200

if __name__ == "__main__":
    print "Demarrage"

    app.run()