# -*- coding: utf8 -*-

import pymongo
import copy
from pymongo import MongoClient
from bson.son import SON
import datetime
import csv
import sys
feature_codes = {}

# connect to database
connection = MongoClient('localhost', 27017)

db = connection.villes

col = db.feature_codes

col.drop()

with open('featureCodes_en.txt','r') as file:
    reader = csv.DictReader(file,["code","text"],delimiter = '\t' , quotechar= '\x07')
    for rows in reader:
        
        data = {
            "_id":rows["code"].split(".")[1],
            "class":rows["code"].split(".")[0],
            "text":rows["text"]
        }
        col.insert(data)