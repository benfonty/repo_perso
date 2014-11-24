import csv
import pymongo

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock

with open('gencods.csv','r') as f:
    gencod = {}
    csvfile = csv.DictReader(f, delimiter=';')
    for ligne in csvfile:
        data = {}
        data["_id"] = ligne["GENCOD"]
        data["classe"] = {"code":ligne["CODCLA"],"libelle":ligne["LIBCLA"]}
        data["famille"] = {"code":ligne["CODFAM"],"libelle":ligne["LIBFAM"]}
        data["type"] = {"code":ligne["CODTYPPDT"],"libelle":ligne["LIBTYPPDT"]}
        database.gencods.insert(data)
       
