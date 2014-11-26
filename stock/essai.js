use stock
db.usages_aggreges.drop()
db.usages.aggregate([{
    $match: {
        date:{$gt:new Date(2014,8,26)}
    }
},{
    $group: {
        _id:{psav:"$psav",classe:"$classe"},
        count:{$sum:1}
    }
},{
    $project:{
        _id:0,
        psav:"$_id.psav",
        besoin:{classe:"$_id.classe",count:"$count"}
    }
},{
    $group: {
        _id:"$psav",
        besoin:{$addToSet:"$besoin"}
    }
},{
    $project: {
        psav:"$_id",
        _id:0,
        besoin:1
    }
},{
    $out:"usages_aggreges"
}])