var React = require('react'); 

module.exports = React.createClass({
    render: function() {
        return (
            <div className="title_menu">
                <div className="title_menu_option menu_restart">
                    Cancel survey
                </div>
                <div className="title_menu_option menu_save">
                    Save current state and exit
                </div>
                <div className="title_menu_option menu_clear">
                    Clear all saved surveys
                </div>
            </div>
       )
    }
});

