var Backbone = require('backbone');

var User = Backbone.Model.extend({

});

var Users = Backbone.Collection.extend({
    url: '/api/v0/users',
    model: User
});

module.exports = {
    User: User,
    Users: new Users()
};
