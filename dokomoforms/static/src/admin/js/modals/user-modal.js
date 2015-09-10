var $ = require('jquery'),
    // Users = require('./models').Users,
    User = require('../models').User,
    tpl = require('../../templates/user-modal.tpl');

var UserModal = function(user_id) {
    this.user = new User();
    // TODO: this could come from the collection, it's obviously already been fetched.
    if (user_id) {
        // We are editing...
        this.user.set('id', user_id);
        this.user.fetch()
            .done(this.open.bind(this));
    } else {
        // we are adding, no uuid
        this.open();
    }
};


UserModal.prototype.open = function() {
    console.log('open', this.user.toJSON());
    // console.log(this.user.toJSON());
    this.$modal = $(tpl(this.user.toJSON())).modal();
    this.$modal.on('shown.bs.modal', function() {
        console.log(this);
        $(this).first('input').focus();
    });

    this.$modal.find('.btn-save-user').click(this.saveUser.bind(this));
};

UserModal.prototype.saveUser = function() {
    console.log('saveUser', this.user.toJSON());

    this.user.set({
        name: $('#name').val(),
        email: [$('#email').val()],
        role: $('#role').val(),
        preferences: {
            default_language: $('#default-lang').val()
        }
    });

    this.user.save()
        .done(this.close.bind(this));
};


UserModal.prototype.close = function() {
    this.$modal.modal('hide');
};


module.exports = UserModal;
