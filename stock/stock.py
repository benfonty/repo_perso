import pymongo
from flask import Flask
from flask.ext.restful import request, abort, Api, Resource, reqparse
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

parserPut = reqparse.RequestParser()
parserPut.add_argument('etat', type=str, required = True, help='Etat obligatoire', location = 'args')

parserPost = reqparse.RequestParser()
parserPost.add_argument('imei', type=str, required = True, help='imei obligatoire')
parserPost.add_argument('gencod', type=str, required = True, help='gencod obligatoire')
parserPost.add_argument('etat', type=str, required = True, help='etat obligatoire')

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
            args = parserPut.parse_args()
            if not controleEtat(args["etat"]):
                return abort(400,message = "etat non valide " + args["etat"])
            if not controleCoherence("typ",old["etat"],args["etat"]):
                return abort(400,message = "erreur coherence " + old["etat"] + "=>" + args["etat"])
                allset["etat"] = etat
            allset["datmaj"] = datetime.datetime.now()
            modif = {"$set":allset}
            debug(str(modif))
            print (collection.update({"_id":imei,"psav":psav},modif))
            if request.args.get("maintenance") == None and old["etat"] != args["etat"]:
                changement(psav,"type",old["etat"],args["etat"])
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
        args = parserPost.parse_args()
        if not controleEtat(args["etat"]):
            return abort(400,message = "Mauvaise valeur " + args["etat"]  + " pour etat")
        if not controleImei(args["imei"]):
            return abort(400,message = "Mauvaise valeur " + args["imei"]  + " pour imei")
        gencod = controleGencod(args["gencod"])
        if gencod == None:
            return abort(400,message = "Mauvaise valeur " + args["gencod"]  + " pour gencod")
        with LOCK:
            old = collection.find_one({"_id":args["imei"]})
            if old != None: 
                if old["psav"] != psav and old["etat"] not in ETATS_PURGEABLE:
                    abort(400,message="imei existe déjà dans un autre psav")
                if not controleCoherence("typ",old["etat"],args["etat"]):
                    return abort(400,message = "erreur coherence " + old["etat"] + "=>" + args["etat"])
            args["_id"] = args["imei"]
            del args["imei"]
            args["datmaj"] = datetime.datetime.now()
            args["psav"] = psav
            args["type"] = gencod["type"]["code"]
            if args["type"] in ("SIM","SIM_F"):
                args["reappro"] = gencod["famille"]["libelle"]
            else:
                args["reappro"] = gencod["classe"]["libelle"]
            print (args)
            collection.save(args)
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