import pymongo
from collections import OrderedDict
from flask import Flask
from flask.ext.restful import request, abort, Api, Resource, reqparse
import datetime
import threading
import random
import copy

LOCK = threading.Lock() 

DEBUG = True

def debug(*affichage):
    if DEBUG:
        print("DEBUG",datetime.datetime.utcnow()," : "," ".join([ str(x) for x in list(affichage)]))

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


def changement(psav,type,classe,etat1,etat2):
    debug("changement",psav,type,classe,etat1,etat2)
    comptabilise = False
    comptabilise = comptabilise or (type in ("SIM","SIM_F") and etat1 == "D" and etat2 == "C")
    comptabilise = comptabilise or (type in ("KDP","KDP_F") and etat1 == "D" and etat2 == "K")
    if comptabilise:
        debug("comptabilise")
        database.usages.insert({"date":datetime.datetime.now(),"psav":psav,"classe":classe})
        
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
            args = parserPut.parse_args()
            allset = {}
            args = parserPut.parse_args()
            if not controleEtat(args["etat"]):
                return abort(400,message = "etat non valide " + args["etat"])
            if not controleCoherence("typ",old["etat"],args["etat"]):
                return abort(400,message = "erreur coherence " + old["etat"] + "=>" + args["etat"])
            args["datmaj"] = datetime.datetime.now()
            modif = {"$set":args}
            debug(str(modif))
            debug (collection.update({"_id":imei,"psav":psav},modif))
        if request.args.get("maintenance") == None and old["etat"] != args["etat"]:
            changement(psav,old["type"],old["reappro"],old["etat"],args["etat"])
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
            item["uri"] = api.url_for(Imei, psav=psav, imei=item["imei"], _external=True)
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
            debug (args)
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

NOM_COLL_STOCK_DISPO_AGGREGE = "stock_dispo_aggrege_"
NOM_COLL_STOCK_ROULANT_AGGREGE = "stock_roulant_aggrege_"
NOM_COLL_ACTIVITE_AGGREGE = "activite_aggrege_"

class Reappro(Resource):
    def post(self):
        PO = 40
        TCG = 70
        SEUIL = 0
        resultat = {}
        dateDepart = datetime.date.today() - datetime.timedelta(days=PO)
        theDateDepart = datetime.datetime.combine(dateDepart, datetime.datetime.min.time())
        print (theDateDepart)
        random.seed()
        numReappro = random.randint(0,1000000)
        col_activite_aggrege = NOM_COLL_ACTIVITE_AGGREGE + str(numReappro)
        col_stock_roulant_aggrege = NOM_COLL_STOCK_ROULANT_AGGREGE + str(numReappro)
        col_stock_dispo_aggrege = NOM_COLL_STOCK_DISPO_AGGREGE + str(numReappro)
        database.usages.aggregate([{"$match":{"date":{"$gt":theDateDepart}}},
            {"$group":{"_id":OrderedDict([("psav","$psav"),("classe","$classe")]),"count":{"$sum":1}}},
            {"$out":col_activite_aggrege}])
        database.stock.aggregate([{"$match":{"etat":{"$in":['D','K']}}},
            {"$group":{"_id":OrderedDict([("psav","$psav"),("classe","$reappro")]),"count":{"$sum":1}}},
            {"$out":col_stock_roulant_aggrege}])
        database.stock.aggregate([{"$match":{"etat":{"$in":['D']}}},
            {"$group":{"_id":OrderedDict([("psav","$psav"),("classe","$reappro")]),"count":{"$sum":1}}},
            {"$out":col_stock_dispo_aggrege}])
        classes_reappro = database.gencods.distinct("classe.libelle")
        classes_reappro = classes_reappro + database.gencods.distinct("famille.libelle")
        for psav in collection.distinct("psav"):
            resultat[psav] = {}
            for classe_reappro in classes_reappro:
                tcg = TCG
                try:
                    tcg = references["reappro"][classe_reappro]["TCG"]
                except KeyError:
                    pass
                seuil = SEUIL
                try:
                    seuil = references["reappro"][classe_reappro]["SEUIL"]
                except KeyError:
                    pass
                searchTerm = OrderedDict([("psav",psav),("classe",classe_reappro)])
                activite = database[col_activite_aggrege].find_one({"_id":searchTerm})
                if activite == None:
                    activite = {"count":0}
                stockDispo = database[col_stock_dispo_aggrege].find_one({"_id":searchTerm})
                if stockDispo == None:
                    stockDispo = {"count":0}
                stockRoulant = database[col_stock_roulant_aggrege].find_one({"_id":searchTerm})
                if stockRoulant == None:
                    stockRoulant = {"count":0}
                besoin  = round(activite["count"] * tcg / 100) - stockRoulant["count"]
                if besoin < 0:
                    besoin = 0
                if besoin + stockDispo["count"] < seuil:
                    besoin = seuil - stockDispo["count"]
                if besoin != 0:
                    resultat[psav][classe_reappro] = besoin
            if resultat[psav] == {}:
                del resultat[psav]
        database[col_activite_aggrege].drop()
        database[col_stock_roulant_aggrege].drop()
        database[col_stock_dispo_aggrege].drop()
        return resultat,200

BASE_URL = '/stock'
BASE_URL_PSAV = BASE_URL + '/<psav>'
app = Flask(__name__)
api = Api(app, default_mediatype="application/json")
api.add_resource(Imei,BASE_URL_PSAV + '/imei/<imei>')
api.add_resource(ImeiCreation,BASE_URL_PSAV + '/imei')
api.add_resource(ImeiList,BASE_URL_PSAV)
api.add_resource(Transfert,BASE_URL_PSAV + '/transfert/<psavcible>')
api.add_resource(Reappro,BASE_URL + '/reappro')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)