var $ = require('jquery'),
    ps = require('../pubsub'),
    // Users = require('./models').Users,
    User = require('../models').User,
    tpl = require('../../templates/user-modal.tpl');

var UserModal = function(user_id) {
    console.log(user_id);
    var user = new User(),
        $modal;
    // TODO: this could come from the collection, it's obviously already been fetched.
    if (user_id) {
        // We are editing...
        user.set('id', user_id);
        user.fetch()
            .done(open);
    } else {
        // we are adding, no uuid
        open();
    }

    function open() {
        console.log('open', user.toJSON());
        $modal = $(tpl(user.toJSON())).modal();
        $modal.on('shown.bs.modal', function() {
            $modal.first('input').focus();
        });

        $modal.find('.btn-save-user').click(saveUser);
    }

    function close() {
        $modal.modal('hide');
        ps.publish('user:saved');
    }

    function saveUser() {
        console.log('saveUser', user.toJSON());

        user.set({
            name: $('#user-name').val(),
            emails: [$('#user-email').val()],
            role: $('#user-role').val(),
            preferences: {
                default_language: $('#user-default-lang').val()
            }
        });

        user.save()
            .done(close);
    }

    return {
        open: open,
        close: close
    };

};


module.exports = UserModal;
