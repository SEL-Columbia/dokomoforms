var React = require('react');
var Card = require('./baseComponents/Card.js');

/*
 * Splash page component
 * Renders the appropiate card for the main page
 *
 * props:
 *     @language: current survey language
 *     @surveyID: current survey id
 */
module.exports = React.createClass({
    getInitialState: function() {
        return { 
        }
    },

    render: function() {
        return (
                <Card messages={[this.props.surveyID, 
                    [<b>love</b>], "toast"]} type={"message-primary"}/>
               )
    }
});
