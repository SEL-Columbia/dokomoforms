var $ = require('jquery'),
    // Users = require('./models').Users,
    User = require('../models').User,
    tpl = require('../../templates/user-modal.tpl');

var UserModal = function(user_id) {
    // TODO: this could come from the collection, it's obviously already been fetched.
    if (user_id) {
        // We are editing...
        this.user = new User({id: user_id});
        this.user.fetch()
            .done(this.open);
    } else {
        // we are adding, no uuid
        this.user = new User();
        this.open();
    }
};


UserModal.prototype.open = function() {
    this.$modal = $(tpl(this.user)).modal();
};


UserModal.prototype.close = function() {
    this.$modal.hide();
};


module.exports = UserModal;
