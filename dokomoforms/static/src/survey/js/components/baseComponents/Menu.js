var React = require('react'),
    createReactClass = require('create-react-class'),
    screenfull = require('screenfull'),
    uuid = require('uuid'),
    PhotoAPI = require('../../api/PhotoAPI.js'),
    ps = require('../../../../common/js/pubsub'),
    auth = require('../../services/auth');

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
module.exports = createReactClass({

    componentWillMount: function() {
        console.log('=======> componentWillMount');
        // this.survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
    },

    wipeActive: function() {
        var self = this;
        // Confirm their intent
        var nuke = confirm('Warning: Active survey and photos will be lost.');
        if (!nuke)
            return;
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');

        // we're storing the start_time on the survey, which we don't want to include
        // in the iteration here...
        delete survey.start_time;

        var questionIDs = Object.keys(survey);
        questionIDs.forEach(function(questionID) {
            var responses = survey[questionID] || [];

            responses.forEach(function(response) {
                //XXX response object does not contain type_constraint, would need to pass in question nodes
                //if (response.type_constraint === 'photo') {
                //XXX hack for now
                if (response.response.length === 36) {
                    PhotoAPI.removePhoto(self.props.db, response.response, function(err, result) {
                        if (err) {
                            //XXX should fail often as it tries to clear every response
                            console.log('Couldnt remove from db:', err);
                            return;
                        }
                        console.log('Removed:', result);
                    });
                }
            });
        });

        // Wipe active survey
        localStorage[this.props.surveyID] = JSON.stringify({});
        // Wipe location info
        localStorage['location'] = JSON.stringify({});
        window.location.reload();
    },


    wipeAll: function() {
        var self = this;
        // Confirm their intent
        var nuke = confirm('Warning: All stored surveys and photos will be lost.');
        if (!nuke)
            return;

        localStorage.clear();
        self.props.db.destroy().then(function() {
            window.location.reload();
        });
    },

    toggleFullscreen: function() {
        console.log('screenfull', screenfull.enabled);
        if (screenfull.enabled) {
            screenfull.toggle();
        }
    },

    selectLanguage: function(e) {
        console.log('selectLanguage', e.target.value);
        ps.publish('settings:language_changed', e.target.value);
    },

    logOut: function() {
        console.log('log out');
        auth.logOut().done(function() {
            console.log('logged out.');
            var curUrl = window.location.href;
            window.location.href = curUrl + '?logged-out=' + uuid.v4();
        });
    },

    logIn: function() {
        console.log('log in');
        auth.logIn();
    },

    reloadFacilities: function() {
        console.log('reloadFacilities');
        ps.publish('revisit:reload_facilities');
    },

    render: function() {
        var self = this;
        var langOpts,
            langMenuItem,
            logOut,
            reloadFacilities;

        console.log('render...', self.props.survey);

        // XXX - maybe we don't display the select box if there's only one lang available?
        // if (self.props.survey.languages && self.props.survey.languages.length > 1) {
        if (self.props.survey.languages) {
            langOpts = self.props.survey.languages.map(function(lang) {
                var selected = (self.props.language === lang);
                return (
                    <option value={lang} selected={selected}>{lang}</option>
                );
            });
        }

        if (langOpts) {
            langMenuItem = (
                <div className='title_menu_option menu_language'>
                    Language:
                    <select className='language_select' onChange={self.selectLanguage}>
                        {langOpts}
                    </select>
                </div>
            );
        }

        if (navigator.onLine) {
            if (this.props.hasFacilities) {
                reloadFacilities = (
                    <div className='title_menu_option menu_facilities' onClick={self.reloadFacilities} >
                        Reload Facilities
                    </div>
                );
            }
            if (this.props.loggedIn) {
                logOut = (
                    <div className='title_menu_option menu_logout' onClick={self.logOut} >
                        Log Out
                    </div>
                );
            } else {
                logOut = (
                    <div className='title_menu_option menu_login' onClick={self.logIn} >
                        Log In
                    </div>
                );
            }
        }

        return (
            <div className='title_menu'>
                <div className='title_menu_option menu_fullscreen' onClick={self.toggleFullscreen} >
                    Toggle fullscreen
                </div>

                {langMenuItem}

                <div className='title_menu_option menu_restart' onClick={self.wipeActive} >
                    Cancel survey
                </div>
                <div className='title_menu_option menu_clear' onClick={self.wipeAll} >
                    Clear all saved surveys
                </div>

                {reloadFacilities}

                {logOut}

            </div>
       );
    }
});
