var $ = require('jquery'),
    Backbone = require('backbone');

var User = Backbone.Model.extend({
    urlRoot: '/api/v0/users'
});

var Users = Backbone.Collection.extend({
    url: '/api/v0/users',
    model: User
});

module.exports = {
    User: User,
    Users: new Users()
};
