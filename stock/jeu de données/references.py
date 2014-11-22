import csv
import pymongo

REFERENCES = ["classes","familles","types","etats"]

references = {}

for reference in REFERENCES:
    with open(reference + '.csv','r') as f:
        references[reference] = {}
        csvfile = csv.DictReader(f, delimiter=';')
        for ligne in csvfile:
            code = ligne["code"]
            del ligne["code"]
            references[reference][code] = ligne

#print (references)
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock
database.references.drop()
database.references.insert(references)