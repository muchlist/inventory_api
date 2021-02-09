# inventory_api
Restfull Api untuk aplikasi inventaris barang-barang IT

update for pending_history branch :

    db.histories.updateMany({"is_complete": true}, {$set: {"complete_status": NumberInt(2)}})
    db.histories.updateMany({"is_complete": false}, {$set: {"complete_status": NumberInt(0)}})   

