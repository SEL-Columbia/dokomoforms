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
 */
module.exports = React.createClass({
    render: function() {
        var self = this;
        return (
            <div className="title_menu">
                <div className="title_menu_option menu_restart"
                    onClick={function() {
                        localStorage.clear();
                        location.reload();
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

