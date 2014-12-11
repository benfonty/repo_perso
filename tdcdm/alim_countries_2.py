# -*- coding: utf8 -*-

import pymongo
import copy
from pymongo import MongoClient
from bson.son import SON
import datetime
import csv
import sys



LIMIT = 10000000

COLLECTION = "villes"


# connect to database
connection = MongoClient('localhost', 27017)

db = connection.villes

col = db[COLLECTION]

condition = {}

condition["country.name"] = "Inconnu"

pays = {}

pays["EH"] = {
    "code":"EH",
    "name":"Sahara occidental"
}

pays["MF"] = { # à coriger
    "code":"MF",
    "name":"Saint-Martin"
}

pays["PS"] = {
    "code":"PS",
    "name":"Palestine"
}

pays["SS"] = {
    "code":"SS",
    "name":"Soudan du Sud"
}

pays["SX"] = { # à coriger
    "code":"SX",
    "name":"Saint-Martin"
}

pays["XK"] = {
    "code":"XK",
    "name":"Kosovo"
}

cursor = col.find(condition,None,0,LIMIT)

nbelement = 0
totaltime = 0
maxtime = datetime.timedelta.min
mintime = datetime.timedelta.max



for town in cursor:
    try:
        nbelement +=1
        if nbelement % 10000 == 0:
            print
            print
            print str(nbelement) + " traités"
            print "temps total " + str(totaltime)
            print "temps moyen " + str(totaltime/nbelement)
            print "temps max " + str(maxtime)
            print "temps min " + str(mintime)
        depart = datetime.datetime.now()
        
        if town["country"]["code"] in pays:
            town["country"] = pays[town["country"]["code"]]
        else:
            town["country"] = {
                "code":town["country"],
                "name":"Inconnu"
            }
            print town["country"]["code"] + " inconnu"
        col.update({"_id":town["_id"]},town)
        arrivee = datetime.datetime.now()
        duree = arrivee - depart
        if totaltime == 0:
            totaltime = duree
        else:
            totaltime += duree
        if duree > maxtime:
            maxtime = duree
        if duree < mintime:        
            mintime = duree
    except Exception,e:
        print town
        raise e

print "OK"
print str(nbelement) + " traités"
if nbelement > 0:
    print "temps total " + str(totaltime)
    print "temps moyen " + str(totaltime/nbelement)
    print "temps max " + str(maxtime)
    print "temps min " + str(mintime)