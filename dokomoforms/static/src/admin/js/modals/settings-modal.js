var $ = require('jquery'),
    moment = require('moment'),
    ps = require('../../../common/js/pubsub'),
    utils = require('../utils'),
    // Users = require('./models').Users,
    _t = require('../lang'),
    User = require('../models').User,
    tpl = require('../../templates/settings-modal.tpl');

var SettingsModal = function(user_id) {
    console.log('SettingsModal', user_id);
    var user = new User(),
        $modal;
    // TODO: this could come from the collection, it's obviously already been fetched.
    if (user_id) {
        // We are editing...
        user.set('id', user_id);
        user.fetch()
            .done(open);
    }

    function open() {
        console.log('open', user.toJSON());
        var dataForDisplay = $.extend(user.toJSON(), {_t: _t});
        console.log('dataForDisplay', dataForDisplay);
        $modal = $(tpl(dataForDisplay)).modal();
        $modal.on('shown.bs.modal', function() {
            $modal.first('input').focus();
            $modal.find('.btn-save-user').click(saveSettings);
            $modal.find('.btn-api-key').click(refreshApiKey);
            utils.initTooltips('.modal');
        });

    }

    function close() {
        $modal.on('hidden.bs.modal', function() {
            $modal.remove();

        });
        $modal.modal('hide');
    }

    function saveSettings() {
        console.log('saveSettings', user.toJSON());

        var changeset = {
            name: $modal.find('#user-name').val(),
            emails: [$modal.find('#user-email').val()],
            role: $modal.find('#user-role').val(),
            preferences: {
                default_language: $modal.find('#user-default-lang').val()
            }
        };

        if (changeset.role === 'enumerator') {
            changeset.allowed_surveys = $modal.find('#user-surveys').val() || [];
        }

        user.set(changeset);

        user.save()
            .done(function() {
                close();
                ps.publish('settings:saved');
            })
            .fail(function() {
                close();
                ps.publish('settings:save-error');
            });
    }

    function refreshApiKey() {
        console.log('refreshApiKey');
        $.getJSON('/api/v0/users/generate-api-token', function(resp) {
            console.log(resp);
            $modal.find('#user-api-token').val(resp.token);
            var expires = moment(resp.expires_on);
            $modal.find('.token-expiration-text').text('Token will expire on ' + expires.format('MMM D, YYYY') + '.');
            $modal.find('.alert-token-expiration').removeClass('hide');
        });
    }

    return {
        open: open,
        close: close
    };

};


module.exports = SettingsModal;
