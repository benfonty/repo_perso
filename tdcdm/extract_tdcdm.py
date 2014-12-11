# -*- coding: utf8 -*-

import pymongo
import copy
from pymongo import MongoClient
from bson.son import SON
import datetime
import csv
import sys
import json

COLLECTION="towns"
COUNTRY_FILE = "countries.json"

countries = []
# connect to database
connection = MongoClient('localhost', 27017)
db = connection.villes
col = db[COLLECTION]

def load_countries():
    c = col.distinct("country.name")
    c.sort()
    with open(COUNTRY_FILE,"w") as file:
        json.dump(c,file)
    return c

print("lecture du fichier des pays")
try:
    with open(COUNTRY_FILE,"r") as file:
        countries = json.load(file)
except Exception as e:
    pass

if len(countries) == 0:
    print ("Fichier de pays non trouvé : chargement")
    countries = load_countries()
taille = len(countries)
print(len(countries),"pays trouvés")
i=0
# db.essai.ensureIndex({"country.name":1,"neighbour.distance":-1})

resultats = []
for country in countries:
    i += 1
   
    #print("en traitement :",country,"(",i,"/",taille,")") 
  
    cursor = col.find({"country.name":country}).sort("neighbour.distance",-1).limit(5)
    for line in cursor:
        resultats.append( {
            "id":line["_id"],
            "nom":line["name"],
            "coord":str(line["location"]),
            "pays":line["country"]["name"],
            "distant de id":line["neighbour"]["town"]["_id"],
            "distant de nom":line["neighbour"]["town"]["name"],
            "distant de pays":line["neighbour"]["town"]["country"]["name"],
            "distant de km":float(line["neighbour"]["distance"]),
            "distant de coord":str(line["neighbour"]["town"]["location"])
            })
with open("tdctm.csv","w", newline='') as file:
    writer = csv.DictWriter(file,["pays","nom","coord","id","distant de nom","distant de coord","distant de id","distant de pays","distant de km"], delimiter=";")
    writer.writeheader()
    for res in resultats:
        writer.writerow(res)

