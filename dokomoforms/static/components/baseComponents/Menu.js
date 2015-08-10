var React = require('react'); 
var PhotoAPI = require('../../PhotoAPI.js');

/*
 * Header Menu component
 *
 * XXX In works, must sort out way to properly clear active survey 
 * (Could have active survey data that references photos in pouchdb that would 
 * be left orphaned if not submitted).
 *
 * @db: active pouch db
 * @surveyID: active surveyID
 */
module.exports = React.createClass({

    wipeActive: function() {
        var self = this;
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var questionIDs = Object.keys(survey);
        console.log('questionIDs', questionIDs);
        questionIDs.forEach(function(questionID) {
            var responses = survey[questionID] || [];
            console.log('responses', responses);
            responses.forEach(function(response) {
                console.log('response', response);
                //XXX response object does not contain type_constraint, would need to pass in question nodes
                //if (response.type_constraint === 'photo') {
                //XXX hack for now
                if (response.response.length === 36) {
                    PhotoAPI.removePhoto(self.props.db, response.response, function(err, result) {
                        if (err) {
                            //XXX should fail often as it tries to clear every response
                            console.log("Couldnt remove from db:", err);
                            return;
                        }

                        console.log("Removed:", result);
                    });
                }
            });
        });

        // Wipe active survey
        localStorage[this.props.surveyID] = JSON.stringify({});
        // Wipe location info
        localStorage['location'] = JSON.stringify({});
        location.reload();
    },

    render: function() {
        var self = this;
        return (
            <div className="title_menu">
                <div className="title_menu_option menu_restart"
                    onClick={function() {
                        self.wipeActive();
                    }}
                >
                    Cancel survey
                </div>
                <div className="title_menu_option menu_clear"
                    onClick={function() {
                        localStorage.clear();
                        self.props.db.destroy().then(function() {
                            location.reload();
                        });
                    }}
                >
                    Clear all saved surveys
                </div>
            </div>
       )
    }
});
