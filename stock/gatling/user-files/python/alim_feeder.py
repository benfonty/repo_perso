import pymongo
import csv


connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock
stocks = database.stock

def IsPsavPersistent(psav):
    return psav[-1] not in ('8','9')

with open("../data/imeiPsav.csv","w", newline='') as fileImeiPsav:
    with open("../data/imeiPsavPersistent.csv","w",newline='') as fileImeiPsavPersistent:
        writer = csv.DictWriter(fileImeiPsav,["psav","imei"], delimiter=";")
        writerPersistent = csv.DictWriter(fileImeiPsavPersistent,["psav","imei"], delimiter=";")
        writer.writeheader()
        writerPersistent.writeheader()
        for stock in stocks.find({},{"psav":1}):
            stock["imei"] = stock["_id"]
            del stock["_id"]
            writer.writerow(stock)
            if IsPsavPersistent(stock["psav"]):
                writerPersistent.writerow(stock)
