import csv
import json

CHAMPS_OBLIGATOIRES = ("imei","gencod","psav","etat","type","classe","famille")

with open('data.csv','r') as fcsv:
    with open ('data.json','w') as fjson:
        with open ('data.err.json','w') as fjsonerr:
            datas = csv.DictReader(fcsv,delimiter=';')
            for data in datas:
                data["_id"] = data["imei"]
                del data["imei"]
                valide = True
                newdata = {}
                for key, value in data.items():
                    if value == "":
                        if key in CHAMPS_OBLIGATOIRES:
                            valide = False
                    else:
                        newdata[key] = value
                        if key == "datmaj":
                            newdata[key] = {"$date":value}
                if valide:
                    json.dump(newdata,fjson)
                    fjson.write("\n")
                else:
                    json.dump(data,fjsonerr)
                    fjsonerr.write("\n")
