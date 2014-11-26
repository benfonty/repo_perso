import csv
import json

i = 0
with open('../../../usages.csv','r') as f:
    with open ('../../../usages.json','w') as jfjson:
        csvfile = csv.DictReader(f, delimiter=';')
        for ligne in csvfile:
            i+= 1
            if (i % 10000) == 0:
                print(i)
            ligne["date"] = {"$date":ligne["date"]}
            json.dump(ligne,jfjson)
            jfjson.write("\n")
            
       
