import pymongo
import csv


connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock
stocks = database.stock

psav = []

def IsPsavPersistent(psav):
    return psav[-1] not in ('8','9')

with open("../data/imeiPsav.csv","w", newline='') as fileImeiPsav, \
    open("../data/imeiPsavPersistent.csv","w",newline='') as fileImeiPsavPersistent, \
    open("../data/psav.csv","w", newline = '') as filePsav, \
    open("../data/psavTransfert.csv", "w", newline = '') as filePsavTransfert:
    writer = csv.DictWriter(fileImeiPsav,["psav","imei"], delimiter=",")
    writerPersistent = csv.DictWriter(fileImeiPsavPersistent,["psav","imei"], delimiter=",")
    writerPsav = csv.DictWriter(filePsav,["psav"], delimiter = ',')
    writerPsavTransfert = csv.DictWriter(filePsavTransfert,["psavTransfert"], delimiter = ',')
    writer.writeheader()
    writerPersistent.writeheader()
    writerPsav.writeheader()
    writerPsavTransfert.writeheader()
    for stock in stocks.find({},{"psav":1}):
        stock["imei"] = stock["_id"]
        del stock["_id"]
        writer.writerow(stock)
        if stock["psav"] not in psav:
            writerPsav.writerow({"psav":stock["psav"]})
        if IsPsavPersistent(stock["psav"]):
            writerPersistent.writerow(stock)
        elif stock["psav"] not in psav:
            writerPsavTransfert.writerow({"psavTransfert":stock["psav"]})
        psav.append(stock["psav"])
