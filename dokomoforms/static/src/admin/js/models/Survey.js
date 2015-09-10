var Backbone = require('backbone');

var Survey = Backbone.Model.extend({

});

var Surveys = Backbone.Collection.extend({
    url: '/api/v0/surveys',
    model: Survey,
    parse: function(response) {
        return response.surveys;
    }
});


module.exports = {
    Survey: Survey,
    Surveys: Surveys
};
