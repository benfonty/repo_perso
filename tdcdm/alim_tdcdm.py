# -*- coding: utf8 -*-

import pymongo
import copy
from pymongo import MongoClient
from bson.son import SON
import datetime


CONDITION = {
    #"feature.class.code":"P"
}

LIMIT = 10000000

COLLECTION = "towns"

COMMAND = [
    ("geoNear",COLLECTION),
    ("near", {
        "type":"Point",
        "coordinates": []
        }
    ),
    ("limit",1),
    ("minDistance",1000),
    ("spherical",True)
]


# connect to database
connection = MongoClient('localhost', 27017)
db = connection.villes
col = db[COLLECTION]
condition = copy.deepcopy(CONDITION)
condition["neighbour"] = {
    "$exists":False
}

cursor = col.find(condition,None,0,LIMIT)
nbelement = 0
totaltime = 0
maxtime = datetime.timedelta.min
mintime = datetime.timedelta.max
depart = datetime.datetime.now()
for town in cursor:
    nbelement +=1
    
    
    COMMAND[1][1]["coordinates"] = town["location"]
    result = db.command(SON(COMMAND))
    if result["ok"] != 1:
        raise "Erreur"  + " " + str(result)
    neighbour = copy.deepcopy(result["results"][0])
    neighbour["distance"] = neighbour["dis"]
    del neighbour["dis"]
    neighbour["town"] = neighbour["obj"]
    del neighbour["obj"]
    if "neighbour" in neighbour["town"]:
        del neighbour["town"]["neighbour"]
    col.update({"_id":town["_id"]},{"$set":{"neighbour":neighbour}})
    arrivee = datetime.datetime.now()
    duree = arrivee - depart
    depart = datetime.datetime.now()
    if totaltime == 0:
        totaltime = duree
    else:
        totaltime += duree
    if duree > maxtime:
        maxtime = duree
    if duree < mintime:        
        mintime = duree
    if nbelement % 10000 == 0:
        print
        print
        print str(nbelement) + " traités"
        print "temps total " + str(totaltime)
        print "temps moyen " + str(totaltime/nbelement)
        print "temps max " + str(maxtime)
        print "temps min " + str(mintime)

print "OK"
print str(nbelement) + " traités"
if nbelement > 0:
    print "temps total " + str(totaltime)
    print "temps moyen " + str(totaltime/nbelement)
    print "temps max " + str(maxtime)
    print "temps min " + str(mintime)