import pymongo
from flask import Flask
from flask.ext.restful import request, abort, Api, Resource
import datetime
import threading

LOCK = threading.Lock() 

DEBUG = True

def debug(str):
    if DEBUG:
        print("DEBUG",datetime.datetime.utcnow(),str)

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock
collection = database.stock

references = database.references.find_one()

ETATS_PURGEABLE = ['C','T']

def controleEtat(etat):
    return etat in references["etats"]
 
def luhnCheck(card_number):
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit
    return ( (sum % 10) == 0 )
       
def controleImei( l ):
    #TODO
    return True

def controleGencod( gencod ):
    return database.gencods.find_one({"_id":gencod})


def changement(psav,typ,etat1,etat2):
    print("changement",psav,typ,etat1,etat2)
        
def controleCoherence(typ,etat1,etat2):
    return True

def purge(psav):
    collection.remove({"psav":psav,"etat":{"$in":ETATS_PURGEABLE}})

CHAMPS = {
    "imei" :{
        "obligatoire" : True,
        "controle": controleImei
    },
    "gencod" :{
        "obligatoire" : True
    },
    "etat" :{
        "obligatoire" : True,
        "controle": controleEtat
    }
}

class Imei(Resource):
    def get(self,psav, imei):
        imei = collection.find_one({"_id":imei,"psav":psav},{"psav":0, "reappro":0})
        if imei == None:
            abort(404,message = "imei inconnu " + imei)
        imei["datmaj"] = str(imei["datmaj"])
        imei["imei"] = imei["_id"]
        del imei["_id"]
        return imei, 200

    def put(self,psav,imei):
        with LOCK:
            old = collection.find_one({"_id":imei,"psav":psav})
            if old == None:
               abort(404,message = "imei inconnu " + imei)
            etat = request.args.get("etat")
            allset = {}
            if etat != None:
                if not controleEtat(etat):
                    return abort(400,message = "etat non valide " + etat)
                if not controleCoherence("typ",old["etat"],etat):
                   return abort(400,message = "erreur coherence " + old["etat"] + "=>" + etat)
                allset["etat"] = etat
            allset["datmaj"] = datetime.datetime.now()
            modif = {"$set":allset}
            debug(str(modif))
            print (collection.update({"_id":imei,"psav":psav},modif))
            if request.args.get("maintenance") == None and old["etat"] != etat:
                changement(psav,"type",old["etat"],etat)
            return "", 204

class ImeiList(Resource):
    def get(self,psav):
        gencod = request.args.get("gencod")
        etat = request.args.get("etat")
        tout = request.args.get("all")
        searchTerm = {"psav":psav}
        if gencod != None:
            searchTerm["gencod"] = gencod
        if etat != None:
            searchTerm["etat"] = etat
        elif tout == None:
            searchTerm["etat"] = {"$nin":ETATS_PURGEABLE}
        debug(searchTerm)
        reponse = []
        for item in collection.find(searchTerm,{"psav":0, "reappro":0}):
            item["datmaj"] = str(item["datmaj"])
            item["imei"] = item["_id"]
            del item["_id"]
            reponse.append(item)
        debug(str(len(reponse)) + " trouvés")
        return {"list":reponse}, 200

class ImeiCreation(Resource):
    def post(self,psav):
        if not request.json:
            abort(400,message = "Pas du Json")
        jsonObj = request.json
        for key,value in jsonObj.items():
            champ = CHAMPS.get(key)
            if champ == None:
                return abort(400,message = "champ inconnu " + key)
            if "controle" in champ and not champ["controle"](value):
                return abort(400,message = "Mauvaise valeur " + value  + " pour " + key)
        for champ, valeur in CHAMPS.items():
            if valeur["obligatoire"] and champ not in jsonObj:
                return abort(400, message = "il manque " + champ)
        gencod = controleGencod(jsonObj["gencod"])
        if gencod == None:
            return abort(400,message = "Mauvaise valeur " + jsonObj["gencod"]  + " pour gencod")
        with LOCK:
            old = collection.find_one({"_id":jsonObj["imei"]})
            if old != None: 
                if old["psav"] != psav and old["etat"] not in ETATS_PURGEABLE:
                    abort(400,message="imei existe déjà dans un autre psav")
                if not controleCoherence("typ",old["etat"],jsonObj["etat"]):
                    return abort(400,message = "erreur coherence " + old["etat"] + "=>" + jsonObj["etat"])
            jsonObj["_id"] = jsonObj["imei"]
            del jsonObj["imei"]
            jsonObj["datmaj"] = datetime.datetime.now()
            jsonObj["psav"] = psav
            jsonObj["type"] = gencod["type"]["code"]
            if jsonObj["type"] in ("SIM","SIM_F"):
                jsonObj["reappro"] = gencod["famille"]["libelle"]
            else:
                jsonObj["reappro"] = gencod["classe"]["libelle"]
            collection.save(jsonObj)
            return "", 201

class Transfert(Resource):
    def post(self,psav,psavcible):
        typeTransfert = request.args.get("type")
        if typeTransfert not in ("total","partiel"):
            abort(400,message = "Mauvais type de transfert")
        if collection.find_one({"psav":psav}) == None:
            abort(400,message = "Pas de stock pour le pSAV source")
        if typeTransfert == "partiel":
            collection.update({"psav":psav,"etat":{"$in":['D','R']},"type":{"$ne":"SIM"}},{"$set":{"etat":"X"}},multi = True)
        reponse = collection.update({"psav":psav,"etat":{"$in":['D','K','R']}},{"$set":{"psav":psavcible}},multi = True)
        purge(psav)
        return {"transfert":reponse["nModified"]},200

BASE_URL = '/stock/<psav>'
app = Flask(__name__)
api = Api(app)
api.add_resource(Imei,BASE_URL + '/imei/<imei>')
api.add_resource(ImeiCreation,BASE_URL + '/imei')
api.add_resource(ImeiList,BASE_URL)
api.add_resource(Transfert,BASE_URL + '/transfert/<psavcible>')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)