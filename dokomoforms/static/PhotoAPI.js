module.exports = {
    /*
     * Get photo with uuid, id from pouchDB as data URI
     */
    getPhoto: function(db, id, callback) {
        db.getAttachment(id, 'photo').then(function(photo) {
            callback(null, URL.createObjectURL(photo));
        }).catch(function(err) {
            callback(err);
        });
    },

    /*
     * Get photo with uuid, id from pouchDB as base64 string
     */
    getBase64: function(db, id, callback) {
        db.getAttachment(id, 'photo').then(function(photoBlob) {
            var reader = new window.FileReader();
            reader.readAsDataURL(photoBlob);
            reader.onloadend = function() {
                var photoURI = reader.result;
                var photo64 = photoURI.substring(photoURI.indexOf(',')+1);
                callback(null, photo64);
            };
        }).catch(function(err) {
            callback(err);
        });
    },

    /*
     * Get photo with uuid, id from pouchDB as blob
     */
    getBlob: function(db, id, callback) {
        db.getAttachment(id, 'photo').then(function(photo) {
            callback(null, photo);
        }).catch(function(err) {
            callback(err);
        });
    },

    /*
     * Remove photo with uuid, id from pouchDB
     */
    removePhoto: function(db, photoID, callback) {
        db.get(photoID).then(function (photoDoc) {
            db.removeAttachment(photoID, 'photo', photoDoc._rev)
                .then(function(result) {
                    db.remove(photoID, result.rev);
                    callback(null, result);
                }).catch(function(err) {
                    callback(err);
                });
        });
    },

    /*
     * Add photo with given uuid and base64 URI to pouchDB
     * TODO set up callback
     */
    addPhoto: function(db, photoID, photo, callback) {
        var photo64 = photo.substring(photo.indexOf(',')+1);
        console.log(photo);
        console.log(photoID);
        db.put({
            '_id': photoID,
            '_attachments': {
                'photo': {
                    'content_type': 'image/png',
                    'data': photo64
                }
            }
        });

    }

};

