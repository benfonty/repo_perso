import pymongo


connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.stock


def controleGencod( gencod ):
    return database.gencods.find_one({"_id":gencod})


upd = 0
dele = 0
for imei in database.stock.find({"type":{"$exists":0}}):
    gencod = None
    if "gencod" in imei:
        gencod = controleGencod(imei["gencod"])
    if (upd + dele) % 10000 == 0:
        print(upd,"update",dele,"delete")
    data = {}
    if gencod == None:
        dele += 1
        database.stock.remove({"_id":imei["_id"]})
    else:
        upd += 1
        data["type"] = gencod["type"]["code"]
        if data["type"] in ("SIM","SIM_F"):
            data["reappro"] = gencod["famille"]["libelle"]
        else:
            data["reappro"] = gencod["classe"]["libelle"]
        database.stock.update({"_id":imei["_id"]},{"$set":data})
