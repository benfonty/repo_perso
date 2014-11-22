import pymongo
import bottle
import cgi
import re
import json
import datetime
#import stdnum

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
        
def controleBi(bi):
    return len(bi) == 8

def controleImei( l ):
    #TODO
    return True

def controleGencod( gencod ):
    #TODO
    return True

def controleFamille(famille):
    return famille in references["familles"]

def controleType(type):
    return type in references["types"]

def controleClasse(classe):
    return classe in references["classes"]

def changement(psav,typ,etat1,etat2):
    print(psav,typ,etat1,etat2)

def controleCoherence(typ,etat1,etat2):
    return True

CHAMPS = {
    "imei" :{
        "obligatoire" : True,
        "controle": controleImei
    },
    "bi" :{
        "obligatoire" : False,
        "controle" : controleBi
    },
    "gencod" :{
        "obligatoire" : True,
        "controle": controleGencod
    },
    "motif" :{
        "obligatoire" : False,
    },
    "etat" :{
        "obligatoire" : True,
        "controle": controleEtat
    },
    "type" :{
        "obligatoire" : True,
        "controle": controleType
    },
    "classe" :{
        "obligatoire" : True,
        "controle": controleClasse
    },
    "famille" :{
        "obligatoire" : True,
        "controle": controleFamille
    }
}

assert controleEtat('D')
assert not controleEtat('PP')
assert controleImei('329463363608757')
#assert not controleImei('329463363608758')

@bottle.get(BASE_URL)
def getStock(psav):
    gencod = bottle.request.query.get("gencod")
    etat = bottle.request.query.get("etat")
    thetype = bottle.request.query.get("type")
    bi = bottle.request.query.get("bi")
    tout = bottle.request.query.get("all")
    searchTerm = {"psav":psav}
    if gencod != None:
        searchTerm["gencod"] = gencod
    if etat != None:
        searchTerm["etat"] = etat
    elif tout == None:
        searchTerm["etat"] = {"$nin":PURGEABLE}

    if bi != None:
        searchTerm["bi"] = bi
    if thetype != None:
        searchTerm["type"] = thetype
    debug(searchTerm)
    reponse = []
    for item in collection.find(searchTerm):
        item["datmaj"] = str(item["datmaj"])
        reponse.append(item)
    debug(str(len(reponse)) + " trouvés")
    return json.dumps(reponse)


@bottle.get(BASE_URL+ '/imei/<imei>')
def getStockByImei(psav,imei):
    imei = collection.find_one({"_id":imei,"psav":psav})
    if imei == None:
        bottle.abort(404,"imei inconnu")
    imei["datmaj"] = str(imei["datmaj"])
    return json.dumps(imei)

def addToUnset(modif,field):
    if "$unset" not in modif:
        modif["$unset"] = {}
    modif["$unset"][field] = 1

@bottle.put(BASE_URL + '/imei/<imei>')
def updateState(psav,imei):
    old = collection.find_one({"_id":imei,"psav":psav})
    if old == None:
        bottle.abort(404,"imei inconnu")

    etat = bottle.request.query.get("etat")
    motif = bottle.request.query.get("motif")
    bi = bottle.request.query.get("bi")
    allset = {}
    allunset = {}
    if etat != None:
        if not controleEtat(etat):
            return bottle.abort(400,"etat non valide " + "etat")
        if not controleCoherence("typ",old["etat"],etat):
            return bottle.abort(400,"erreur coherence " + old["etat"] + "=>" + etat)
        allset["etat"] = etat
    if bi != None:
        if bi != "null":
            if not controleBi(bi):
                return bottle.abort(400,"bi non valide " + bi)
            allset["bi"] = bi
        else:
            allunset["bi"] = 1

    if motif != None:
        if allset != "null":
            modif["motif"] = motif
        else:
            allunset["motif"] = 1
    allset["datmaj"] = datetime.datetime.now()
    modif = {"$set":allset}
    if allunset != {}:
        modif["$unset"] = allunset
    debug(str(modif))
    print (collection.update({"_id":imei,"psav":psav},modif))
    changement(psav,"type",old["etat"],etat)
    return "OK"




@bottle.post(BASE_URL + '/imei')
def create(psav):
    try:
        jsonObj = bottle.request.json
    except ValueError:
        return bottle.abort(400,"format incorrect")
    for key,value in jsonObj.items():
        champ = CHAMPS.get(key)
        if champ == None:
            return bottle.abort(400,"champ inconnu " + key)
        if "controle" in champ and not champ["controle"](value):
            return bottle.abort(400,"Mauvaise valeur " + value  + " pour " + key)
    for champ, valeur in CHAMPS.items():
        if valeur["obligatoire"] and champ not in jsonObj:
            return bottle.abort(400, "il manque " + champ)
    old = collection.find_one({"_id":jsonObj["imei"]})
    if old != None: 
        if old["psav"] != psav and old["etat"] not in PURGEABLE:
            bottle.abort(400,"imei existe déjà dans un autre psav")
        if not controleCoherence("typ",old["etat"],jsonObj["etat"]):
            return bottle.abort(400,"erreur coherence " + old["etat"] + "=>" + jsonObj["etat"])
    jsonObj["_id"] = jsonObj["imei"]
    del jsonObj["imei"]
    jsonObj["datmaj"] = datetime.datetime.now()
    jsonObj["psav"] = psav
    collection.save(jsonObj)



@bottle.post(BASE_URL + '/transfert/<psavcible>')
def transfert(psav,psavcible):

    #nouvelle imei à insérer
    return "TODO"

bottle.debug(True)
bottle.run(host='localhost', port=8082)