var Backbone = require('backbone');

var Survey = Backbone.Model.extend({

});

var Surveys = Backbone.Collection.extend({
    url: '/api/v0/surveys',
    model: Survey
});


module.exports = {
    Survey: Survey,
    Surveys: new Surveys()
};
