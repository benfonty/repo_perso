# -*- coding: utf8 -*-
import csv
import re
import datetime
import pymongo
import sys
import glob

i = 0

def nullif(s):
    if s != None:
        s = s.strip()
    if s == None or s == "":
        return None
    return s

def nullifint(s):
    if s != None:
        s = s.strip()
    if s == None or s == "":
        return None
    return int(s)

def tableau(s):
    if s == None:
        return None
    resultat = s.split(',')
    return [n.strip() for n in resultat]

def to_date(s):
    if s == None:
        return None
    resultat = re.match(r'(\d\d\d\d)-(\d\d)-(\d\d)',s)
    assert resultat != None
    return datetime.datetime(int(resultat.group(1)) , int(resultat.group(2)),int(resultat.group(3)) )

assert nullif(None) == None
assert nullif("") == None
assert nullif ("toto") == "toto"

assert tableau(None) == None
assert tableau("12") == ["12"]
assert tableau ("12,13") == ["12","13"]

assert to_date("2014-12-13") == datetime.datetime(2014,12,13)

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.villes
villes = database.villes

#villes.drop()

files = glob.glob("allcountries.csv")


for onefile in files:
    i = 0
    try:
        with open(onefile,'r') as file:
            reader = csv.reader(file,delimiter = '\t' , quotechar= '\x07')
            for row in reader:
                element = {}
                element["_id"] = nullifint(row[0])
                if nullif(row[1]) != None:
                    element["name"] = nullif(row[1])
                if nullif(row[2]) != None:
                    element["asciiname"] = nullif(row[2])
                if tableau(nullif(row[3])) != None:
                    element["altername_names"] = tableau(nullif(row[3]))
                
                lon = nullif(row[5])
                lat = nullif(row[4])
                if lon != None and lat != None:
                    element["location"] = []
                    element["location"].append(float(lon))
                    element["location"].append(float(lat))
                if nullif(row[6]) != None:
                    element["feature_class"] = nullif(row[6])
                if nullif(row[7]) != None:
                    element["feature_code"] = nullif(row[7])
                if nullif(row[8]) != None:
                    element["country"] = nullif(row[8])
                if tableau(nullif(row[9])) != None:
                    element["alt_country"] = tableau(nullif(row[9]))
                if nullifint(row[14]) != None:
                    element["population"] = nullifint(row[14])
                if nullifint(row[15]) != None:
                    element["elevation"] = nullifint(row[15])
                if nullif(row[17]) != None:
                    element["timezone"] = nullif(row[17])
                if to_date(nullif(row[18])) != None:
                    element["modification_date"] = to_date(nullif(row[18]))
                
                villes.save(element)
                  
                i += 1
                if i % 1000 == 0:
                    print onefile + " " + str(i) + "\n"
    except:
        print "problem with file " + onefile + " " + str(i)