use stock
db.stock.ensureIndex({psav:1})
if (db.system.namespaces.find( { name: 'stock.usages' } )) {
    db.runCommand({"convertToCapped": "usages", size: 150000000});
}
else {
    db.createCollection( "usages", { capped: true, size: 150000000 } );
}
