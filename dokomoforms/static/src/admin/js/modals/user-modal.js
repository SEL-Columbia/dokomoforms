var $ = require('jquery'),
    ps = require('../pubsub'),
    utils = require('../utils'),
    // Users = require('./models').Users,
    _t = require('../lang'),
    User = require('../models').User,
    tpl = require('../../templates/user-modal.tpl');

var UserModal = function(user_id, surveys) {
    console.log('UserModal', user_id, surveys.toJSON());
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
        var dataForDisplay = $.extend(user.toJSON(), {all_surveys: surveys.toJSON(), _t: _t});
        console.log('dataForDisplay', dataForDisplay);
        $modal = $(tpl(dataForDisplay)).modal();
        $modal.on('shown.bs.modal', function() {
            $modal.first('input').focus();
            $modal.find('.btn-save-user').click(saveUser);
            $modal.find('.btn-delete-user').click(deleteUser);
            utils.initTooltips('.modal');
        });

    }

    function close() {
        $modal.on('hidden.bs.modal', function() {
            console.log('closed?');
            $modal.remove();

        });
        $modal.modal('hide');
    }

    function saveUser() {
        console.log('saveUser', user.toJSON());

        var changeset = {
            name: $modal.find('#user-name').val(),
            emails: [$modal.find('#user-email').val()],
            role: $modal.find('#user-role').val(),
            preferences: {
                default_language: $modal.find('#user-default-lang').val()
            }
        };
        var surveys = $modal.find('#user-surveys').val() || [];
        console.log('surveys', surveys);
        if (changeset.role === 'enumerator') {
            changeset.allowed_surveys = surveys;
        } else if (changeset.role === 'administrator') {
            changeset.surveys = surveys;
        }

        user.set(changeset);

        user.save()
            .done(function() {
                close();
                ps.publish('user:saved');
            })
            .fail(function() {
                ps.publish('user:save-error');
            });
    }

    function deleteUser() {
        console.log('saveUser', user.toJSON());
        if(!confirm('Are you certain you want to remove this user from the system?')) {
            return;
        }
        user.destroy()
            .done(function() {
                close();
                ps.publish('user:deleted');
            })
            .fail(function() {
                ps.publish('user:delete-error');
            });
    }

    return {
        open: open,
        close: close
    };

};


module.exports = UserModal;
