import pymongo
import flask
import cgi
import re
import json
import datetime
#import stdnum
import threading


LOCK = threading.Lock()

app = flask.Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({"error":str(error)}), 404)

@app.errorhandler(400)
def not_found(error):
    return flask.make_response(flask.jsonify({"error":str(error)}), 400)

BASE_URL = '/stock/<psav>'

DEBUG = True

def debug(str):
    if DEBUG:
        print("DEBUG",datetime.datetime.utcnow(),str)

PURGEABLE = ['C','T']

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock
collection = database.stock

references = database.references.find_one()

def controleEtat(etat):
    return etat in references["etats"]
        
def controleImei( l ):
    #TODO
    return True

def controleGencod( gencod ):
    #TODO
    return True


def changement(psav,typ,etat1,etat2):
    print(psav,typ,etat1,etat2)

def controleCoherence(typ,etat1,etat2):
    return True

CHAMPS = {
    "imei" :{
        "obligatoire" : True,
        "controle": controleImei
    },
    "gencod" :{
        "obligatoire" : True,
        "controle": controleGencod
    },
    "etat" :{
        "obligatoire" : True,
        "controle": controleEtat
    }
}

assert controleEtat('D')
assert not controleEtat('PP')
assert controleImei('329463363608757')
#assert not controleImei('329463363608758')


@app.route(BASE_URL, methods=['GET'])
def getStock(psav):
    gencod = flask.request.args.get("gencod")
    etat = flask.request.args.get("etat")
    tout = flask.request.args.get("all")
    searchTerm = {"psav":psav}
    if gencod != None:
        searchTerm["gencod"] = gencod
    if etat != None:
        searchTerm["etat"] = etat
    elif tout == None:
        searchTerm["etat"] = {"$nin":PURGEABLE}
    debug(searchTerm)
    reponse = []
    for item in collection.find(searchTerm,{"psav":0}):
        item["datmaj"] = str(item["datmaj"])
        item["imei"] = item["_id"]
        del item["_id"]
        reponse.append(item)
    debug(str(len(reponse)) + " trouvés")
    return flask.jsonify({"list":reponse}), 200

@app.route(BASE_URL+ '/imei/<imei>', methods=['GET'])
def getStockByImei(psav,imei):
    imei = collection.find_one({"_id":imei,"psav":psav})
    if imei == None:
        flask.abort(404,{"erreur":"imei inconnu"})
    imei["datmaj"] = str(imei["datmaj"])
    imei["imei"] = imei["_id"]
    del imei["_id"]
    return flask.jsonify(imei), 200

@app.route(BASE_URL+ '/imei/<imei>', methods=['PUT'])
def updateState(psav,imei):
    with LOCK:
       old = collection.find_one({"_id":imei,"psav":psav})
       if old == None:
           flask.abort(404,{"erreur":"imei inconnu"})
    
       etat = flask.request.args.get("etat")
       allset = {}
       allunset = {}
       if etat != None:
           if not controleEtat(etat):
               return flask.abort(400,{"erreur":"etat non valide " + "etat"})
           if not controleCoherence("typ",old["etat"],etat):
               return flask.abort(400,{"erreur":"erreur coherence " + old["etat"] + "=>" + etat})
           allset["etat"] = etat
       allset["datmaj"] = datetime.datetime.now()
       modif = {"$set":allset}
       if allunset != {}:
           modif["$unset"] = allunset
       debug(str(modif))
       print (collection.update({"_id":imei,"psav":psav},modif))
       changement(psav,"type",old["etat"],etat)
       return "", 204

@app.route(BASE_URL + '/imei', methods=['POST'])
def create(psav):
    if not flask.request.json:
        abort(400)
    jsonObj = flask.request.json
    for key,value in jsonObj.items():
        champ = CHAMPS.get(key)
        if champ == None:
            return flask.abort(400,{"erreur":"champ inconnu " + key})
        if "controle" in champ and not champ["controle"](value):
            return flask.abort(400,{"erreur":"Mauvaise valeur " + value  + " pour " + key})
    for champ, valeur in CHAMPS.items():
        if valeur["obligatoire"] and champ not in jsonObj:
            return flask.abort(400, {"erreur":"il manque " + champ})
    with LOCK:
        old = collection.find_one({"_id":jsonObj["imei"]})
        if old != None: 
            if old["psav"] != psav and old["etat"] not in PURGEABLE:
                flask.abort(400,{"erreur":"imei existe déjà dans un autre psav"})
            if not controleCoherence("typ",old["etat"],jsonObj["etat"]):
                return flask.abort(400,{"erreur":"erreur coherence " + old["etat"] + "=>" + jsonObj["etat"]})
        jsonObj["_id"] = jsonObj["imei"]
        del jsonObj["imei"]
        jsonObj["datmaj"] = datetime.datetime.now()
        jsonObj["psav"] = psav
        collection.save(jsonObj)
        return "", 201

@app.route(BASE_URL + '/transfert/<psavcible>', methods=['POST'])
def transfert(psav,psavcible):

    #nouvelle imei à insérer
    return "TODO", 204

if __name__ == '__main__':
    app.run(debug=True, threaded=True)